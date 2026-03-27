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
        import tempfile

        encrypted_data = "test_data"

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "test_qr.png")

            save_qr_code(encrypted_data, output_path)

            assert os.path.exists(output_path)
            assert os.path.getsize(output_path) > 100

    def test_save_qr_code_creates_directory(self):
        """Should create output directory if it doesn't exist"""
        from qr_generator import save_qr_code
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = os.path.join(tmpdir, "test_qr_dir")
            output_path = os.path.join(output_dir, "test.png")

            save_qr_code("test_data", output_path)

            assert os.path.exists(output_path)
