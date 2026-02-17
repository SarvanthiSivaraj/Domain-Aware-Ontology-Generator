"""
Test Suite for Type Detector Module

Tests data type detection and inference functionality.
"""

import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils.type_detector import (
    DataType, 
    infer_type, 
    infer_column_type, 
    detect_date_format,
    analyze_field_types
)


class TestTypeDetector(unittest.TestCase):
    """Test cases for type detection"""
    
    def test_integer_detection(self):
        """Test integer type detection"""
        self.assertEqual(infer_type(42), DataType.INTEGER)
        self.assertEqual(infer_type("123"), DataType.INTEGER)
        self.assertEqual(infer_type("0"), DataType.INTEGER)
        self.assertEqual(infer_type("-456"), DataType.INTEGER)
    
    def test_float_detection(self):
        """Test float type detection"""
        self.assertEqual(infer_type(3.14), DataType.FLOAT)
        self.assertEqual(infer_type("3.14"), DataType.FLOAT)
        self.assertEqual(infer_type("0.001"), DataType.FLOAT)
        self.assertEqual(infer_type("-2.5"), DataType.FLOAT)
        self.assertEqual(infer_type("1.5e10"), DataType.FLOAT)
    
    def test_boolean_detection(self):
        """Test boolean type detection"""
        self.assertEqual(infer_type(True), DataType.BOOLEAN)
        self.assertEqual(infer_type(False), DataType.BOOLEAN)
        self.assertEqual(infer_type("true"), DataType.BOOLEAN)
        self.assertEqual(infer_type("false"), DataType.BOOLEAN)
        self.assertEqual(infer_type("TRUE"), DataType.BOOLEAN)
        self.assertEqual(infer_type("yes"), DataType.BOOLEAN)
        self.assertEqual(infer_type("no"), DataType.BOOLEAN)
    
    def test_string_detection(self):
        """Test string type detection"""
        self.assertEqual(infer_type("hello"), DataType.STRING)
        self.assertEqual(infer_type("test123"), DataType.STRING)
        self.assertEqual(infer_type("user@email.com"), DataType.STRING)
    
    def test_null_detection(self):
        """Test null type detection"""
        self.assertEqual(infer_type(None), DataType.NULL)
        self.assertEqual(infer_type(""), DataType.NULL)
        self.assertEqual(infer_type("  "), DataType.NULL)
        self.assertEqual(infer_type("null"), DataType.NULL)
        self.assertEqual(infer_type("NULL"), DataType.NULL)
        self.assertEqual(infer_type("N/A"), DataType.NULL)
        self.assertEqual(infer_type("NA"), DataType.NULL)
    
    def test_datetime_detection(self):
        """Test datetime type detection"""
        self.assertEqual(infer_type("2024-01-15T09:30:00Z"), DataType.DATETIME)
        self.assertEqual(infer_type("2024-01-15 09:30:00"), DataType.DATETIME)
        self.assertEqual(infer_type("2024-01-15"), DataType.DATETIME)
        self.assertEqual(infer_type("15/01/2024"), DataType.DATETIME)
    
    def test_datetime_format_detection(self):
        """Test datetime format detection"""
        fmt = detect_date_format("2024-01-15T09:30:00Z")
        self.assertEqual(fmt, "%Y-%m-%dT%H:%M:%SZ")
        
        fmt = detect_date_format("2024-01-15")
        self.assertEqual(fmt, "%Y-%m-%d")
    
    def test_column_type_inference_uniform(self):
        """Test column type inference with uniform types"""
        # All integers
        values = [1, 2, 3, 4, 5]
        self.assertEqual(infer_column_type(values), DataType.INTEGER)
        
        # All strings
        values = ["a", "b", "c"]
        self.assertEqual(infer_column_type(values), DataType.STRING)
    
    def test_column_type_inference_with_nulls(self):
        """Test column type inference with null values"""
        values = [1, 2, None, 4, 5]
        self.assertEqual(infer_column_type(values), DataType.INTEGER)
        
        values = ["a", "b", "", "d"]
        self.assertEqual(infer_column_type(values), DataType.STRING)
    
    def test_column_type_inference_mixed(self):
        """Test column type inference with mixed types"""
        # Mix of int and float -> should be float
        values = [1, 2.5, 3, 4.0]
        self.assertEqual(infer_column_type(values), DataType.FLOAT)
        
        # Mix of different types -> should default to string
        values = [1, "text", True]
        result = infer_column_type(values, threshold=0.5)
        self.assertIn(result, [DataType.STRING, DataType.INTEGER])
    
    def test_analyze_field_types(self):
        """Test field type analysis across records"""
        records = [
            {"id": "1", "age": 25, "active": True, "joined": "2024-01-15"},
            {"id": "2", "age": 30, "active": False, "joined": "2024-02-20"},
            {"id": "3", "age": 28, "active": True, "joined": "2024-03-10"}
        ]
        
        field_types = analyze_field_types(records)
        
        self.assertEqual(field_types['id'], DataType.STRING)
        self.assertEqual(field_types['age'], DataType.INTEGER)
        self.assertEqual(field_types['active'], DataType.BOOLEAN)
        self.assertEqual(field_types['joined'], DataType.DATETIME)
    
    def test_edge_cases(self):
        """Test edge cases"""
        # Empty string after stripping
        self.assertEqual(infer_type("   "), DataType.NULL)
        
        # "0" and "1" should be integers
        self.assertEqual(infer_type("0"), DataType.INTEGER)
        self.assertEqual(infer_type("1"), DataType.INTEGER)
        
        # Scientific notation
        self.assertEqual(infer_type("1e5"), DataType.FLOAT)


if __name__ == '__main__':
    unittest.main()
