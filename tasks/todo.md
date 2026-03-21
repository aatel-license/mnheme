# Task: Diary/Journal Aesthetic with Themes and Mobile Responsiveness

## Plan
- [x] Step 1: Create `src/core/themes.js` — define 5 themes with CSS variable maps
- [x] Step 2: Create `src/hooks/useTheme.jsx` — theme context, persistence via localStorage, apply via data-theme attribute
- [x] Step 3: ThemeProvider integrated into useTheme.jsx (no separate file needed)
- [x] Step 4: Rewrite `src/index.css` — CSS variables per theme, diary aesthetic, full mobile responsiveness
- [x] Step 5: Update `src/components/Layout.jsx` — add mobile hamburger, sidebar overlay, remove scanlines
- [x] Step 6: Update `src/components/Sidebar.jsx` — collapsible sidebar with close-on-click behavior
- [x] Step 7: Create `src/components/ThemeSelector.jsx` — theme selection UI with swatches
- [x] Step 8: Update `src/pages/SettingsPage.jsx` — add Appearance tab (default tab)
- [x] Step 9: Update `src/App.jsx` — wrap with ThemeProvider
- [x] Step 10: Update `index.html` — add Google Fonts preconnect, update title
- [x] Step 11: Fix: rename useTheme.js -> useTheme.jsx (JSX in file)
- [x] Step 12: Fix old CSS var references in Timeline.jsx and Stats.jsx (--green -> --accent)
- [x] Step 13: Build verification — `npm run build` passes clean

## Review
### Files Created (3)
- `src/core/themes.js` — 5 diary/journal themes (Classic, Moonlight, Vintage, Zen, Garden)
- `src/hooks/useTheme.jsx` — ThemeProvider context + useTheme hook + localStorage persistence
- `src/components/ThemeSelector.jsx` — Theme picker UI with color swatches

### Files Modified (7)
- `src/index.css` — Complete rewrite: diary aesthetic, CSS variables, mobile responsive, 5 breakpoints
- `src/components/Layout.jsx` — Mobile header with hamburger, sidebar overlay, scroll lock
- `src/components/Sidebar.jsx` — Accepts isOpen/onClose props, closes on nav click
- `src/components/Timeline.jsx` — Updated old --green refs to --accent
- `src/components/Stats.jsx` — Updated old --green-dim/--green refs to --accent-dim/--accent
- `src/pages/SettingsPage.jsx` — Added Appearance tab with ThemeSelector
- `src/App.jsx` — Wrapped with ThemeProvider
- `index.html` — Google Fonts preconnect, updated title

### Verification
- `npm run build` passes with zero errors
- All old --green CSS variable references updated to --accent equivalents
- No broken imports
