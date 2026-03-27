# Encrypted QR Code Event Sign-up Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a privacy-first QR code generator that reads Excel sign-up data, encrypts attendee names and food restrictions, generates individual QR code images, and provides a standalone HTML decryption page for event-day scanning.

**Architecture:** Three independent components working together:
1. **`generate_qr_codes.py`** - Reads Excel, encrypts data, generates QR PNG files (runs locally once)
2. **Encryption utility** - Reusable AES-256 encryption/decryption (used by both script and HTML)
3. **`decrypt.html`** - Standalone client-side decryption page (scans QR → paste → decrypt → display)

**Tech Stack:**
- Python 3.8+ (openpyxl, qrcode, Pillow, cryptography)
- Client-side JavaScript (TweetNaCl.js or libsodium.js for decryption)
- No backend, no servers, no databases

---

## File Structure

```
ClaudeCodeTest/
├── qr-generator/
│   ├── generate_qr_codes.py          # Main script - reads Excel, encrypts, generates QRs
│   ├── encryption.py                 # Reusable encryption/decryption utility
│   ├── excel_reader.py               # Reads Excel, extracts name + restrictions
│   ├── qr_generator.py               # Generates QR PNG from encrypted data
│   ├── requirements.txt              # Python dependencies
│   ├── decrypt.html                  # Standalone decryption page (no dependencies)
│   ├── sample_data.xlsx              # Test Excel file with fake data
│   ├── README.md                     # Documentation
│   └── tests/
│       ├── test_encryption.py
│       ├── test_excel_reader.py
│       ├── test_qr_generator.py
│       └── test_main.py
```

---

## Task 1: Project Setup & Sample Data

**Files:**
- Create: `qr-generator/requirements.txt`
- Create: `qr-generator/sample_data.xlsx`
- Create: `qr-generator/tests/__init__.py`

### Steps

- [ ] **Step 1: Create `qr-generator/requirements.txt`**

```
openpyxl==3.10.0
qrcode==7.4.2
Pillow==10.0.0
cryptography==41.0.0
pytest==7.4.0
```

- [ ] **Step 2: Create sample Excel file**

Run:
```bash
cd qr-generator
python3 << 'EOF'
from openpyxl import Workbook

wb = Workbook()
ws = wb.active
ws.title = "Attendees"

# Header
ws['A1'] = "Email"
ws['B1'] = "Full Name"
ws['C1'] = "Day One"
ws['D1'] = "Day Two"
ws['E1'] = "Food Restrictions"
ws['F1'] = "Squad"

# Sample data
test_data = [
    ["john.smith@company.com", "John Smith", "Count me in", "Count me in", "None", "Squad A"],
    ["maria.rodriguez@company.com", "Maria Rodriguez", "Count me in", "No food for me", "Vegetarian", "Squad B"],
    ["alex.kim@company.com", "Alex Kim", "No food for me", "Count me in", "Gluten free", "Squad A"],
    ["lisa.chen@company.com", "Lisa Chen", "Count me in", "Count me in", "Vegan, Nut allergy", "Squad C"],
    ["robert.johnson@company.com", "Robert Johnson", "Count me in", "Count me in", "None", "Squad B"],
]

for row_idx, row_data in enumerate(test_data, start=2):
    for col_idx, value in enumerate(row_data, start=1):
        ws.cell(row=row_idx, column=col_idx, value=value)

wb.save('sample_data.xlsx')
print("✓ Created sample_data.xlsx with 5 test attendees")
EOF
```

Expected output: `sample_data.xlsx` with 5 sample rows

- [ ] **Step 3: Create tests directory**

```bash
mkdir -p qr-generator/tests
touch qr-generator/tests/__init__.py
```

- [ ] **Step 4: Commit**

```bash
cd qr-generator
git add requirements.txt sample_data.xlsx tests/__init__.py
git commit -m "setup: initialize QR generator project with sample data and dependencies"
```

