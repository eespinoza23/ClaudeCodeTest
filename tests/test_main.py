import pytest
from pathlib import Path
import shutil
import os
import tempfile


class TestMainScript:
    def test_main_script_generates_qr_files(self):
        """Integration test: script should generate QR files from Excel"""
        from generate_qr_codes import main

        # Use sample data
        excel_file = 'sample_data.xlsx'
        output_dir = os.path.join(tempfile.gettempdir(), 'test_qr_output')
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
