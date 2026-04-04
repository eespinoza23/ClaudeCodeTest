# Studio Français — GitHub Gist Cloud Sync

**Date:** 2026-04-04  
**Project:** https://eespinoza23.github.io/studio-francais/  
**Scope:** Single-user cross-device progress sync via GitHub Gist

---

## Problem

Progress is stored in `localStorage` only. Checking off lessons on one device is invisible on any other device or browser.

## Solution

Add a thin sync layer that mirrors `localStorage` state to a private GitHub Gist. No backend, no new accounts — uses the user's existing GitHub account.

---

## Architecture

```
Checkbox click
    → localStorage write (existing, unchanged)
    → debounced Gist write (2s delay, new)

App load
    → fetch Gist state
    → compare timestamps with localStorage
    → load whichever is newer
```

**Storage keys added to localStorage:**
- `jcf_pat` — GitHub Personal Access Token (gist scope only)
- `jcf_gist_id` — ID of the private gist created during setup

**Gist contents** — single file `progress.json`:
```json
{
  "lastModified": "2026-04-04T14:32:00Z",
  "c1_w1_d0": true,
  "c1_w1_d1": false
}
```

---

## Components

### 1. Sync Engine (`syncEngine`)
Standalone module, no dependencies on existing app logic.

- `init()` — on app load: fetch Gist, compare timestamps, merge
- `save(state)` — debounced 2s: write state + timestamp to Gist
- `setup(pat)` — one-time: POST to create gist, store pat + gistId
- `getStatus()` — returns `synced | syncing | error | unconfigured`

### 2. Setup Modal
Triggered by clicking the "☁ Sync" header button when unconfigured.

- Step 1: Instructions + link to GitHub token creation (gist scope only)
- Step 2: PAT input field → calls `syncEngine.setup(pat)`
- Step 3: Success confirmation showing Gist ID for use on other devices

### 3. Status Indicator
Small icon in the app header, always visible after setup.

| State | Display |
|-------|---------|
| `synced` | ☁ Synced (green, last sync time on hover) |
| `syncing` | ⟳ Syncing... |
| `error` | ⚠ Sync error (click to retry) |
| `unconfigured` | ☁ Setup Sync |

---

## Setup Flow (new device)

**First device:**
1. Click "☁ Setup Sync"
2. Follow link to GitHub → create PAT with `gist` scope
3. Paste PAT → app creates private gist automatically
4. Done — Gist ID shown in settings for use on other devices

**Subsequent devices:**
1. Click "☁ Setup Sync"
2. Paste same PAT
3. Paste Gist ID (from settings on first device)
4. App loads existing progress immediately

---

## Conflict Resolution

On load, compare `lastModified` timestamps:

```
Gist newer     → overwrite localStorage, use Gist data
Local newer    → write localStorage to Gist, use local data
Gist same age  → no-op
Gist unreachable → use localStorage silently (offline mode)
```

---

## API Calls

| Action | Endpoint | When |
|--------|----------|------|
| Create gist | `POST /gists` | Setup only (once) |
| Read progress | `GET /gists/{id}` | App load |
| Write progress | `PATCH /gists/{id}` | Every save (debounced 2s) |

Auth: `Authorization: Bearer {PAT}` on all calls.

---

## Offline Behavior

- App works exactly as before when offline — localStorage is always the source of truth
- Gist writes fail silently; status indicator shows error
- On next load with connectivity, timestamps resolve which side wins

---

## Constraints

- PAT is stored in localStorage — acceptable for personal single-user use
- PAT should have **only** `gist` scope to minimize exposure
- No multi-user support in this design

---

## Out of Scope

- Multiple users / student accounts
- Real-time multi-tab sync
- Progress analytics or history
