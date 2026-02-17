"""
Parsed Data Structure Module

Provides a unified data structure for storing parsed data with metadata.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from collections import Counter
import json


@dataclass
class FieldMetadata:
    """Metadata for a single field"""
    name: str
    data_type: str
    nullable: bool = True
    null_count: int = 0
    unique_count: int = 0
    sample_values: List[Any] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'name': self.name,
            'type': self.data_type,
            'nullable': self.nullable,
            'null_count': self.null_count,
            'unique_count': self.unique_count,
            'sample_values': self.sample_values[:5]  # Limit samples
        }


class ParsedData:
    """
    Unified data structure for parsed data with metadata.
    
    Stores:
    - Records (list of dictionaries)
    - Schema metadata (field types, statistics)
    - Hierarchy information (for nested structures)
    """
    
    def __init__(self, source_file: str, file_format: str):
        """
        Initialize ParsedData.
        
        Args:
            source_file: Path to the source file
            file_format: Format of the source file (json/csv)
        """
        self.source_file = source_file
        self.file_format = file_format
        self.records: List[Dict[str, Any]] = []
        self.field_metadata: Dict[str, FieldMetadata] = {}
        self.hierarchy: Dict[str, Any] = {}
        self._record_count = 0
    
    def set_records(self, records: List[Dict[str, Any]]) -> None:
        """
        Set the parsed records.
        
        Args:
            records: List of record dictionaries
        """
        self.records = records
        self._record_count = len(records)
    
    def set_field_metadata(self, field_metadata: Dict[str, FieldMetadata]) -> None:
        """
        Set field metadata.
        
        Args:
            field_metadata: Dictionary mapping field names to metadata
        """
        self.field_metadata = field_metadata
    
    def set_hierarchy(self, hierarchy: Dict[str, Any]) -> None:
        """
        Set hierarchy information.
        
        Args:
            hierarchy: Dictionary describing data hierarchy
        """
        self.hierarchy = hierarchy
    
    def get_records(self) -> List[Dict[str, Any]]:
        """Get all records"""
        return self.records
    
    def get_fields(self) -> List[str]:
        """Get list of all field names"""
        return list(self.field_metadata.keys())
    
    def get_field_type(self, field_name: str) -> Optional[str]:
        """
        Get the data type of a field.
        
        Args:
            field_name: Name of the field
            
        Returns:
            str: Data type, or None if field doesn't exist
        """
        metadata = self.field_metadata.get(field_name)
        return metadata.data_type if metadata else None
    
    def get_field_metadata(self, field_name: str) -> Optional[FieldMetadata]:
        """
        Get metadata for a field.
        
        Args:
            field_name: Name of the field
            
        Returns:
            FieldMetadata: Field metadata, or None if field doesn't exist
        """
        return self.field_metadata.get(field_name)
    
    def get_hierarchy(self) -> Dict[str, Any]:
        """Get hierarchy information"""
        return self.hierarchy
    
    def get_record_count(self) -> int:
        """Get total number of records"""
        return self._record_count
    
    def preview(self, n: int = 5) -> List[Dict[str, Any]]:
        """
        Get first n records.
        
        Args:
            n: Number of records to return
            
        Returns:
            List of first n records
        """
        return self.records[:n]
    
    def summary(self) -> str:
        """
        Get a human-readable summary of the parsed data.
        
        Returns:
            str: Summary text
        """
        lines = []
        lines.append(f"=== Parsed Data Summary ===")
        lines.append(f"Source: {self.source_file}")
        lines.append(f"Format: {self.file_format.upper()}")
        lines.append(f"Records: {self._record_count}")
        lines.append(f"Fields: {len(self.field_metadata)}")
        lines.append("")
        
        if self.field_metadata:
            lines.append("Field Types:")
            for field_name, metadata in self.field_metadata.items():
                nullable_str = " (nullable)" if metadata.nullable else ""
                lines.append(f"  - {field_name}: {metadata.data_type}{nullable_str}")
        
        if self.hierarchy:
            lines.append("")
            lines.append(f"Hierarchies detected: {len(self.hierarchy)}")
            for parent, children in self.hierarchy.items():
                lines.append(f"  - {parent} → {children}")
        
        return "\n".join(lines)
    
    def to_dict(self) -> dict:
        """
        Convert ParsedData to dictionary representation.
        
        Returns:
            dict: Dictionary with all data and metadata
        """
        return {
            'source_file': self.source_file,
            'file_format': self.file_format,
            'record_count': self._record_count,
            'fields': {name: meta.to_dict() for name, meta in self.field_metadata.items()},
            'hierarchy': self.hierarchy,
            'records': self.records
        }
    
    def to_json(self, indent: int = 2) -> str:
        """
        Convert to JSON string.
        
        Args:
            indent: JSON indentation level
            
        Returns:
            str: JSON representation
        """
        return json.dumps(self.to_dict(), indent=indent, default=str)
    
    def __repr__(self) -> str:
        """String representation"""
        return f"ParsedData(source={self.source_file}, format={self.file_format}, records={self._record_count}, fields={len(self.field_metadata)})"
