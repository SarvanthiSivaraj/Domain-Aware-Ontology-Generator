"""
Test Suite for Data Validator Module

Tests file validation, format detection, and error handling.
"""

import unittest
import os
import json
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.core.validator import FileValidator
from src.core.detector import FormatDetector, FileFormat


class TestFileValidator(unittest.TestCase):
    """Test cases for FileValidator class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.validator = FileValidator()
        self.test_data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data'))
        
        # Sample file paths
        self.json_file = os.path.join(self.test_data_dir, 'sample_cybersecurity.json')
        self.csv_file = os.path.join(self.test_data_dir, 'sample_users.csv')
    
    def test_valid_json_file(self):
        """Test validation of a valid JSON file"""
        result = self.validator.validate(self.json_file)
        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.errors), 0)
        
        fmt = FormatDetector.detect(self.json_file)
        self.assertEqual(fmt, FileFormat.JSON)
    
    def test_valid_csv_file(self):
        """Test validation of a valid CSV file"""
        result = self.validator.validate(self.csv_file)
        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.errors), 0)
        
        fmt = FormatDetector.detect(self.csv_file)
        self.assertEqual(fmt, FileFormat.CSV)
    
    def test_nonexistent_file(self):
        """Test validation of non-existent file"""
        fake_file = "nonexistent_file.json"
        result = self.validator.validate(fake_file)
        
        self.assertFalse(result.is_valid)
        self.assertGreater(len(result.errors), 0)
        self.assertIn("not found", result.errors[0].lower())
    
    def test_unsupported_format(self):
        """Test detection of unsupported file format"""
        # Create a temporary .txt file
        temp_file = os.path.join(self.test_data_dir, 'test.txt')
        with open(temp_file, 'w') as f:
            f.write("test data")
        
        try:
            fmt = FormatDetector.detect(temp_file)
            self.assertEqual(fmt, FileFormat.UNKNOWN)
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)


if __name__ == '__main__':
    # Run tests
    unittest.main()
