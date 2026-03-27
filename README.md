# Encrypted QR Code Generator for Event Sign-ups

Generate secure, encrypted QR codes from an Excel spreadsheet of event attendees. Each QR code encodes a person's name and food restrictions, encrypted with a master password. Perfect for event registration and catering coordination.

## Features

✅ **Privacy-First:** All processing happens locally (no servers, no uploads)
✅ **Encrypted Data:** QR codes contain encrypted, unreadable data
✅ **Client-Side Decryption:** HTML page decrypts in your browser (no backend needed)
✅ **Simple Workflow:** Run script → get QR codes → use HTML page at event
✅ **No Dependencies:** HTML decryption page works offline with no external libraries

## Quick Start

### 1. Install Python Dependencies

```bash
cd qr-generator
pip install -r requirements.txt
```

### 2. Create Your Excel File

Create an Excel file (`attendees.xlsx`) with columns:
- **A:** Email
- **B:** Full Name
- **C:** Day One (confirmation)
- **D:** Day Two (confirmation)
- **E:** Food Restrictions
- **F:** Squad/Team

Example:
```
Email                          | Full Name        | Day One       | Day Two       | Food Restrictions    | Squad
john.smith@company.com         | John Smith       | Count me in   | Count me in   | None                 | Squad A
maria.rodriguez@company.com    | Maria Rodriguez  | Count me in   | No food      | Vegetarian           | Squad B
```

### 3. Generate QR Codes

```bash
python generate_qr_codes.py attendees.xlsx -o qr_codes -p "your_master_password"
```

This creates a folder `qr_codes/` with one PNG file per attendee.

### 4. At the Event

1. Print or display the QR code images
2. Open `decrypt.html` in a browser on your phone/laptop
3. Scan a QR code with your phone's camera
4. Copy the encrypted data
5. Paste into the decryption page
6. Enter the master password
7. See the attendee's name and food restrictions

## Security

### How It Works

1. **Excel file** stays on your machine (never uploaded)
2. **Python script** reads Excel and encrypts locally
3. **QR codes** contain encrypted data (unreadable without password)
4. **Decryption page** uses Web Crypto API (modern browsers)
   - All decryption happens in your browser
   - No data sent to servers
   - Works completely offline

### What About the Excel File?

Once you've generated the QR codes:
1. Save the `qr_codes/` folder
2. Copy `decrypt.html` to your phone/laptop
3. **Delete the original Excel file**
4. The QR codes are useless without the password, even if leaked

### Passwords

- **Master Password:** Shared with your event team
- Everyone uses the SAME password to decrypt
- Not per-person, so keep it safe but shareable

## File Structure

```
qr-generator/
├── generate_qr_codes.py    # Main script
├── encryption.py           # AES-256 encryption utility
├── excel_reader.py         # Read Excel file
├── qr_generator.py         # Generate QR images
├── decrypt.html            # Standalone decryption page
├── requirements.txt        # Python dependencies
├── sample_data.xlsx        # Example Excel file
├── tests/                  # Unit tests
└── README.md              # This file
```

## Testing

Run tests to verify everything works:

```bash
cd qr-generator
pytest -v
```

Or test with sample data:

```bash
python generate_qr_codes.py sample_data.xlsx -o test_output -p "password123"
```

## Troubleshooting

### "Module not found" errors
```bash
pip install -r requirements.txt
```

### "Can't decrypt" in HTML page
- Check you're using the correct master password
- Make sure QR code was scanned completely
- Try copying the encrypted data directly (not scanning)

### QR codes too small/large
Edit line in `qr_generator.py`:
```python
save_qr_code(encrypted, output_path, size=10)  # Change 10 to desired size
```

### File naming issues (on Windows)
Some attendee names may have special characters. If you get errors:
- Try running with fewer attendees first
- Or modify naming in `generate_qr_codes.py`:
```python
output_path = os.path.join(output_dir, f"{idx:03d}_{name}.png")  # Use numbering
```

## Technical Details

### Encryption Algorithm
- **Type:** AES-256-GCM (authenticated encryption)
- **Key Derivation:** PBKDF2 (100,000 iterations, SHA-256)
- **Encoding:** Base64 (URL-safe) for QR compatibility

### QR Code Format
Each QR code contains:
```
base64(salt || nonce || ciphertext || tag)
```

Where `salt` and `nonce` are random for each encryption, making each QR code unique even for the same data.

### Decryption Page
- Pure JavaScript (no frameworks)
- Uses Web Crypto API (built into modern browsers)
- Works offline
- No logging, no storage, no external calls

## License

This project is provided as-is. Use for your event, modify as needed.

## Questions?

For issues or improvements, contact your event organizer.
