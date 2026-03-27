"""
Extract attendee data from images using OCR and create Excel file
"""

import pytesseract
from PIL import Image
import re
from openpyxl import Workbook
from pathlib import Path
import os
import subprocess

# Configure pytesseract to find tesseract.exe
# Try the actual installed location first, then fallback locations
tesseract_paths = [
    r'C:\Users\learn\AppData\Local\Programs\Tesseract-OCR\tesseract.exe',
    r'C:\Program Files\Tesseract-OCR\tesseract.exe',
    r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
]

tesseract_exe = None
for path in tesseract_paths:
    if Path(path).exists():
        pytesseract.pytesseract.pytesseract_cmd = path
        tesseract_exe = path
        # Also add to PATH environment variable
        tesseract_dir = str(Path(path).parent)
        os.environ['PATH'] = tesseract_dir + os.pathsep + os.environ.get('PATH', '')
        print(f"Found Tesseract at: {path}")
        break
else:
    print("WARNING: Tesseract not found at any standard location")

def extract_text_from_images(image_paths):
    """Extract text from multiple images using OCR"""
    all_text = ""

    for image_path in image_paths:
        print(f"Processing: {image_path}")
        try:
            img = Image.open(image_path)
            # Try pytesseract first
            try:
                text = pytesseract.image_to_string(img, lang='eng')
            except Exception as ptes_err:
                # Fallback: use subprocess directly if tesseract_exe is available
                if tesseract_exe:
                    print(f"  pytesseract failed, trying subprocess directly...")
                    try:
                        result = subprocess.run(
                            [tesseract_exe, str(image_path), 'stdout', '-l', 'eng'],
                            capture_output=True,
                            text=True,
                            timeout=30
                        )
                        text = result.stdout
                        if result.returncode != 0:
                            print(f"  Tesseract stderr: {result.stderr}")
                    except Exception as sub_err:
                        print(f"  Subprocess also failed: {sub_err}")
                        text = ""
                else:
                    raise ptes_err

            all_text += text + "\n"
        except Exception as e:
            print(f"Error processing {image_path}: {e}")

    return all_text

def parse_attendee_data(text):
    """Parse OCR text to extract attendee records"""
    attendees = []
    seen_emails = set()

    # Split by lines
    lines = text.split('\n')

    for line in lines:
        line = line.strip()

        # Skip empty lines and headers
        if not line or 'Email' in line or 'Full Name' in line or '@' not in line:
            continue

        # Look for email pattern (more lenient for OCR errors)
        email_match = re.search(r'([a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', line)

        if email_match:
            email = email_match.group(1)

            # Skip if we've already processed this email
            if email in seen_emails:
                continue
            seen_emails.add(email)

            # Extract everything after the email
            name_part = line[email_match.end():].strip()

            # Split into words to extract name and other info
            words = name_part.split()

            if words:
                # First 1-3 words are usually the name
                # Stop at keywords: Count, No, None, Food, etc.
                name_words = []
                remaining_words = []
                found_keyword = False

                for word in words:
                    if found_keyword or any(kw in word.lower() for kw in ['count', 'no', 'none', 'food', 'vegetarian', 'vegan', 'gluten']):
                        found_keyword = True
                        remaining_words.append(word)
                    else:
                        name_words.append(word)

                name = ' '.join(name_words).strip()
                remaining_text = ' '.join(remaining_words).lower()

                # Sanitize name (remove extra characters from OCR)
                name = re.sub(r'[^a-zA-Z\s\-]', '', name).strip()

                if not name and len(name_words) > 0:
                    # Try just the first name
                    name = name_words[0]

                # Parse restrictions and day info from remaining text
                restrictions = "None"
                if any(word in remaining_text for word in ['vegetarian', 'vegan', 'gluten', 'dairy', 'nut']):
                    # Try to extract the restriction phrase
                    for restriction in ['vegetarian', 'vegan', 'gluten free', 'dairy free', 'nut free']:
                        if restriction.lower() in remaining_text:
                            restrictions = restriction.capitalize()
                            break

                # Default values
                day_one = "Count me in"
                day_two = "Count me in"
                squad = "Squad 1"

                # Look for "no food" patterns
                if 'no food' in remaining_text or 'no ' in remaining_text:
                    day_one = "No food for me"

                if name:  # Only add if we have a name
                    attendees.append([
                        email,
                        name,
                        day_one,
                        day_two,
                        restrictions,
                        squad
                    ])

    return attendees

def create_excel_file(attendees, output_path):
    """Create Excel file from attendee data"""
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

    # Data
    for row_idx, attendee in enumerate(attendees, start=2):
        for col_idx, value in enumerate(attendee, start=1):
            ws.cell(row=row_idx, column=col_idx, value=value)

    wb.save(output_path)
    print(f"Created {output_path} with {len(attendees)} attendees")

def main():
    print("=" * 50)
    print("Attendee Data Extractor (OCR)")
    print("=" * 50)

    # Image paths
    desktop = Path.home() / "Desktop"
    image_paths = [
        desktop / "1.jpeg",
        desktop / "2.jpeg",
        desktop / "3.jpeg",
        desktop / "4.jpeg",
    ]

    # Check if images exist
    existing_images = [p for p in image_paths if p.exists()]
    if not existing_images:
        print("ERROR: No images found on Desktop!")
        return

    print(f"Found {len(existing_images)} images")

    # Extract text
    print("\nExtracting text from images...")
    text = extract_text_from_images(existing_images)

    # Debug: show extracted text length and first 500 chars
    print(f"\nDEBUG: Extracted {len(text)} characters of text")
    if text.strip():
        print("First 500 characters of extracted text:")
        print("-" * 50)
        print(text[:500])
        print("-" * 50)

    # Parse data
    print("Parsing attendee data...")
    attendees = parse_attendee_data(text)

    print(f"\nExtracted {len(attendees)} attendees")

    if attendees:
        print("\nFirst 5 attendees:")
        for attendee in attendees[:5]:
            print(f"  {attendee[0]} - {attendee[1]}")

    # Create Excel
    output_path = Path.cwd() / "qr-generator" / "attendees_extracted.xlsx"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"\nCreating Excel file...")
    create_excel_file(attendees, output_path)

    print("\nDone!")
    print(f"File saved to: {output_path}")

if __name__ == "__main__":
    main()
