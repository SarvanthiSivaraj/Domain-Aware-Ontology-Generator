"""
Demo script for Step 2 - Format Detection and Parsing

Demonstrates parsing JSON and CSV files.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.parsers.json_parser import JSONParser
from src.parsers.csv_parser import CSVParser
from src.core.data_validator import validate_input_file


def demo_json_parsing():
    """Demo JSON parsing"""
    print("=" * 60)
    print("JSON PARSING DEMO")
    print("=" * 60)
    
    json_file = "tests/test_data/sample_cybersecurity.json"
    
    # Validate first
    is_valid, file_format, errors = validate_input_file(json_file)
    if not is_valid:
        print(f"❌ Validation failed: {errors}")
        return
    
    print(f"✅ File validated: {file_format.value.upper()}\n")
    
    # Parse
    parser = JSONParser()
    parsed = parser.parse(json_file)
    
    # Display summary
    print(parsed.summary())
    print("\n" + "-" * 60)
    
    # Show sample records
    print("\nSample Records (first 3):")
    for i, record in enumerate(parsed.preview(3), 1):
        print(f"\nRecord {i}:")
        for key, value in list(record.items())[:5]:  # Show first 5 fields
            print(f"  {key}: {value}")
        if len(record) > 5:
            print(f"  ... and {len(record) - 5} more fields")
    
    print("\n" + "=" * 60)


def demo_csv_parsing():
    """Demo CSV parsing"""
    print("\n" * 2)
    print("=" * 60)
    print("CSV PARSING DEMO")
    print("=" * 60)
    
    csv_file = "tests/test_data/sample_users.csv"
    
    # Validate first
    is_valid, file_format, errors = validate_input_file(csv_file)
    if not is_valid:
        print(f"❌ Validation failed: {errors}")
        return
    
    print(f"✅ File validated: {file_format.value.upper()}\n")
    
    # Parse
    parser = CSVParser()
    parsed = parser.parse(csv_file)
    
    # Display summary
    print(parsed.summary())
    print("\n" + "-" * 60)
    
    # Show field types
    print("\nField Type Analysis:")
    for field in parsed.get_fields():
        field_type = parsed.get_field_type(field)
        metadata = parsed.get_field_metadata(field)
        nullable = " (nullable)" if metadata.nullable else ""
        print(f"  {field}: {field_type}{nullable}")
    
    print("\n" + "-" * 60)
    
    # Show sample records
    print("\nSample Records (all):")
    for i, record in enumerate(parsed.preview(10), 1):
        print(f"\nRecord {i}:")
        for key, value in record.items():
            print(f"  {key}: {value}")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    demo_json_parsing()
    demo_csv_parsing()
    
    print("\n\n🎉 Step 2 - Format Detection and Parsing is working!\n")
