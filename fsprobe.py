"""
mnheme/fsprobe.py
================
Rilevamento del filesystem e probe delle capabilities reali.

Non si fida di nomi o magic number da soli — esegue probe live
nella directory target (hardlink, reflink, symlink) per sapere
cosa funziona davvero su quel mount point.

Filesystem supportati e strategia scelta
-----------------------------------------

  Filesystem   OS            Hard Link  Reflink  Symlink  Strategia
  ──────────── ──────────── ─────────  ───────  ───────  ─────────────
  ext4         Linux         SI         NO       SI       HARDLINK
  btrfs        Linux         SI         SI*      SI       REFLINK → HARDLINK
  xfs          Linux         SI         SI*      SI       REFLINK → HARDLINK
  zfs          Linux/BSD     SI         NO       SI       HARDLINK
  tmpfs        Linux         SI         NO       SI       HARDLINK
  NFS v3/v4    Linux/macOS   SI**       NO       SI       HARDLINK → SYMLINK
  CIFS/SMB     Linux/Win     dipende    NO       dipende  HARDLINK → COPY
  9p           Linux         SI         NO       SI       HARDLINK
  NTFS         Windows       SI         NO       SI***    HARDLINK
  FAT32        Win/Lin/macOS NO         NO       NO       COPY
  exFAT        Win/Lin/macOS NO         NO       NO       COPY
  APFS         macOS         SI         SI       SI       REFLINK → HARDLINK
  HFS+         macOS         SI         NO       SI       HARDLINK
  HDFS         JVM/Linux     NO****     NO       NO       COPY

  * reflink solo se il filesystem è stato creato con -O reflink (xfs) o è btrfs
  ** NFS hardlink fallisce se src e dst sono su export diversi
  *** Windows symlink richiede Developer Mode o privilegi admin
  **** HDFS tramite WebHDFS/libhdfs: nessun concetto di hard link locale

Strategia di fallback
---------------------
  REFLINK → HARDLINK → SYMLINK → COPY_ATOMIC → COPY

  - REFLINK    : ioctl FICLONE (Linux) / clonefile (macOS) — CoW, istantaneo
  - HARDLINK   : os.link() — zero byte, stesso inode
  - SYMLINK    : os.symlink() — puntatore, elimina il link se il sorgente sparisce
  - COPY_ATOMIC: copia + rename atomico (tmp → dest) — sicuro su crash
  - COPY       : shutil.copy2 — fallback universale
"""

from __future__ import annotations

import ctypes
import os
import platform
import shutil
import struct
import sys
import tempfile
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Optional


# ─────────────────────────────────────────────
# ENUMS
# ─────────────────────────────────────────────

class FsType(str, Enum):
    """Filesystem identificato."""
    EXT2      = "ext2/3"
    EXT4      = "ext4"
    BTRFS     = "btrfs"
    XFS       = "xfs"
    ZFS       = "zfs"
    TMPFS     = "tmpfs"
    NFS       = "nfs"
    CIFS      = "cifs/smb"
    PLAN9     = "9p"
    NTFS      = "ntfs"
    FAT32     = "fat32/vfat"
    EXFAT     = "exfat"
    APFS      = "apfs"
    HFS       = "hfs+"
    HDFS      = "hdfs"
    FUSE      = "fuse"
    OVERLAYFS = "overlayfs"
    UNKNOWN   = "unknown"


class LinkStrategy(str, Enum):
    """
    Strategia di storage scelta dal probe.
    Ordinata dalla più efficiente alla meno efficiente.
    """
    REFLINK      = "reflink"       # CoW, zero byte, stesso blocco fisico
    HARDLINK     = "hardlink"      # Hard link, zero byte, stesso inode
    SYMLINK      = "symlink"       # Link simbolico
    COPY_ATOMIC  = "copy_atomic"   # Copia + rename atomico
    COPY         = "copy"          # Copia plain


