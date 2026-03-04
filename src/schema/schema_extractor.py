"""
Schema Analyzer Module

Analyzes the structural patterns of parsed data, including identifier detection,
naming convention analysis, and prefix recognition.
"""

from typing import List, Dict, Any, Optional, Set
from collections import Counter
import re
from src.core.parsed_data import FieldMetadata
from src.utils.type_detector import analyze_field_types, DataType

class SchemaExtractor:
    """
    Step 4: Schema Extractor
    Analyzes the structural schema of flat or flattened datasets.
    
    Provides:
    - ID/Identifier detection
    - Prefix-based grouping logic
    - Data type integration
    """

    ID_PATTERNS = [
        r'^.*_id$',         # user_id, device_id
        r'^id$',            # id
        r'^.*_uid$',        # unique_id
        r'^uid$',           # uid
        r'^.*_key$',        # primary_key
        r'^uuid$',          # uuid
        r'^ident(ity)?$'    # identity, ident
    ]

    def __init__(self):
        """Initialize the SchemaAnalyzer"""
        pass

    def analyze(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Perform a comprehensive schema analysis on a list of records.
        
        Args:
            records: List of record dictionaries
            
        Returns:
            dict: result containing 'field_metadata' and 'hierarchy'
        """
        if not records:
            return {'field_metadata': {}, 'hierarchy': {}}

        # 1. Detect data types using the existing utility
        field_types = analyze_field_types(records)
        all_fields = list(field_types.keys())

        # 2. Detect common prefixes
        prefixes = self.detect_prefixes(all_fields)

        # 3. Detect identifiers
        id_fields = self.detect_identifiers(all_fields)

        # 4. Create field metadata
        field_metadata = {}
        hierarchy = {}

        for field_name in all_fields:
            # Collect values for statistics
            values = [record.get(field_name) for record in records]
            non_null_values = [v for v in values if v is not None]
            
            # Determine prefix
            detected_prefix = None
            for p in prefixes:
                if field_name.startswith(p) and field_name != p[:-1]: # Don't match the prefix itself if it's a field
                    detected_prefix = p[:-1] # Remove the trailing underscore for the metadata
                    break
            
            # Update hierarchy mapping (group by prefix)
            if detected_prefix:
                if detected_prefix not in hierarchy:
                    hierarchy[detected_prefix] = []
                if field_name not in hierarchy[detected_prefix]:
                    hierarchy[detected_prefix].append(field_name)

            # Create the metadata object
            metadata = FieldMetadata(
                name=field_name,
                data_type=field_types.get(field_name, DataType.UNKNOWN).value,
                nullable=(len(non_null_values) < len(values)),
                null_count=len(values) - len(non_null_values),
                unique_count=len(set(str(v) for v in non_null_values)) if non_null_values else 0,
                is_identifier=(field_name in id_fields),
                prefix=detected_prefix,
                sample_values=list(set(non_null_values))[:5]
            )
            field_metadata[field_name] = metadata

        return {
            'field_metadata': field_metadata,
            'hierarchy': hierarchy
        }

    def detect_identifiers(self, field_names: List[str]) -> Set[str]:
        """
        Identify fields that are likely primary or foreign keys.
        
        Args:
            field_names: List of field names to check
            
        Returns:
            Set[str]: Fields identified as IDs
        """
        id_fields = set()
        for name in field_names:
            lower_name = name.lower()
            for pattern in self.ID_PATTERNS:
                if re.match(pattern, lower_name):
                    id_fields.add(name)
                    break
        return id_fields

    def detect_prefixes(self, field_names: List[str], min_overlap: int = 2) -> List[str]:
        """
        Detect repeated prefixes across field names.
        Example: ['user_id', 'user_name'] -> 'user_'
        
        Args:
            field_names: List of field names
            min_overlap: Minimum number of fields that must share the prefix
            
        Returns:
            List[str]: Detected prefixes (with trailing underscore) sorted by length descending
        """
        prefixes = Counter()
        
        for name in field_names:
            if '_' in name:
                parts = name.split('_')
                # Try compound prefixes: e.g. "network_activities_"
                for i in range(1, len(parts)):
                    candidate = "_".join(parts[:i]) + "_"
                    prefixes[candidate] += 1
        
        # Filter by overlap and return longest matches first
        detected = [p for p, count in prefixes.items() if count >= min_overlap]
        return sorted(detected, key=len, reverse=True)
