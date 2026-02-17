"""
Type Detection Module

Automatically detects and classifies data types from raw values.
Supports: string, integer, float, boolean, datetime, and null types.
"""

import re
from datetime import datetime
from enum import Enum
from typing import Any, List, Optional, Dict
from collections import Counter


class DataType(Enum):
    """Enumeration of supported data types"""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATETIME = "datetime"
    NULL = "null"
    UNKNOWN = "unknown"


# Common datetime formats to try
DATETIME_FORMATS = [
    "%Y-%m-%dT%H:%M:%SZ",           # ISO 8601: 2024-01-15T09:30:00Z
    "%Y-%m-%dT%H:%M:%S",             # ISO 8601 without Z
    "%Y-%m-%d %H:%M:%S",             # SQL datetime
    "%Y-%m-%d",                      # Date only
    "%d/%m/%Y",                      # DD/MM/YYYY
    "%m/%d/%Y",                      # MM/DD/YYYY
    "%d-%m-%Y",                      # DD-MM-YYYY
    "%Y/%m/%d",                      # YYYY/MM/DD
]


def infer_type(value: Any) -> DataType:
    """
    Infer the data type of a single value.
    
    Args:
        value: The value to analyze
        
    Returns:
        DataType: The detected data type
    """
    # Handle None/null
    if value is None or (isinstance(value, str) and value.strip() == ''):
        return DataType.NULL
    
    # Handle Python native types first
    if isinstance(value, bool):
        return DataType.BOOLEAN
    if isinstance(value, int):
        return DataType.INTEGER
    if isinstance(value, float):
        return DataType.FLOAT
    if isinstance(value, datetime):
        return DataType.DATETIME
    
    # Convert to string for further analysis
    if not isinstance(value, str):
        value = str(value)
    
    value = value.strip()
    
    # Check for empty string after stripping
    if value == '':
        return DataType.NULL
    
    # Check for common null representations
    if value.upper() in ['NULL', 'NONE', 'N/A', 'NA', 'NAN', 'UNDEFINED']:
        return DataType.NULL
    
    # Check for boolean
    if value.upper() in ['TRUE', 'FALSE', 'YES', 'NO', 'Y', 'N', '1', '0']:
        if value.upper() in ['TRUE', 'FALSE', 'YES', 'NO', 'Y', 'N']:
            return DataType.BOOLEAN
        # '1' and '0' could be integers, so continue checking
    
    # Check for integer
    try:
        int(value)
        # Make sure it's not a float disguised as int
        if '.' not in value and 'e' not in value.lower():
            return DataType.INTEGER
    except ValueError:
        pass
    
    # Check for float
    try:
        float(value)
        return DataType.FLOAT
    except ValueError:
        pass
    
    # Check for datetime
    if _is_datetime(value):
        return DataType.DATETIME
    
    # Default to string
    return DataType.STRING


def _is_datetime(value: str) -> bool:
    """
    Check if a string represents a datetime.
    
    Args:
        value: String to check
        
    Returns:
        bool: True if the value is a datetime
    """
    for fmt in DATETIME_FORMATS:
        try:
            datetime.strptime(value, fmt)
            return True
        except ValueError:
            continue
    
    # Check for ISO 8601 with milliseconds
    iso_pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?Z?$'
    if re.match(iso_pattern, value):
        return True
    
    return False


def detect_date_format(value: str) -> Optional[str]:
    """
    Detect the datetime format of a string.
    
    Args:
        value: String to analyze
        
    Returns:
        Optional[str]: The detected format string, or None if not a datetime
    """
    for fmt in DATETIME_FORMATS:
        try:
            datetime.strptime(value, fmt)
            return fmt
        except ValueError:
            continue
    return None


def infer_column_type(values: List[Any], threshold: float = 0.8) -> DataType:
    """
    Infer the data type of a column from multiple values.
    Uses majority voting with a threshold.
    
    Args:
        values: List of values to analyze
        threshold: Minimum fraction of values that must match for type agreement
        
    Returns:
        DataType: The inferred column type
    """
    if not values:
        return DataType.UNKNOWN
    
    # Infer type for each non-null value
    type_counts = Counter()
    null_count = 0
    
    for value in values:
        detected_type = infer_type(value)
        if detected_type == DataType.NULL:
            null_count += 1
        else:
            type_counts[detected_type] += 1
    
    # If all values are null
    if not type_counts:
        return DataType.NULL
    
    # Get the most common type
    most_common_type, count = type_counts.most_common(1)[0]
    
    # Calculate agreement ratio (excluding nulls)
    total_non_null = len(values) - null_count
    agreement_ratio = count / total_non_null if total_non_null > 0 else 0
    
    # If agreement is above threshold, return the type
    if agreement_ratio >= threshold:
        return most_common_type
    
    # Handle mixed numeric types (int/float) - default to float
    if DataType.INTEGER in type_counts and DataType.FLOAT in type_counts:
        return DataType.FLOAT
    
    # If no clear agreement, default to string (most flexible)
    return DataType.STRING


def analyze_field_types(records: List[Dict[str, Any]]) -> Dict[str, DataType]:
    """
    Analyze field types across multiple records.
    
    Args:
        records: List of record dictionaries
        
    Returns:
        Dict[str, DataType]: Mapping of field names to detected types
    """
    if not records:
        return {}
    
    # Collect all field names
    all_fields = set()
    for record in records:
        all_fields.update(record.keys())
    
    # Analyze each field
    field_types = {}
    for field in all_fields:
        # Collect all values for this field
        values = [record.get(field) for record in records]
        field_types[field] = infer_column_type(values)
    
    return field_types
