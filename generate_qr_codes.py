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
    print(f"Reading Excel file: {excel_file}")
    attendees = read_attendees(excel_file)
    print(f"Found {len(attendees)} attendees")

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    print(f"Output directory: {output_dir}")

    # Process each attendee
    for idx, attendee in enumerate(attendees, start=1):
        name = attendee['name']
        restrictions = attendee['restrictions']

        # Create plaintext payload
        plaintext = f"{name} | {restrictions}"

        # Encrypt
        print(f"Encrypting [{idx}/{len(attendees)}] {name}...", end=' ')
        encrypted = encrypt_data(plaintext, master_password)

        # Generate QR code
        output_path = os.path.join(output_dir, f"{name}.png")
        save_qr_code(encrypted, output_path)
        print(f"Saved to {name}.png")

    print(f"\nDone! Generated {len(attendees)} QR codes in {output_dir}")
    print(f"\nSecurity reminder:")
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
        print(f"Error: {e}")
        exit(1)


if __name__ == '__main__':
    cli()