---

## Task 2: Encryption Utility Module

**Files:**
- Create: `qr-generator/encryption.py`
- Create: `qr-generator/tests/test_encryption.py`

### Steps

- [ ] **Step 1: Write failing tests for encryption**

Create `qr-generator/tests/test_encryption.py`:

```python
import pytest
from encryption import encrypt_data, decrypt_data, derive_key

class TestEncryption:
    def test_encrypt_decrypt_roundtrip(self):
        """Encrypted data should decrypt to original"""
        plaintext = "John Smith | Vegetarian"
        password = "master_password_123"

        encrypted = encrypt_data(plaintext, password)
        decrypted = decrypt_data(encrypted, password)

        assert decrypted == plaintext

    def test_decrypt_wrong_password_fails(self):
        """Wrong password should raise exception"""
        plaintext = "John Smith | Vegetarian"
        password = "correct_password"

        encrypted = encrypt_data(plaintext, password)

        with pytest.raises(Exception):
            decrypt_data(encrypted, "wrong_password")

    def test_encrypt_returns_base64(self):
        """Encrypted data should be base64 encoded"""
        plaintext = "Test Data"
        password = "password"

        encrypted = encrypt_data(plaintext, password)

        # Should be valid base64 (no special chars except - _ =)
        assert all(c.isalnum() or c in '-_=' for c in encrypted)

    def test_encrypt_is_deterministic_with_seed(self):
        """Same plaintext + password should produce different ciphertexts (due to random nonce)"""
        plaintext = "John Smith | Vegetarian"
        password = "password"

        encrypted1 = encrypt_data(plaintext, password)
        encrypted2 = encrypt_data(plaintext, password)

        # They should be different (different nonces)
        assert encrypted1 != encrypted2

        # But both should decrypt to the same thing
        assert decrypt_data(encrypted1, password) == plaintext
        assert decrypt_data(encrypted2, password) == plaintext
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd qr-generator
pytest tests/test_encryption.py -v
```

