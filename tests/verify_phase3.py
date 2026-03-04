import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.parsers.json_parser import JSONParser
from src.parsers.csv_parser import CSVParser

def verify():
    print("Verifying JSON Schema Analysis...")
    json_parser = JSONParser()
    json_data = json_parser.parse("tests/test_data/sample_cybersecurity.json")
    
    # Check for identifiers
    id_fields = [f for f, m in json_data.field_metadata.items() if m.is_identifier]
    print(f"Detected ID fields: {', '.join(id_fields)}")
    
    # Check for prefixes
    prefixes = set(m.prefix for m in json_data.field_metadata.values() if m.prefix)
    print(f"Detected Prefixes: {', '.join(filter(None, prefixes))}")
    
    print("\nVerifying CSV Schema Analysis...")
    csv_parser = CSVParser()
    csv_data = csv_parser.parse("tests/test_data/sample_users.csv")
    
    # Check for identifiers
    id_fields = [f for f, m in csv_data.field_metadata.items() if m.is_identifier]
    print(f"Detected ID fields: {', '.join(id_fields)}")
    
    # Check for prefixes
    prefixes = set(m.prefix for m in csv_data.field_metadata.values() if m.prefix)
    print(f"Detected Prefixes: {', '.join(filter(None, prefixes))}")

if __name__ == "__main__":
    verify()
