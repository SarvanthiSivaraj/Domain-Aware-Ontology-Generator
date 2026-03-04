"""
Step 4: Schema Analyzer Module
Analyzes the structural patterns of parsed data, including identifier detection,
naming convention analysis, and prefix recognition.
"""

from typing import List, Dict, Any, Optional, Set
from collections import Counter
import re
from src.core.parsed_data import FieldMetadata
from src.utils.type_detector import analyze_field_types, DataType

class SchemaMetadata:
    """Formal outcome object for Step 4."""
    def __init__(self, field_metadata: Dict[str, FieldMetadata], hierarchy: Dict[str, List[str]]):
        self.field_metadata = field_metadata
        self.hierarchy = hierarchy
        self.fields = list(field_metadata.keys())

class SchemaExtractor:
    """
    Step 4: Schema Extractor
    Analyzes the structural schema of flat or flattened datasets.
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

    def analyze(self, records: List[Dict[str, Any]]) -> SchemaMetadata:
        """
        Runs comprehensive schema analysis on records.
        """
        if not records:
            return SchemaMetadata({}, {})
            
        # 1. Detect field names and types using the utility
        field_types = analyze_field_types(records)
        all_fields = list(field_types.keys())
            
        # 2. Detect identifiers and prefixes
        id_fields = self.detect_identifiers(all_fields)
        prefix_list = self.detect_prefixes(all_fields)
        
        field_metadata = {}
        hierarchy = {}
        
        for field in all_fields:
            # Analyze prefix
            detected_prefix = None
            for p in prefix_list:
                if field.startswith(p) and field != p[:-1]:
                    detected_prefix = p[:-1]
                    break
            
            # Update hierarchy mapping
            if detected_prefix:
                if detected_prefix not in hierarchy:
                    hierarchy[detected_prefix] = []
                hierarchy[detected_prefix].append(field)

            # Collect non-null values for samples and stats
            values = [record.get(field) for record in records if field in record]
            non_null_values = [v for v in values if v is not None]

            # Create the metadata object correctly
            # name and data_type are required positional arguments
            dt = field_types.get(field, DataType.UNKNOWN).value
            
            metadata = FieldMetadata(
                name=field,
                data_type=dt,
                nullable=(len(non_null_values) < len(records)),
                null_count=len(records) - len(non_null_values),
                unique_count=len(set(str(v) for v in non_null_values)) if non_null_values else 0,
                is_identifier=(field in id_fields),
                prefix=detected_prefix,
                sample_values=list(set(non_null_values))[:5]
            )
            
            field_metadata[field] = metadata

        return SchemaMetadata(field_metadata, hierarchy)

    def detect_identifiers(self, field_names: List[str]) -> Set[str]:
        """Identify fields that are likely primary or foreign keys."""
        id_fields = set()
        for name in field_names:
            lower_name = name.lower()
            for pattern in self.ID_PATTERNS:
                if re.match(pattern, lower_name):
                    id_fields.add(name)
                    break
        return id_fields

    def detect_prefixes(self, field_names: List[str], min_overlap: int = 2) -> List[str]:
        """Detect repeated prefixes across field names."""
        prefixes = Counter()
        for name in field_names:
            if '_' in name:
                parts = name.split('_')
                for i in range(1, len(parts)):
                    candidate = "_".join(parts[:i]) + "_"
                    prefixes[candidate] += 1
        return sorted([p for p, count in prefixes.items() if count >= min_overlap], key=len, reverse=True)