# Magic number → FsType (da linux/magic.h)
_LINUX_MAGIC: dict[int, FsType] = {
    0xEF53:       FsType.EXT4,
    0xEF51:       FsType.EXT2,
    0x9123683E:   FsType.BTRFS,
    0x58465342:   FsType.XFS,
    0x2FC12FC1:   FsType.ZFS,
    0x01021994:   FsType.TMPFS,
    0x6969:       FsType.NFS,
    0xFF534D42:   FsType.CIFS,
    0xFE534D42:   FsType.CIFS,
    0x517B:       FsType.CIFS,
    0x01021997:   FsType.PLAN9,
    0x65735546:   FsType.FUSE,
    0x794C7630:   FsType.OVERLAYFS,
    0x4D44:       FsType.FAT32,    # MSDOS
    0x6969CAFE:   FsType.FAT32,
}

# ioctl per reflink su Linux (include/uapi/linux/fs.h)
_LINUX_FICLONE     = 0x40049409
_LINUX_FICLONERANGE = 0x4020940D


# ─────────────────────────────────────────────
# CAPABILITY RESULT
# ─────────────────────────────────────────────

@dataclass
class FsCapabilities:
    """
    Risultato del probe live su un path specifico.

    Tutti i campi boolean riflettono cosa funziona *davvero* in quel mount,
    non solo cosa dice il nome del filesystem.
    """
    path        : str
    os_name     : str           # Linux | Windows | Darwin | ...
    fs_type     : FsType        # filesystem rilevato
    fs_name_raw : str           # stringa grezza da /proc/mounts o GetVolumeInfo
    device      : int           # st_dev del path
    inode_bits  : int           # dimensione inode in bit (32 o 64)

    # Capabilities provate live
    can_hardlink  : bool = False
    can_reflink   : bool = False
    can_symlink   : bool = False

    # Flags aggiuntivi
    is_readonly   : bool = False
    is_remote     : bool = False   # NFS, CIFS, 9p, HDFS
    is_case_sensitive: bool = True

    # Strategia scelta
    strategy      : LinkStrategy = LinkStrategy.COPY
    strategy_note : str = ""

    def to_dict(self) -> dict:
        return {
            "path":           self.path,
            "os":             self.os_name,
            "fs_type":        self.fs_type.value,
            "fs_name_raw":    self.fs_name_raw,
            "device":         self.device,
            "inode_bits":     self.inode_bits,
            "can_hardlink":   self.can_hardlink,
            "can_reflink":    self.can_reflink,
            "can_symlink":    self.can_symlink,
            "is_readonly":    self.is_readonly,
            "is_remote":      self.is_remote,
            "strategy":       self.strategy.value,
            "strategy_note":  self.strategy_note,
        }

    def __str__(self) -> str:
        caps = []
        if self.can_reflink:  caps.append("reflink")
        if self.can_hardlink: caps.append("hardlink")
        if self.can_symlink:  caps.append("symlink")
        flags = []
        if self.is_remote:   flags.append("remote")
        if self.is_readonly: flags.append("readonly")
        return (
            f"FsCapabilities("
            f"fs={self.fs_type.value}  "
            f"os={self.os_name}  "
            f"caps=[{', '.join(caps) or 'none'}]  "
            f"flags=[{', '.join(flags) or 'none'}]  "
            f"strategy={self.strategy.value}"
            f")"
        )


# ─────────────────────────────────────────────
# PROBE ENGINE
# ─────────────────────────────────────────────

