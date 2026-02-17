"""
Parser Factory Module

Creates the appropriate parser based on file format.
"""

from src.core.data_validator import FileFormat
from src.parsers.base_parser import BaseParser
from src.parsers.json_parser import JSONParser
from src.parsers.csv_parser import CSVParser


def create_parser(file_format: FileFormat) -> BaseParser:
    """
    Create and return the appropriate parser for the given file format.
    
    Args:
        file_format: The format of the file (FileFormat enum)
        
    Returns:
        BaseParser: An instance of the appropriate parser
        
    Raises:
        ValueError: If the file format is not supported
    """
    if file_format == FileFormat.JSON:
        return JSONParser()
    elif file_format == FileFormat.CSV:
        return CSVParser()
    else:
        raise ValueError(f"Unsupported file format: {file_format}")


def parse_file(file_path: str, file_format: FileFormat):
    """
    Convenience function to parse a file.
    
    Args:
        file_path: Path to the file
        file_format: Format of the file
        
    Returns:
        ParsedData: Parsed data with metadata
    """
    parser = create_parser(file_format)
    return parser.parse(file_path)
