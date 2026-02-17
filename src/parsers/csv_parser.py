"""
CSV Parser Module

Parses CSV files into structured data with type detection.
"""

import csv
import pandas as pd
from typing import Dict, Any, List
from src.parsers.base_parser import BaseParser
from src.core.parsed_data import ParsedData, FieldMetadata
from src.utils.type_detector import infer_column_type, DataType


class CSVParser(BaseParser):
    """
    Parser for CSV files.
    
    Features:
    - Parses CSV into tabular data
    - Automatically detects column types
    - Handles missing values
    - Uses pandas for robust parsing
    """
    
    def __init__(self):
        """Initialize the CSV parser"""
        pass
    
    def parse(self, file_path: str) -> ParsedData:
        """
        Parse a CSV file.
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            ParsedData: Parsed data with metadata
        """
        # Read CSV using pandas
        df = pd.read_csv(file_path, keep_default_na=False, na_values=['', 'NA', 'N/A', 'null', 'NULL'])
        
        # Create ParsedData object
        parsed_data = ParsedData(source_file=file_path, file_format='csv')
        
        # Convert DataFrame to list of dictionaries
        records = df.to_dict('records')
        parsed_data.set_records(records)
        
        # Detect schema
        schema = self.detect_schema(df)
        parsed_data.set_field_metadata(schema['field_metadata'])
        
        return parsed_data
    
    def detect_schema(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Detect schema from DataFrame.
        
        Args:
            df: Pandas DataFrame
            
        Returns:
            dict: Schema information
        """
        field_metadata = {}
        
        for column in df.columns:
            # Get column values
            values = df[column].tolist()
            
            # Infer column type
            column_type = infer_column_type(values)
            
            # Calculate statistics
            non_null_values = [v for v in values if pd.notna(v) and v != '']
            unique_values = list(set(non_null_values))[:5]
            
            metadata = FieldMetadata(
                name=column,
                data_type=column_type.value,
                nullable=(len(non_null_values) < len(values)),
                null_count=len(values) - len(non_null_values),
                unique_count=df[column].nunique(),
                sample_values=unique_values
            )
            field_metadata[column] = metadata
        
        return {
            'field_metadata': field_metadata,
            'hierarchy': {}  # CSV is flat, no hierarchy
        }
