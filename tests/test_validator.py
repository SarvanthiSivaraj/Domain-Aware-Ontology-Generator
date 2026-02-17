"""
Test Suite for Data Validator Module

Tests file validation, format detection, and error handling.
"""

import unittest
import os
import json
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.data_validator import DataValidator, FileFormat, validate_input_file


class TestDataValidator(unittest.TestCase):
    """Test cases for DataValidator class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.validator = DataValidator()
        self.test_data_dir = os.path.join(os.path.dirname(__file__), 'test_data')
        
        # Sample file paths
        self.json_file = os.path.join(self.test_data_dir, 'sample_cybersecurity.json')
        self.csv_file = os.path.join(self.test_data_dir, 'sample_users.csv')
    
    def test_valid_json_file(self):
        """Test validation of a valid JSON file"""
        is_valid, file_format, errors = self.validator.validate_file(self.json_file)
        
        self.assertTrue(is_valid)
        self.assertEqual(file_format, FileFormat.JSON)
        self.assertEqual(len(errors), 0)
    
    def test_valid_csv_file(self):
        """Test validation of a valid CSV file"""
        is_valid, file_format, errors = self.validator.validate_file(self.csv_file)
        
        self.assertTrue(is_valid)
        self.assertEqual(file_format, FileFormat.CSV)
        self.assertEqual(len(errors), 0)
    
    def test_nonexistent_file(self):
        """Test validation of non-existent file"""
        fake_file = "nonexistent_file.json"
        is_valid, file_format, errors = self.validator.validate_file(fake_file)
        
        self.assertFalse(is_valid)
        self.assertEqual(file_format, FileFormat.UNKNOWN)
        self.assertGreater(len(errors), 0)
        self.assertIn("not found", errors[0].lower())
    
    def test_unsupported_format(self):
        """Test validation of unsupported file format"""
        # Create a temporary .txt file
        temp_file = os.path.join(self.test_data_dir, 'test.txt')
        with open(temp_file, 'w') as f:
            f.write("test data")
        
        try:
            is_valid, file_format, errors = self.validator.validate_file(temp_file)
            
            self.assertFalse(is_valid)
            self.assertEqual(file_format, FileFormat.UNKNOWN)
            self.assertGreater(len(errors), 0)
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)
    
    def test_convenience_function(self):
        """Test the convenience validation function"""
        is_valid, file_format, errors = validate_input_file(self.json_file)
        
        self.assertTrue(is_valid)
        self.assertEqual(file_format, FileFormat.JSON)


if __name__ == '__main__':
    # Run tests
    unittest.main()