class FsProbe:
    """
    Rileva il filesystem e prova le capabilities reali nella directory indicata.

    Utilizzo
    --------
    >>> probe = FsProbe("/data/mnheme_files")
    >>> caps  = probe.detect()
    >>> print(caps)
    FsCapabilities(fs=ext4 os=Linux caps=[hardlink, symlink] strategy=hardlink)

    Il probe:
    1. Identifica OS e filesystem (via /proc/mounts, statfs, GetVolumeInformation)
    2. Tenta hard link, reflink, symlink nella stessa directory target
    3. Sceglie la strategia ottimale
    4. Cachea il risultato (il filesystem non cambia a runtime)
    """

    def __init__(self, target_dir: str | Path) -> None:
        self._target   = Path(target_dir)
        self._target.mkdir(parents=True, exist_ok=True)
        self._cached : Optional[FsCapabilities] = None

    def detect(self, force: bool = False) -> FsCapabilities:
        """
        Esegue il probe completo. Ritorna il risultato cachato alle chiamate successive.

        Parametri
        ---------
        force : se True, riesegue il probe anche se già cachato
        """
        if self._cached and not force:
            return self._cached

        os_name     = platform.system()   # Linux | Windows | Darwin
        stat_info   = os.stat(self._target)
        device      = stat_info.st_dev

        fs_name_raw, fs_type, is_remote = self._detect_fs_type(os_name)
        inode_bits  = self._detect_inode_size()
        is_readonly = self._detect_readonly()

        caps = FsCapabilities(
            path        = str(self._target),
            os_name     = os_name,
            fs_type     = fs_type,
            fs_name_raw = fs_name_raw,
            device      = device,
            inode_bits  = inode_bits,
            is_remote   = is_remote,
            is_readonly = is_readonly,
        )

        # Live probes nella stessa directory target
        self._probe_hardlink(caps)
        self._probe_reflink(caps, os_name)
        self._probe_symlink(caps)
        self._probe_case_sensitivity(caps)

        # Scegli strategia ottimale
        self._choose_strategy(caps)

        self._cached = caps
        return caps

    # ── DETECTION ────────────────────────────

    def _detect_fs_type(self, os_name: str) -> tuple[str, FsType, bool]:
        """
        Ritorna (raw_name, FsType, is_remote).
        Usa /proc/mounts su Linux, GetVolumeInformation su Windows,
        statfs su macOS.
        """
        raw     = "unknown"
        fstype  = FsType.UNKNOWN
        remote  = False

        if os_name == "Linux":
            raw, fstype, remote = self._detect_linux()

        elif os_name == "Windows":
            raw, fstype, remote = self._detect_windows()

        elif os_name == "Darwin":
            raw, fstype, remote = self._detect_macos()

        # Fallback: statfs magic number
        if fstype == FsType.UNKNOWN:
            fstype = self._detect_by_magic()

        return raw, fstype, remote

    def _detect_linux(self) -> tuple[str, FsType, bool]:
        """Parse /proc/mounts per trovare il mount point più specifico."""
        target_abs = str(self._target.resolve())
        best_match = ""
        best_fs    = "unknown"
        remote_fs  = {"nfs", "nfs4", "cifs", "smb", "smb2", "smb3",
                      "smbfs", "9p", "glusterfs", "lustre", "hdfs",
                      "webdav", "davfs", "s3fs", "gcsfuse"}

        try:
            with open("/proc/mounts") as f:
                for line in f:
                    parts = line.split()
                    if len(parts) < 3:
                        continue
                    mount_point = parts[1]
                    fs_name     = parts[2].lower()
                    # Trova il mount point più lungo che sia prefisso del target
                    if target_abs.startswith(mount_point) and len(mount_point) > len(best_match):
                        best_match = mount_point
                        best_fs    = fs_name
        except OSError:
            pass

        fs_type = self._linux_fsname_to_type(best_fs)
        is_remote = best_fs in remote_fs or best_fs.startswith("fuse.")

        return best_fs, fs_type, is_remote

    def _detect_windows(self) -> tuple[str, FsType, bool]:
        """Usa GetVolumeInformationW per rilevare il filesystem su Windows."""
        raw    = "unknown"
        fstype = FsType.UNKNOWN
        remote = False

        try:
            import ctypes
            root = str(Path(self._target).anchor)
            buf  = ctypes.create_unicode_buffer(256)
            flags = ctypes.c_ulong(0)
            ctypes.windll.kernel32.GetVolumeInformationW(
                root, None, 0, None, None,
                ctypes.byref(flags), buf, 256
            )
            raw = buf.value.upper()

            _win_map = {
                "NTFS":    FsType.NTFS,
                "FAT32":   FsType.FAT32,
                "FAT":     FsType.FAT32,
                "EXFAT":   FsType.EXFAT,
                "REFS":    FsType.NTFS,    # ReFS: simile a NTFS per i nostri scopi
                "APFS":    FsType.APFS,
            }
            fstype = _win_map.get(raw, FsType.UNKNOWN)

            # Rileva UNC paths (network drives)
            remote = str(self._target).startswith("\\\\")

        except Exception:
            pass

        return raw.lower(), fstype, remote

    def _detect_macos(self) -> tuple[str, FsType, bool]:
        """Usa subprocess diskutil per ottenere il tipo di filesystem su macOS."""
        import subprocess, json
        raw    = "unknown"
        fstype = FsType.UNKNOWN
        remote = False

        try:
            out = subprocess.check_output(
                ["diskutil", "info", "-plist", str(self._target)],
                stderr=subprocess.DEVNULL, timeout=5
            )
            import plistlib
            info = plistlib.loads(out)
            raw  = info.get("FilesystemType", "unknown").lower()
            _mac_map = {
                "apfs":      FsType.APFS,
                "hfs":       FsType.HFS,
                "msdos":     FsType.FAT32,
                "exfat":     FsType.EXFAT,
                "nfs":       FsType.NFS,
                "smbfs":     FsType.CIFS,
                "ntfs":      FsType.NTFS,
            }
            fstype = _mac_map.get(raw, FsType.UNKNOWN)
            remote = raw in ("nfs", "smbfs", "afpfs", "webdav")
        except Exception:
            # Fallback: statfs.f_fstypename via ctypes
            try:
                import ctypes.util
                libc = ctypes.CDLL(ctypes.util.find_library("c"))
                class StatFS(ctypes.Structure):
                    _fields_ = [
                        ("f_otype",     ctypes.c_int16),
                        ("f_oflags",    ctypes.c_int16),
                        ("f_bsize",     ctypes.c_long),
                        ("f_iosize",    ctypes.c_long),
                        ("f_blocks",    ctypes.c_long),
                        ("f_bfree",     ctypes.c_long),
                        ("f_bavail",    ctypes.c_long),
                        ("f_files",     ctypes.c_long),
                        ("f_ffree",     ctypes.c_long),
                        ("f_fsid",      ctypes.c_int64),
                        ("f_owner",     ctypes.c_uint32),
                        ("f_reserved1", ctypes.c_int16),
                        ("f_type",      ctypes.c_int16),
                        ("f_flags",     ctypes.c_long),
                        ("f_reserved2", ctypes.c_long * 2),
                        ("f_fstypename", ctypes.c_char * 16),
                        ("f_mntonname", ctypes.c_char * 90),
                        ("f_mntfromname", ctypes.c_char * 90),
                        ("f_reserved3", ctypes.c_char * 16),
                    ]
                st = StatFS()
                libc.statfs(str(self._target).encode(), ctypes.byref(st))
                raw = st.f_fstypename.decode("utf-8", errors="replace").strip("\x00").lower()
            except Exception:
                pass

        return raw, fstype, remote

    def _detect_by_magic(self) -> FsType:
        """
        Usa statfs(2) per leggere il magic number del filesystem.
        Solo Linux (struct statfs.f_type).
        """
        if platform.system() != "Linux":
            return FsType.UNKNOWN
        try:
            import ctypes
            class LinuxStatFS(ctypes.Structure):
                _fields_ = [
                    ("f_type",    ctypes.c_long),
                    ("f_bsize",   ctypes.c_long),
                    ("f_blocks",  ctypes.c_ulong),
                    ("f_bfree",   ctypes.c_ulong),
                    ("f_bavail",  ctypes.c_ulong),
                    ("f_files",   ctypes.c_ulong),
                    ("f_ffree",   ctypes.c_ulong),
                    ("f_fsid",    ctypes.c_longlong),
                    ("f_namelen", ctypes.c_long),
                    ("f_frsize",  ctypes.c_long),
                    ("f_flags",   ctypes.c_long),
                    ("f_spare",   ctypes.c_long * 4),
                ]
            libc   = ctypes.CDLL("libc.so.6", use_errno=True)
            sfs    = LinuxStatFS()
            ret    = libc.statfs(str(self._target).encode(), ctypes.byref(sfs))
            if ret == 0:
                magic = sfs.f_type & 0xFFFFFFFF
                return _LINUX_MAGIC.get(magic, FsType.UNKNOWN)
        except Exception:
            pass
        return FsType.UNKNOWN

    # ── LIVE PROBES ──────────────────────────

    def _probe_hardlink(self, caps: FsCapabilities) -> None:
        """
        Prova os.link() nella directory target.
        Richiede che src e dst siano sullo stesso device.
        """
        src = dst = None
        try:
            fd, src = tempfile.mkstemp(dir=self._target, prefix=".probe_hl_")
            os.close(fd)
            dst = src + ".hl"
            os.link(src, dst)
            s1, s2 = os.stat(src), os.stat(dst)
            caps.can_hardlink = (s1.st_ino == s2.st_ino) and (s1.st_dev == s2.st_dev)
        except (OSError, NotImplementedError):
            caps.can_hardlink = False
        finally:
            for p in [src, dst]:
                if p and os.path.exists(p):
                    try: os.unlink(p)
                    except: pass

    def _probe_reflink(self, caps: FsCapabilities, os_name: str) -> None:
        """
        Prova reflink (Copy-on-Write):
        - Linux: ioctl FICLONE
        - macOS: clonefile(2)
        """
        src = dst = None
        try:
            fd, src = tempfile.mkstemp(dir=self._target, prefix=".probe_rl_")
            os.write(fd, b"\x00" * 4096)
            os.close(fd)
            dst = src + ".rl"

            if os_name == "Linux":
                import fcntl
                with open(src, "rb") as s, open(dst, "w+b") as d:
                    fcntl.ioctl(d.fileno(), _LINUX_FICLONE, s.fileno())
                caps.can_reflink = os.path.exists(dst)

            elif os_name == "Darwin":
                import ctypes.util
                libc = ctypes.CDLL(ctypes.util.find_library("c"))
                # clonefile(src, dst, flags=0)
                ret = libc.clonefile(
                    src.encode(), dst.encode(), ctypes.c_uint(0)
                )
                caps.can_reflink = (ret == 0)

        except (OSError, AttributeError, NotImplementedError):
            caps.can_reflink = False
        finally:
            for p in [src, dst]:
                if p and os.path.exists(p):
                    try: os.unlink(p)
                    except: pass

    def _probe_symlink(self, caps: FsCapabilities) -> None:
        """Prova os.symlink() nella directory target."""
        src = lnk = None
        try:
            fd, src = tempfile.mkstemp(dir=self._target, prefix=".probe_sl_")
            os.close(fd)
            lnk = src + ".sl"
            os.symlink(src, lnk)
            caps.can_symlink = os.path.islink(lnk)
        except (OSError, NotImplementedError):
            caps.can_symlink = False
        finally:
            for p in [lnk, src]:
                if p and os.path.lexists(p):
                    try: os.unlink(p)
                    except: pass

    def _probe_case_sensitivity(self, caps: FsCapabilities) -> None:
        """Prova se il filesystem è case-sensitive."""
        fd = path = None
        try:
            fd, path = tempfile.mkstemp(dir=self._target, prefix=".probe_cs_")
            os.close(fd)
            upper = path.upper()
            caps.is_case_sensitive = not os.path.exists(upper) or upper == path
        except Exception:
            caps.is_case_sensitive = True
        finally:
            if path and os.path.exists(path):
                try: os.unlink(path)
                except: pass

    def _detect_readonly(self) -> bool:
        """Prova se la directory è in sola lettura."""
        try:
            fd, p = tempfile.mkstemp(dir=self._target, prefix=".probe_rw_")
            os.close(fd)
            os.unlink(p)
            return False
        except OSError:
            return True

    def _detect_inode_size(self) -> int:
        """Stima la larghezza degli inode number (32 o 64 bit)."""
        try:
            ino = os.stat(self._target).st_ino
            return 64 if ino > 0xFFFFFFFF else 32
        except Exception:
            return 32

    # ── STRATEGIA ────────────────────────────

    def _choose_strategy(self, caps: FsCapabilities) -> None:
        """
        Sceglie la strategia migliore in base alle capability live.

        Priorità:
          REFLINK > HARDLINK > SYMLINK > COPY_ATOMIC > COPY

        SYMLINK viene preferito a COPY_ATOMIC solo se il filesystem
        non è remoto (symlink su NFS può spezzarsi se il sorgente
        viene smontato o migrato).
        """
        if caps.is_readonly:
            caps.strategy      = LinkStrategy.COPY
            caps.strategy_note = "filesystem read-only: impossibile scrivere"
            return

        if caps.can_reflink:
            caps.strategy      = LinkStrategy.REFLINK
            caps.strategy_note = f"CoW reflink nativo su {caps.fs_type.value}"

        elif caps.can_hardlink:
            caps.strategy      = LinkStrategy.HARDLINK
            caps.strategy_note = f"hard link (zero byte, stesso inode) su {caps.fs_type.value}"

        elif caps.can_symlink and not caps.is_remote:
            caps.strategy      = LinkStrategy.SYMLINK
            caps.strategy_note = (
                f"symlink su {caps.fs_type.value}  "
                f"(no hard link: es. FAT32/exFAT/cross-device)"
            )

        else:
            caps.strategy      = LinkStrategy.COPY_ATOMIC
            caps.strategy_note = (
                f"copia atomica (tmp+rename) su {caps.fs_type.value}  "
                f"(es. FAT32, exFAT, HDFS, FS remoto senza hard link)"
            )

    # ── HELPERS ──────────────────────────────

    @staticmethod
    def _linux_fsname_to_type(name: str) -> FsType:
        _map = {
            "ext2":     FsType.EXT2,
            "ext3":     FsType.EXT2,
            "ext4":     FsType.EXT4,
            "btrfs":    FsType.BTRFS,
            "xfs":      FsType.XFS,
            "zfs":      FsType.ZFS,
            "tmpfs":    FsType.TMPFS,
            "ramfs":    FsType.TMPFS,
            "nfs":      FsType.NFS,
            "nfs4":     FsType.NFS,
            "cifs":     FsType.CIFS,
            "smb":      FsType.CIFS,
            "smb2":     FsType.CIFS,
            "smb3":     FsType.CIFS,
            "smbfs":    FsType.CIFS,
            "9p":       FsType.PLAN9,
            "fuse.9p":  FsType.PLAN9,
            "vfat":     FsType.FAT32,
            "fat":      FsType.FAT32,
            "msdos":    FsType.FAT32,
            "exfat":    FsType.EXFAT,
            "ntfs":     FsType.NTFS,
            "ntfs-3g":  FsType.NTFS,
            "fuse.ntfs-3g": FsType.NTFS,
            "overlayfs":FsType.OVERLAYFS,
            "overlay":  FsType.OVERLAYFS,
            "fuse":     FsType.FUSE,
        }
        # Cerca per prefisso (es. fuse.glusterfs, fuse.s3fs)
        t = _map.get(name.lower())
        if t:
            return t
        if name.startswith("fuse."):
            return FsType.FUSE
        return FsType.UNKNOWN
