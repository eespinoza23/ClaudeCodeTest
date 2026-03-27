# Encrypted QR Code Generator for Event Sign-ups

**Date:** 2026-03-26
**Project:** ClaudeCodeTest
**Scope:** Generate encrypted QR codes from Excel sign-up data for event lunch confirmations

---

## Overview

Build a privacy-first system to generate encrypted QR codes from an Excel spreadsheet of event attendees. Each QR code encodes a person's full name and food restrictions, encrypted with a master password. At the event, attendees' QR codes are scanned and decrypted locally on a phone using a standalone HTML page—no servers involved.

---

## Data Structure

**Input: Excel file with 6 columns**

| Column | Name | Content | Example |
|--------|------|---------|---------|
| A | Email | Company email address | john.smith@company.com |
| B | Full Name | First and last name | John Smith |
| C | Day One | Lunch confirmation | "Count me in" / "No food for me" / "None" |
| D | Day Two | Lunch confirmation | "Count me in" / "No food for me" / "None" |
| E | Food Restrictions | Dietary needs | "None" / "Vegetarian" / "Vegan" / "Gluten free" / allergies |
| F | Squad/Team | Team assignment | "Squad 1" / "Team A" / etc. |

**Columns used:** B (Full Name) + E (Food Restrictions)
**Columns ignored:** A, C, D, F

---

## Processing Pipeline

### Step 1: Read Excel
- Python script reads Excel file using `openpyxl` or `pandas`
- Iterates through all rows (skip header)
- Extracts: Full Name (B) + Food Restrictions (E)

### Step 2: Encrypt
- For each row, create plaintext: `"Full Name | Food Restrictions"`
  - Example: `"John Smith | Vegetarian"`
- Encrypt using AES-256-GCM with master password (derived via PBKDF2)
- Encrypt library: `cryptography.fernet` (simpler) or `PyCryptodome` (more standard)

### Step 3: Generate QR Code
- Convert encrypted bytes to URL-safe base64 string
- Generate QR code from base64 string using `qrcode` library
- Encode QR as PNG image

### Step 4: Save Output
- Save each QR code as individual PNG file
- Filename: `{Full Name}.png` (e.g., `John Smith.png`)
- Output folder: Same as script or user-specified

### Step 5: Cleanup Prompt
- After successful generation, prompt user to delete source Excel file
- Rationale: Once QR codes exist, Excel file is unnecessary and a security risk

---

## Encryption Model

**Algorithm:** AES-256 with authenticated encryption (HMAC or GCM)
**Key Derivation:** PBKDF2 from master password
**Master Password:** Single password shared with event team (not per-person)

**Encrypted Payload Format:**
```
{
  "name": "Full Name",
  "restrictions": "Food Restrictions",
  "timestamp": "ISO timestamp" (optional, for ordering)
}
```
Convert to JSON → encrypt → base64 → encode in QR

---

## QR Code & Decryption

### QR Code Content
- Each QR contains a base64-encoded encrypted string (no plain data)
- QR data is approximately 300-500 bytes (easily fits in QR code)

### Decryption Workflow
1. **Scan:** Phone scans QR code → captures encrypted base64 string
2. **Paste:** User opens decryption web page, pastes encrypted string
3. **Enter Password:** User enters master password
4. **Decrypt:** Browser decrypts client-side using JavaScript `TweetNaCl.js` or `libsodium.js`
5. **Display:** Show full name + food restrictions

### Decryption Page (Standalone HTML)
- Single `.html` file (no backend, no server)
- Client-side JavaScript decryption (all processing in browser)
- Works offline
- No storage, no logging, no external calls
- User brings HTML file to event on phone/laptop

---

## Output Format

**QR Code Images:**
- Format: PNG
- Naming: `{Full Name}.png` (e.g., `John Smith.png`, `Maria Rodriguez.png`)
- Size: ~300×300 pixels (adjustable)
- One file per person
- Output folder: Same as Excel, or user-specified

**Decryption Page:**
- File: `decrypt.html`
- Standalone, no dependencies
- Can be opened from local filesystem or served via HTTP
- Contains embedded JavaScript & CSS

---

## Security & Privacy

**Data Isolation:**
- Excel file stays on user's machine (never uploaded)
- Python script runs locally (no internet calls, no data transmission)
- QR codes are encrypted (unreadable without password)
- Decryption happens in user's browser (no server sees decrypted data)

**Deletion Workflow:**
- After QR codes generated, user deletes source Excel file
- QR codes + HTML page are all that remain
- Even if QR codes are lost/leaked, they're useless without the password

**At the Event:**
- Organizer brings decryption HTML file on phone/laptop
- Scan QR → paste encrypted data → enter password → see info
- No internet needed, no cloud, no databases

---

## File Deliverables

1. **`generate_qr_codes.py`** — Main Python script
   - Input: Excel file path, master password
   - Output: Folder of PNG files

2. **`decrypt.html`** — Standalone decryption page
   - Input: Encrypted base64 string, password
   - Output: Decrypted name + restrictions

3. **`README.md`** — Instructions
   - How to run the script
   - How to use the decryption page
   - Security notes

---

## Implementation Order

1. **Create sample Excel file** (fake data for testing)
2. **Write `generate_qr_codes.py`**
   - Read Excel, extract columns
   - Encrypt using AES
   - Generate QR codes
   - Save PNG files
3. **Write `decrypt.html`**
   - Client-side decryption JavaScript
   - Paste encrypted data, enter password, display result
4. **Test** with sample data
5. **Create `README.md`** with instructions
6. **Prepare for real data** (user provides Excel when ready)

---

## Assumptions & Constraints

- **Python 3.8+** available on user's machine
- **Master password:** User will generate and protect (not stored anywhere)
- **QR code size:** Standard (can be printed on labels/cards)
- **No backend:** Everything runs locally
- **No persistence:** Decryption page doesn't save or log anything

---

## Success Criteria

- ✅ Python script reads Excel correctly
- ✅ Encryption/decryption round-trips without loss
- ✅ QR codes generate and encode encrypted data
- ✅ HTML page decrypts successfully with correct password
- ✅ QR codes reject wrong password with clear error
- ✅ All processing stays local (no uploads, no servers)
- ✅ User can delete Excel and keep only QR codes + HTML

