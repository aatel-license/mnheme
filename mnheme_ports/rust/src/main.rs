// mnheme/rust/src/main.rs
use mnheme::{MemoryDB, Feeling};

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut db = MemoryDB::open("mente.mnheme")?;

    // Store a memory
    let mem = db.remember(
        "Debito",
        Feeling::Ansia,
        "Ho firmato il mutuo oggi. 25 anni.",
        Some("Era un mercoledì piovoso."),
        Some(vec!["casa".into(), "mutuo".into(), "2024".into()]),
        None,
    )?;
    println!("Stored: {:?}", mem.memory_id);

    // Recall
    let memories = db.recall("Debito", None, None, false)?;
    println!("Recalled {} memories for Debito", memories.len());

    // Stats
    println!("Total records: {}", db.count(None, None));
    println!("Feelings: {:?}", db.feeling_distribution());

    // Export
    let json = db.export_json()?;
    std::fs::write("backup.json", json)?;
    println!("Exported to backup.json");

    Ok(())
}
