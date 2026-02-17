"""
JSON Parser Module

Parses JSON files into structured data with hierarchy detection.
"""

import json
from typing import Dict, Any, List, Set
from collections import defaultdict
from src.parsers.base_parser import BaseParser
from src.core.parsed_data import ParsedData, FieldMetadata
from src.utils.type_detector import analyze_field_types, DataType


class JSONParser(BaseParser):
    """
    Parser for JSON files.
    
    Features:
    - Parses nested JSON structures
    - Flattens data while preserving hierarchy information
    - Detects field types automatically
    - Handles both single objects and arrays
    """
    
    def __init__(self):
        """Initialize the JSON parser"""
        self.hierarchy_map = {}
    
    def parse(self, file_path: str) -> ParsedData:
        """
        Parse a JSON file.
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            ParsedData: Parsed data with metadata
        """
        # Load JSON file
        with open(file_path, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
        
        # Create ParsedData object
        parsed_data = ParsedData(source_file=file_path, file_format='json')
        
        # Extract records and hierarchy
        records = self._extract_records(raw_data)
        parsed_data.set_records(records)
        
        # Detect schema
        schema = self.detect_schema(records)
        parsed_data.set_field_metadata(schema['field_metadata'])
        parsed_data.set_hierarchy(schema['hierarchy'])
        
        return parsed_data
    
    def _extract_records(self, data: Any) -> List[Dict[str, Any]]:
        """
        Extract records from JSON data.
        
        Handles:
        - Single object: returns as single-item list
        - Array of objects: returns as list
        - Nested structures: flattens and combines
        
        Args:
            data: Raw JSON data (dict or list)
            
        Returns:
            List of record dictionaries
        """
        self.hierarchy_map = {}
        
        if isinstance(data, list):
            # Array of objects
            return self._flatten_records(data)
        elif isinstance(data, dict):
            # Check if it's a collection of arrays (like our cybersecurity example)
            if self._is_collection_dict(data):
                return self._flatten_collection_dict(data)
            else:
                # Single object
                return [self._flatten_object(data)]
        else:
            # Primitive value - wrap it
            return [{'value': data}]
    
    def _is_collection_dict(self, data: dict) -> bool:
        """
        Check if dictionary contains collections (arrays) as values.
        
        Args:
            data: Dictionary to check
            
        Returns:
            bool: True if it's a collection dictionary
        """
        # If most values are lists, it's likely a collection dict
        list_count = sum(1 for v in data.values() if isinstance(v, list))
        return list_count > 0 and list_count >= len(data) * 0.5
    
    def _flatten_collection_dict(self, data: dict) -> List[Dict[str, Any]]:
        """
        Flatten a dictionary containing collections.
        
        For example, {"users": [...], "devices": [...]}
        Each collection becomes records with a type indicator.
        
        Args:
            data: Dictionary with array values
            
        Returns:
            List of flattened records
        """
        all_records = []
        
        for collection_name, collection_data in data.items():
            if isinstance(collection_data, list):
                # Track hierarchy
                self.hierarchy_map[collection_name] = len(collection_data)
                
                # Flatten each item in the collection
                for item in collection_data:
                    if isinstance(item, dict):
                        flattened = self._flatten_object(item, prefix=f"{collection_name}_")
                        flattened['_entity_type'] = collection_name
                        all_records.append(flattened)
                    else:
                        all_records.append({
                            '_entity_type': collection_name,
                            'value': item
                        })
        
        return all_records
    
    def _flatten_records(self, records: List[Any]) -> List[Dict[str, Any]]:
        """
        Flatten a list of records.
        
        Args:
            records: List of objects
            
        Returns:
            List of flattened dictionaries
        """
        flattened = []
        for record in records:
            if isinstance(record, dict):
                flattened.append(self._flatten_object(record))
            else:
                flattened.append({'value': record})
        return flattened
    
    def _flatten_object(self, obj: dict, prefix: str = '', max_depth: int = 3, current_depth: int = 0) -> Dict[str, Any]:
        """
        Flatten a nested object into a single-level dictionary.
        
        Args:
            obj: Object to flatten
            prefix: Prefix for flattened keys
            max_depth: Maximum nesting depth to flatten
            current_depth: Current recursion depth
            
        Returns:
            Flattened dictionary
        """
        flattened = {}
        
        for key, value in obj.items():
            new_key = f"{prefix}{key}" if prefix else key
            
            if isinstance(value, dict) and current_depth < max_depth:
                # Recursively flatten nested dict
                nested = self._flatten_object(value, prefix=f"{new_key}_", 
                                             max_depth=max_depth, 
                                             current_depth=current_depth + 1)
                flattened.update(nested)
            elif isinstance(value, list) and len(value) > 0 and isinstance(value[0], dict):
                # For lists of objects, store as JSON string or take first item
                # This maintains some structure without over-flattening
                flattened[new_key] = json.dumps(value)
            elif isinstance(value, list):
                # Simple list - convert to comma-separated or JSON
                if all(isinstance(v, (str, int, float, bool)) for v in value):
                    flattened[new_key] = ', '.join(str(v) for v in value)
                else:
                    flattened[new_key] = json.dumps(value)
            else:
                # Primitive value
                flattened[new_key] = value
        
        return flattened
    
    def detect_schema(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Detect schema from parsed records.
        
        Args:
            records: List of record dictionaries
            
        Returns:
            dict: Schema information
        """
        if not records:
            return {'field_metadata': {}, 'hierarchy': {}}
        
        # Analyze field types
        field_types = analyze_field_types(records)
        
        # Create field metadata
        field_metadata = {}
        all_fields = set()
        for record in records:
            all_fields.update(record.keys())
        
        for field_name in all_fields:
            # Collect field values
            values = [record.get(field_name) for record in records]
            non_null_values = [v for v in values if v is not None]
            
            # Get unique values (limited sample)
            unique_values = list(set(non_null_values))[:5]
            
            metadata = FieldMetadata(
                name=field_name,
                data_type=field_types.get(field_name, DataType.UNKNOWN).value,
                nullable=(len(non_null_values) < len(values)),
                null_count=len(values) - len(non_null_values),
                unique_count=len(set(str(v) for v in non_null_values)),
                sample_values=unique_values
            )
            field_metadata[field_name] = metadata
        
        return {
            'field_metadata': field_metadata,
            'hierarchy': self.hierarchy_map
        }