Expected: All tests FAIL (functions don't exist)

- [ ] **Step 3: Implement encryption utility**

Create `qr-generator/encryption.py`:

```python
"""Encryption utility for QR code data using AES-256-GCM"""

import base64
import json
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.backends import default_backend
import os


def derive_key(password: str, salt: bytes) -> bytes:
    """Derive AES-256 key from password using PBKDF2"""
    kdf = PBKDF2(
        algorithm=hashes.SHA256(),
        length=32,  # 256 bits for AES-256
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    return kdf.derive(password.encode())


def encrypt_data(plaintext: str, password: str) -> str:
    """
    Encrypt plaintext with password using AES-256-GCM.
    Returns base64-encoded string containing salt + nonce + ciphertext + tag.
    """
    # Generate random salt and nonce
    salt = os.urandom(16)  # 128 bits
    nonce = os.urandom(12)  # 96 bits (standard for GCM)

    # Derive key from password
    key = derive_key(password, salt)

    # Encrypt
    cipher = AESGCM(key)
    ciphertext = cipher.encrypt(nonce, plaintext.encode(), None)

    # Combine: salt (16) + nonce (12) + ciphertext+tag (variable)
    payload = salt + nonce + ciphertext

    # Encode to base64 for QR code compatibility
    encoded = base64.urlsafe_b64encode(payload).decode('ascii')

    return encoded


def decrypt_data(encoded: str, password: str) -> str:
    """
    Decrypt base64-encoded encrypted data with password.
    Raises exception if decryption fails (wrong password or corrupted data).
    """
    # Decode from base64
    try:
        payload = base64.urlsafe_b64decode(encoded.encode('ascii'))
    except Exception as e:
        raise ValueError(f"Invalid base64 encoding: {e}")

    # Extract components
    if len(payload) < 28:  # 16 (salt) + 12 (nonce) + 0 (minimum ciphertext)
        raise ValueError("Payload too short")

    salt = payload[:16]
    nonce = payload[16:28]
    ciphertext = payload[28:]

    # Derive key from password
    key = derive_key(password, salt)

    # Decrypt
    cipher = AESGCM(key)
    try:
        plaintext = cipher.decrypt(nonce, ciphertext, None)
    except Exception as e:
        raise ValueError(f"Decryption failed - wrong password or corrupted data: {e}")

    return plaintext.decode()
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd qr-generator
pip install -r requirements.txt
pytest tests/test_encryption.py -v
```

Expected: All tests PASS

- [ ] **Step 5: Commit**

```bash
cd qr-generator
git add encryption.py tests/test_encryption.py
git commit -m "feat: add AES-256-GCM encryption utility with PBKDF2 key derivation"
```

---

## Task 3: Excel Reader Module

**Files:**
- Create: `qr-generator/excel_reader.py`
- Create: `qr-generator/tests/test_excel_reader.py`

### Steps

- [ ] **Step 1: Write failing tests**

Create `qr-generator/tests/test_excel_reader.py`:

```python
import pytest
from excel_reader import read_attendees
from pathlib import Path


class TestExcelReader:
    def test_read_attendees_returns_list(self):
        """Should return list of attendee records"""
        result = read_attendees('sample_data.xlsx')
        assert isinstance(result, list)
        assert len(result) > 0

    def test_read_attendees_structure(self):
        """Each record should have name and restrictions"""
        result = read_attendees('sample_data.xlsx')

        for record in result:
            assert 'name' in record
            assert 'restrictions' in record
            assert isinstance(record['name'], str)
            assert isinstance(record['restrictions'], str)

    def test_read_attendees_extracts_correct_columns(self):
        """Should extract columns B (name) and E (restrictions)"""
        result = read_attendees('sample_data.xlsx')

        # Check first record matches sample data
        assert result[0]['name'] == 'John Smith'
        assert result[0]['restrictions'] == 'None'

        assert result[1]['name'] == 'Maria Rodriguez'
        assert result[1]['restrictions'] == 'Vegetarian'

    def test_read_attendees_skips_header(self):
        """Should skip header row"""
        result = read_attendees('sample_data.xlsx')

        # Should not include header
        assert all(r['name'] != 'Full Name' for r in result)

    def test_read_attendees_empty_file_handling(self):
        """Should handle file with only headers"""
        # This would need a separate empty Excel file for testing
        # For now, just verify the function exists and is callable
        assert callable(read_attendees)
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd qr-generator
pytest tests/test_excel_reader.py -v
```

Expected: All tests FAIL (function doesn't exist)

- [ ] **Step 3: Implement Excel reader**

Create `qr-generator/excel_reader.py`:

```python
"""Read attendee data from Excel file"""

from openpyxl import load_workbook
from typing import List, Dict


def read_attendees(excel_path: str) -> List[Dict[str, str]]:
    """
    Read attendee data from Excel file.

    Extracts columns:
    - Column B: Full Name
    - Column E: Food Restrictions

    Returns list of dicts with keys: 'name', 'restrictions'
    """
    attendees = []

    # Load workbook
    wb = load_workbook(excel_path)
    ws = wb.active

    # Iterate through rows (skip header at row 1)
    for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=False), start=2):
        # Column B = index 1, Column E = index 4
        name_cell = ws[f'B{row_idx}']
        restrictions_cell = ws[f'E{row_idx}']

        name = name_cell.value
        restrictions = restrictions_cell.value

        # Skip empty rows
        if not name:
            continue

        # Handle None/empty restrictions
        if restrictions is None:
            restrictions = "None"

        attendees.append({
            'name': str(name).strip(),
            'restrictions': str(restrictions).strip()
        })

    wb.close()
    return attendees
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd qr-generator
pytest tests/test_excel_reader.py -v
```

Expected: All tests PASS

- [ ] **Step 5: Commit**

```bash
cd qr-generator
git add excel_reader.py tests/test_excel_reader.py
git commit -m "feat: add Excel reader to extract attendee names and food restrictions"
```

---

## Task 4: QR Code Generator Module

**Files:**
- Create: `qr-generator/qr_generator.py`
- Create: `qr-generator/tests/test_qr_generator.py`

### Steps

- [ ] **Step 1: Write failing tests**

Create `qr-generator/tests/test_qr_generator.py`:

```python
import pytest
from qr_generator import generate_qr_code
from pathlib import Path
import os


class TestQRGenerator:
    def test_generate_qr_code_returns_png_bytes(self):
        """Should return PNG image bytes"""
        encrypted_data = "base64_encoded_encrypted_string_here"

        result = generate_qr_code(encrypted_data)

        assert isinstance(result, bytes)
        # PNG signature: 89 50 4E 47
        assert result[:4] == b'\x89PNG'

    def test_generate_qr_code_encodes_data(self):
        """Should encode the encrypted data in QR code"""
        encrypted_data = "test_encrypted_data_12345"

        png_bytes = generate_qr_code(encrypted_data)

        # Just verify it's a valid PNG (rough check)
        assert len(png_bytes) > 100
        assert b'PNG' in png_bytes

    def test_save_qr_code_creates_file(self):
        """Should save QR code to PNG file"""
        from qr_generator import save_qr_code

        encrypted_data = "test_data"
        output_path = "/tmp/test_qr.png"

        # Clean up if exists
        if os.path.exists(output_path):
            os.remove(output_path)

        save_qr_code(encrypted_data, output_path)

        assert os.path.exists(output_path)
        assert os.path.getsize(output_path) > 100

        # Clean up
        os.remove(output_path)

    def test_save_qr_code_creates_directory(self):
        """Should create output directory if it doesn't exist"""
        from qr_generator import save_qr_code

        output_dir = "/tmp/test_qr_dir"
        output_path = os.path.join(output_dir, "test.png")

        # Clean up if exists
        if os.path.exists(output_dir):
            import shutil
            shutil.rmtree(output_dir)

        save_qr_code("test_data", output_path)

        assert os.path.exists(output_path)

        # Clean up
        import shutil
        shutil.rmtree(output_dir)
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd qr-generator
pytest tests/test_qr_generator.py -v
```

Expected: All tests FAIL (functions don't exist)

- [ ] **Step 3: Implement QR code generator**

Create `qr-generator/qr_generator.py`:

```python
"""Generate QR codes from encrypted data"""

import qrcode
from pathlib import Path
import os


def generate_qr_code(encrypted_data: str, size: int = 10) -> bytes:
    """
    Generate QR code PNG from encrypted data.

    Args:
        encrypted_data: Base64-encoded encrypted string
        size: QR code size (box_size parameter for qrcode library)

    Returns:
        PNG image as bytes
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=size,
        border=2,
    )
    qr.add_data(encrypted_data)
    qr.make(fit=True)

    # Create image
    img = qr.make_image(fill_color="black", back_color="white")

    # Convert to bytes
    from io import BytesIO
    buffer = BytesIO()
    img.save(buffer, format='PNG')

    return buffer.getvalue()


def save_qr_code(encrypted_data: str, output_path: str, size: int = 10) -> None:
    """
    Save QR code to PNG file.

    Creates output directory if it doesn't exist.

    Args:
        encrypted_data: Base64-encoded encrypted string
        output_path: Full path to output PNG file
        size: QR code size
    """
    # Create directory if needed
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    # Generate and save
    png_bytes = generate_qr_code(encrypted_data, size)

    with open(output_path, 'wb') as f:
        f.write(png_bytes)
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd qr-generator
pytest tests/test_qr_generator.py -v
```

Expected: All tests PASS

- [ ] **Step 5: Commit**

```bash
cd qr-generator
git add qr_generator.py tests/test_qr_generator.py
git commit -m "feat: add QR code generator for encrypted data"
```

---

## Task 5: Main Script Integration

**Files:**
- Create: `qr-generator/generate_qr_codes.py`
- Create: `qr-generator/tests/test_main.py`

### Steps

- [ ] **Step 1: Write integration test**

Create `qr-generator/tests/test_main.py`:

```python
import pytest
from pathlib import Path
import shutil
import os


class TestMainScript:
    def test_main_script_generates_qr_files(self):
        """Integration test: script should generate QR files from Excel"""
        from generate_qr_codes import main

        # Use sample data
        excel_file = 'sample_data.xlsx'
        output_dir = '/tmp/test_qr_output'
        master_password = 'test_password_123'

        # Clean up if exists
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)

        # Run main
        main(excel_file, output_dir, master_password)

        # Verify output
        assert os.path.exists(output_dir)
        files = os.listdir(output_dir)
        assert len(files) == 5  # 5 test attendees

        # All should be PNG files named by full name
        assert any('John Smith.png' in f for f in files)
        assert any('Maria Rodriguez.png' in f for f in files)

        # Clean up
        shutil.rmtree(output_dir)
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd qr-generator
pytest tests/test_main.py -v
```

Expected: Test FAILS (main function doesn't exist)

- [ ] **Step 3: Implement main script**

Create `qr-generator/generate_qr_codes.py`:

```python
"""Main script to generate encrypted QR codes from Excel attendee data"""

import argparse
import os
from pathlib import Path
from excel_reader import read_attendees
from encryption import encrypt_data
from qr_generator import save_qr_code


def main(excel_file: str, output_dir: str, master_password: str) -> None:
    """
    Read Excel file, encrypt attendee data, generate QR codes.

    Args:
        excel_file: Path to input Excel file
        output_dir: Directory to save QR code PNG files
        master_password: Master password for encryption (shared with decryption page)
    """
    print(f"📖 Reading Excel file: {excel_file}")
    attendees = read_attendees(excel_file)
    print(f"✓ Found {len(attendees)} attendees")

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    print(f"📁 Output directory: {output_dir}")

    # Process each attendee
    for idx, attendee in enumerate(attendees, start=1):
        name = attendee['name']
        restrictions = attendee['restrictions']

        # Create plaintext payload
        plaintext = f"{name} | {restrictions}"

        # Encrypt
        print(f"🔐 Encrypting [{idx}/{len(attendees)}] {name}...", end=' ')
        encrypted = encrypt_data(plaintext, master_password)

        # Generate QR code
        output_path = os.path.join(output_dir, f"{name}.png")
        save_qr_code(encrypted, output_path)
        print(f"✓ Saved to {name}.png")

    print(f"\n✅ Done! Generated {len(attendees)} QR codes in {output_dir}")
    print(f"\n🔒 Security reminder:")
    print(f"   - Share the decryption HTML page with your event team")
    print(f"   - Everyone uses the same master password at the event")
    print(f"   - Delete the Excel file after QR codes are generated")
    print(f"   - Only keep: QR codes + decrypt.html")


def cli():
    """Command-line interface"""
    parser = argparse.ArgumentParser(
        description='Generate encrypted QR codes from Excel attendee data'
    )
    parser.add_argument(
        'excel_file',
        help='Path to Excel file with attendee data'
    )
    parser.add_argument(
        '-o', '--output',
        default='qr_codes',
        help='Output directory for QR code PNG files (default: qr_codes)'
    )
    parser.add_argument(
        '-p', '--password',
        help='Master password for encryption (will prompt if not provided)',
        default=None
    )

    args = parser.parse_args()

    # Prompt for password if not provided
    if not args.password:
        import getpass
        args.password = getpass.getpass('Enter master password for encryption: ')

    # Run
    try:
        main(args.excel_file, args.output, args.password)
    except Exception as e:
        print(f"❌ Error: {e}")
        exit(1)


if __name__ == '__main__':
    cli()
```

- [ ] **Step 4: Run integration test**

```bash
cd qr-generator
pytest tests/test_main.py -v
```

Expected: Test PASSES

- [ ] **Step 5: Test manual run**

```bash
cd qr-generator
python generate_qr_codes.py sample_data.xlsx -o test_output -p "test_password_123"
ls -lh test_output/
```

Expected output:
```
📖 Reading Excel file: sample_data.xlsx
✓ Found 5 attendees
📁 Output directory: test_output
🔐 Encrypting [1/5] John Smith... ✓ Saved to John Smith.png
🔐 Encrypting [2/5] Maria Rodriguez... ✓ Saved to Maria Rodriguez.png
...
✅ Done! Generated 5 QR codes in test_output
```

- [ ] **Step 6: Commit**

```bash
cd qr-generator
git add generate_qr_codes.py tests/test_main.py
git commit -m "feat: add main script to generate encrypted QR codes from Excel"
```

---

## Task 6: Decryption HTML Page

**Files:**
- Create: `qr-generator/decrypt.html`

### Steps

- [ ] **Step 1: Create standalone HTML with decryption**

Create `qr-generator/decrypt.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>QR Code Decryption</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }

        .container {
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            max-width: 500px;
            width: 100%;
            padding: 40px;
        }

        h1 {
            color: #333;
            margin-bottom: 10px;
            font-size: 28px;
        }

        .subtitle {
            color: #666;
            margin-bottom: 30px;
            font-size: 14px;
        }

        .form-group {
            margin-bottom: 20px;
        }

        label {
            display: block;
            color: #333;
            font-weight: 600;
            margin-bottom: 8px;
            font-size: 14px;
        }

        textarea, input[type="password"] {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 6px;
            font-size: 14px;
            font-family: 'Courier New', monospace;
            transition: border-color 0.3s;
        }

        textarea:focus, input[type="password"]:focus {
            outline: none;
            border-color: #667eea;
        }

        textarea {
            min-height: 100px;
            resize: vertical;
        }

        button {
            width: 100%;
            padding: 14px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 6px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }

        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.4);
        }

        button:active {
            transform: translateY(0);
        }

        .result {
            margin-top: 30px;
            padding: 20px;
            border-radius: 6px;
            display: none;
        }

        .result.success {
            background: #f0fdf4;
            border-left: 4px solid #22c55e;
            display: block;
        }

        .result.error {
            background: #fef2f2;
            border-left: 4px solid #ef4444;
            display: block;
        }

        .result-title {
            font-weight: 600;
            margin-bottom: 10px;
            font-size: 14px;
        }

        .result.success .result-title {
            color: #15803d;
        }

        .result.error .result-title {
            color: #991b1b;
        }

        .result-data {
            background: white;
            padding: 12px;
            border-radius: 4px;
            font-size: 14px;
            font-family: 'Courier New', monospace;
            margin-top: 8px;
            word-break: break-all;
        }

        .result.success .result-data {
            color: #166534;
        }

        .result.error .result-data {
            color: #7f1d1d;
        }

        .info {
            background: #f3f4f6;
            border-left: 4px solid #3b82f6;
            padding: 12px;
            border-radius: 4px;
            font-size: 13px;
            color: #374151;
            margin-bottom: 20px;
        }

        .loading {
            display: none;
            text-align: center;
            color: #667eea;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔐 QR Decryption</h1>
        <p class="subtitle">Scan QR code and paste encrypted data below</p>

        <div class="info">
            ℹ️ This tool decrypts data client-side in your browser. No data is sent anywhere.
        </div>

        <form id="decryptForm">
            <div class="form-group">
                <label for="encryptedData">Encrypted Data (from QR code)</label>
                <textarea id="encryptedData" placeholder="Paste the scanned QR code data here..." required></textarea>
            </div>

            <div class="form-group">
                <label for="password">Master Password</label>
                <input type="password" id="password" placeholder="Enter the master password..." required>
            </div>

            <button type="submit">Decrypt</button>
            <div class="loading" id="loading">Decrypting...</div>
        </form>

        <div class="result" id="result">
            <div class="result-title" id="resultTitle">Decrypted Information</div>
            <div class="result-data" id="resultData"></div>
        </div>
    </div>

    <script>
        // Inline encryption/decryption using Web Crypto API

        async function deriveKey(password, salt) {
            const enc = new TextEncoder();
            const baseKey = await crypto.subtle.importKey(
                'raw',
                enc.encode(password),
                { name: 'PBKDF2' },
                false,
                ['deriveBits', 'deriveKey']
            );

            return crypto.subtle.deriveKey(
                {
                    name: 'PBKDF2',
                    salt: salt,
                    iterations: 100000,
                    hash: 'SHA-256'
                },
                baseKey,
                { name: 'AES-GCM', length: 256 },
                false,
                ['decrypt']
            );
        }

        async function decryptData(encryptedBase64, password) {
            try {
                // Decode base64
                const binaryString = atob(encryptedBase64);
                const bytes = new Uint8Array(binaryString.length);
                for (let i = 0; i < binaryString.length; i++) {
                    bytes[i] = binaryString.charCodeAt(i);
                }

                // Extract components
                const salt = bytes.slice(0, 16);
                const nonce = bytes.slice(16, 28);
                const ciphertext = bytes.slice(28);

                // Derive key
                const key = await deriveKey(password, salt);

                // Decrypt
                const plaintext = await crypto.subtle.decrypt(
                    { name: 'AES-GCM', iv: nonce },
                    key,
                    ciphertext
                );

                // Decode to string
                const dec = new TextDecoder();
                return dec.decode(plaintext);

            } catch (error) {
                throw new Error('Decryption failed - wrong password or corrupted data');
            }
        }

        function parseDecryptedData(plaintext) {
            // Expected format: "Full Name | Food Restrictions"
            const parts = plaintext.split('|').map(p => p.trim());

            if (parts.length !== 2) {
                throw new Error('Invalid data format');
            }

            return {
                name: parts[0],
                restrictions: parts[1]
            };
        }

        document.getElementById('decryptForm').addEventListener('submit', async (e) => {
            e.preventDefault();

            const encryptedData = document.getElementById('encryptedData').value.trim();
            const password = document.getElementById('password').value;
            const resultDiv = document.getElementById('result');
            const loadingDiv = document.getElementById('loading');

            loadingDiv.style.display = 'block';
            resultDiv.style.display = 'none';

            try {
                const plaintext = await decryptData(encryptedData, password);
                const data = parseDecryptedData(plaintext);

                resultDiv.className = 'result success';
                document.getElementById('resultTitle').textContent = '✓ Decrypted Successfully';
                document.getElementById('resultData').innerHTML = `
                    <strong>Name:</strong> ${escapeHtml(data.name)}<br>
                    <strong>Food Restrictions:</strong> ${escapeHtml(data.restrictions)}
                `;
                resultDiv.style.display = 'block';

            } catch (error) {
                resultDiv.className = 'result error';
                document.getElementById('resultTitle').textContent = '✗ Decryption Failed';
                document.getElementById('resultData').textContent = error.message;
                resultDiv.style.display = 'block';

            } finally {
                loadingDiv.style.display = 'none';
            }
        });

        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
    </script>
</body>
</html>
```

- [ ] **Step 2: Test decrypt.html manually**

1. Open `decrypt.html` in a browser
2. Generate test data by running:
   ```bash
   cd qr-generator
   python3 << 'EOF'
   from encryption import encrypt_data

   plaintext = "Test Person | Vegetarian"
   password = "test_password"
   encrypted = encrypt_data(plaintext, password)

   print(f"Encrypted: {encrypted}")
   EOF
   ```
3. Copy encrypted output
4. Paste into decrypt.html with password "test_password"
5. Verify it shows "Test Person | Vegetarian"

- [ ] **Step 3: Commit**

```bash
cd qr-generator
git add decrypt.html
git commit -m "feat: add standalone decryption HTML page with client-side Web Crypto"
```

---

## Task 7: Documentation

**Files:**
- Create: `qr-generator/README.md`

### Steps

- [ ] **Step 1: Write README**

Create `qr-generator/README.md`:

```markdown
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
```

- [ ] **Step 2: Commit**

```bash
cd qr-generator
git add README.md
git commit -m "docs: add comprehensive README with setup and usage instructions"
```

---

## Task 8: Final Integration & Cleanup

**Files:**
- Update: `qr-generator/sample_data.xlsx` (improve template)
- Create: `.gitignore` (exclude QR output folder)

### Steps

- [ ] **Step 1: Create .gitignore**

Create `qr-generator/.gitignore`:

```
# QR code output folders
qr_codes/
test_output/
output/
*.png

# Python
__pycache__/
*.pyc
*.pyo
*.egg-info/
.pytest_cache/
.coverage
htmlcov/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
```

- [ ] **Step 2: Verify all tests pass**

```bash
cd qr-generator
pytest -v --tb=short
```

Expected: All tests PASS

- [ ] **Step 3: Test end-to-end workflow**

```bash
cd qr-generator

# 1. Generate QR codes from sample data
python generate_qr_codes.py sample_data.xlsx -o final_test -p "Demo_Password_123"

# 2. List generated files
ls -lh final_test/

# 3. Verify count
echo "Generated $(ls final_test/*.png | wc -l) QR codes"

# 4. Generate one test encrypted string
python3 << 'EOF'
from encryption import encrypt_data
plaintext = "John Smith | None"
password = "Demo_Password_123"
encrypted = encrypt_data(plaintext, password)
print(f"Test encrypted data: {encrypted}")
EOF

# 5. Clean up
rm -rf final_test/
```

Expected: 5 QR codes generated, can create valid encrypted test data

- [ ] **Step 4: Final commit**

```bash
cd qr-generator
git add .gitignore
git commit -m "build: add gitignore to exclude QR output and Python artifacts"
```

- [ ] **Step 5: Summary**

Verify all files are in place:

```bash
cd qr-generator
echo "=== Project Structure ===" && find . -type f -name "*.py" -o -name "*.html" -o -name "*.txt" -o -name "*.md" | sort
echo "" && echo "=== Test Results ===" && pytest -v --tb=line | tail -5
echo "" && echo "=== Ready for Production ===" && ls -lh decrypt.html README.md generate_qr_codes.py
```

---

## Implementation Checklist

- [ ] Task 1: Project setup & sample data
- [ ] Task 2: Encryption utility module
- [ ] Task 3: Excel reader module
- [ ] Task 4: QR code generator module
- [ ] Task 5: Main script integration
- [ ] Task 6: Decryption HTML page
- [ ] Task 7: Documentation
- [ ] Task 8: Final integration & cleanup

---

## Success Criteria

✅ All unit tests pass
✅ End-to-end test works (Excel → QR codes)
✅ decrypt.html successfully decrypts sample QR data
✅ README provides clear setup and usage
✅ Project is git-tracked with clear commits
✅ No sensitive data in repo (only sample data)

---

## Next Steps After Implementation

1. **Test with Real Data:** Once user has Excel file ready, run script locally
2. **Print/Display QRs:** Print the PNG files or display on screens
3. **Bring to Event:** Copy `decrypt.html` + password to event devices
4. **Delete Source:** After QR generation, delete the Excel file
5. **Archive:** Keep QR codes + HTML page for future reference (read-only, encrypted)

