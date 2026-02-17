"""
Test Suite for Parser Modules

Tests JSON and CSV parsers.
"""

import unittest
import sys
import os
import json

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.parsers.json_parser import JSONParser
from src.parsers.csv_parser import CSVParser
from src.parsers.parser_factory import create_parser
from src.core.data_validator import FileFormat
from src.utils.type_detector import DataType


class TestJSONParser(unittest.TestCase):
    """Test cases for JSON parser"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.parser = JSONParser()
        self.test_data_dir = os.path.join(os.path.dirname(__file__), 'test_data')
        self.json_file = os.path.join(self.test_data_dir, 'sample_cybersecurity.json')
    
    def test_parse_json_file(self):
        """Test parsing a JSON file"""
        parsed = self.parser.parse(self.json_file)
        
        # Check basic properties
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed.file_format, 'json')
        self.assertGreater(parsed.get_record_count(), 0)
    
    def test_json_records_extraction(self):
        """Test that records are extracted correctly"""
        parsed = self.parser.parse(self.json_file)
        records = parsed.get_records()
        
        # Should have records from all collections
        self.assertGreater(len(records), 0)
        
        # Check that entity types are preserved
        entity_types = set(r.get('_entity_type') for r in records if '_entity_type' in r)
        self.assertGreater(len(entity_types), 0)
    
    def test_json_field_detection(self):
        """Test field detection in JSON"""
        parsed = self.parser.parse(self.json_file)
        fields = parsed.get_fields()
        
        # Should have detected fields
        self.assertGreater(len(fields), 0)
    
    def test_json_type_detection(self):
        """Test data type detection in JSON"""
        parsed = self.parser.parse(self.json_file)
        
        # Get some field types (may vary based on structure)
        fields = parsed.get_fields()
        for field in fields:
            field_type = parsed.get_field_type(field)
            self.assertIsNotNone(field_type)
    
    def test_json_hierarchy_detection(self):
        """Test hierarchy detection in JSON"""
        parsed = self.parser.parse(self.json_file)
        hierarchy = parsed.get_hierarchy()
        
        # Should detect some hierarchy (collections)
        self.assertIsInstance(hierarchy, dict)
    
    def test_json_flatten_simple_object(self):
        """Test flattening a simple object"""
        simple_obj = {"name": "John", "age": 30}
        records = self.parser._extract_records(simple_obj)
        
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]['name'], "John")
        self.assertEqual(records[0]['age'], 30)
    
    def test_json_flatten_nested_object(self):
        """Test flattening a nested object"""
        nested_obj = {
            "user": {
                "name": "John",
                "details": {
                    "age": 30,
                    "city": "NYC"
                }
            }
        }
        records = self.parser._extract_records(nested_obj)
        
        # Should flatten nested structure
        self.assertEqual(len(records), 1)
        # Check for flattened keys
        self.assertIn('user_name', records[0])
        self.assertIn('user_details_age', records[0])


class TestCSVParser(unittest.TestCase):
    """Test cases for CSV parser"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.parser = CSVParser()
        self.test_data_dir = os.path.join(os.path.dirname(__file__), 'test_data')
        self.csv_file = os.path.join(self.test_data_dir, 'sample_users.csv')
    
    def test_parse_csv_file(self):
        """Test parsing a CSV file"""
        parsed = self.parser.parse(self.csv_file)
        
        # Check basic properties
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed.file_format, 'csv')
        self.assertGreater(parsed.get_record_count(), 0)
    
    def test_csv_records_extraction(self):
        """Test that CSV records are extracted correctly"""
        parsed = self.parser.parse(self.csv_file)
        records = parsed.get_records()
        
        # Should have records matching CSV rows (excluding header)
        self.assertGreater(len(records), 0)
        
        # Each record should be a dictionary
        for record in records:
            self.assertIsInstance(record, dict)
    
    def test_csv_field_detection(self):
        """Test field detection in CSV"""
        parsed = self.parser.parse(self.csv_file)
        fields = parsed.get_fields()
        
        # Should match CSV columns
        expected_fields = ['user_id', 'user_name', 'user_email', 'user_role', 'login_ip', 'device_id']
        for expected in expected_fields:
            self.assertIn(expected, fields)
    
    def test_csv_type_detection(self):
        """Test data type detection in CSV"""
        parsed = self.parser.parse(self.csv_file)
        
        # Check some expected types
        user_id_type = parsed.get_field_type('user_id')
        self.assertIsNotNone(user_id_type)
        
        user_email_type = parsed.get_field_type('user_email')
        self.assertIsNotNone(user_email_type)
    
    def test_csv_no_hierarchy(self):
        """Test that CSV has no hierarchy (flat structure)"""
        parsed = self.parser.parse(self.csv_file)
        hierarchy = parsed.get_hierarchy()
        
        # CSV is flat, should have empty hierarchy
        self.assertEqual(len(hierarchy), 0)


class TestParserFactory(unittest.TestCase):
    """Test cases for parser factory"""
    
    def test_create_json_parser(self):
        """Test creating JSON parser"""
        parser = create_parser(FileFormat.JSON)
        self.assertIsInstance(parser, JSONParser)
    
    def test_create_csv_parser(self):
        """Test creating CSV parser"""
        parser = create_parser(FileFormat.CSV)
        self.assertIsInstance(parser, CSVParser)
    
    def test_unsupported_format(self):
        """Test error handling for unsupported format"""
        with self.assertRaises(ValueError):
            create_parser(FileFormat.UNKNOWN)


class TestParsedData(unittest.TestCase):
    """Test cases for ParsedData structure"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_data_dir = os.path.join(os.path.dirname(__file__), 'test_data')
        self.csv_file = os.path.join(self.test_data_dir, 'sample_users.csv')
    
    def test_parsed_data_methods(self):
        """Test ParsedData query methods"""
        parser = CSVParser()
        parsed = parser.parse(self.csv_file)
        
        # Test get_fields
        fields = parsed.get_fields()
        self.assertIsInstance(fields, list)
        self.assertGreater(len(fields), 0)
        
        # Test get_records
        records = parsed.get_records()
        self.assertIsInstance(records, list)
        
        # Test preview
        preview = parsed.preview(3)
        self.assertLessEqual(len(preview), 3)
        
        # Test summary
        summary = parsed.summary()
        self.assertIsInstance(summary, str)
        self.assertIn('Records:', summary)
    
    def test_parsed_data_to_dict(self):
        """Test converting ParsedData to dictionary"""
        parser = CSVParser()
        parsed = parser.parse(self.csv_file)
        
        data_dict = parsed.to_dict()
        self.assertIsInstance(data_dict, dict)
        self.assertIn('source_file', data_dict)
        self.assertIn('file_format', data_dict)
        self.assertIn('records', data_dict)
        self.assertIn('fields', data_dict)


if __name__ == '__main__':
    unittest.main()
