"""
CSV Parser Module

Parses CSV files into structured data with type detection.
"""

import csv
import pandas as pd
from typing import Dict, Any, List
from src.parsers.base_parser import BaseParser
from src.core.parsed_data import ParsedData

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
        
        return parsed_data
    
