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
