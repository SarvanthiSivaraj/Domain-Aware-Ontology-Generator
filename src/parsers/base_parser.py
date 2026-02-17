"""
Base Parser Abstract Class

Defines the interface that all parsers must implement.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
from src.core.parsed_data import ParsedData


class BaseParser(ABC):
    """
    Abstract base class for data parsers.
    
    All parsers must implement the parse() method to convert
    raw file data into a ParsedData object.
    """
    
    @abstractmethod
    def parse(self, file_path: str) -> ParsedData:
        """
        Parse a file and return structured data.
        
        Args:
            file_path: Path to the file to parse
            
        Returns:
            ParsedData: Parsed data with metadata
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format is invalid
        """
        pass
    
    @abstractmethod
    def detect_schema(self, data: Any) -> Dict[str, Any]:
        """
        Detect and extract schema information from parsed data.
        
        Args:
            data: The parsed data structure
            
        Returns:
            dict: Schema information including field types and metadata
        """
        pass
