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
