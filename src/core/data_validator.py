"""
Data Input and Validation Module

Handles file validation, format detection, and initial error checking
for the Domain-Aware Ontology Generator.
"""

import os
import json
import csv
from typing import Tuple, Optional
from enum import Enum


class FileFormat(Enum):
    """Supported file formats"""
    JSON = "json"
    CSV = "csv"
    UNKNOWN = "unknown"


class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass


class DataValidator:
    """
    Validates and processes input data files for ontology generation.
    
    This class performs:
    - File existence and accessibility checks
    - Format detection (JSON/CSV)
    - Basic structure validation
    - Empty file detection
    """
    
    SUPPORTED_FORMATS = {'.json', '.csv'}
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB limit
    
    def __init__(self):
        """Initialize the DataValidator"""
        self.file_path: Optional[str] = None
        self.file_format: FileFormat = FileFormat.UNKNOWN
        self.validation_errors: list = []
    
    def validate_file(self, file_path: str) -> Tuple[bool, FileFormat, list]:
        """
        Validate the input file and detect its format.
        
        Args:
            file_path (str): Path to the input file
            
        Returns:
            Tuple[bool, FileFormat, list]: 
                - Validation success status
                - Detected file format
                - List of validation errors (if any)
        """
        self.file_path = file_path
        self.validation_errors = []
        
        # Step 1: Check if file exists
        if not self._check_file_exists():
            return False, FileFormat.UNKNOWN, self.validation_errors
        
        # Step 2: Check file size
        if not self._check_file_size():
            return False, FileFormat.UNKNOWN, self.validation_errors
        
        # Step 3: Detect file format
        self.file_format = self._detect_format()
        if self.file_format == FileFormat.UNKNOWN:
            self.validation_errors.append("Unsupported file format. Only JSON and CSV are supported.")
            return False, FileFormat.UNKNOWN, self.validation_errors
        
        # Step 4: Check if file is empty
        if not self._check_not_empty():
            return False, self.file_format, self.validation_errors
        
        # Step 5: Validate file structure based on format
        if not self._validate_structure():
            return False, self.file_format, self.validation_errors
        
        return True, self.file_format, []
    
    def _check_file_exists(self) -> bool:
        """Check if the file exists and is accessible"""
        if not os.path.exists(self.file_path):
            self.validation_errors.append(f"File not found: {self.file_path}")
            return False
        
        if not os.path.isfile(self.file_path):
            self.validation_errors.append(f"Path is not a file: {self.file_path}")
            return False
        
        if not os.access(self.file_path, os.R_OK):
            self.validation_errors.append(f"File is not readable: {self.file_path}")
            return False
        
        return True
    
    def _check_file_size(self) -> bool:
        """Check if file size is within acceptable limits"""
        file_size = os.path.getsize(self.file_path)
        
        if file_size > self.MAX_FILE_SIZE:
            self.validation_errors.append(
                f"File size ({file_size / 1024 / 1024:.2f} MB) exceeds maximum allowed size "
                f"({self.MAX_FILE_SIZE / 1024 / 1024:.2f} MB)"
            )
            return False
        
        return True
    
    def _detect_format(self) -> FileFormat:
        """Detect the file format based on extension"""
        _, ext = os.path.splitext(self.file_path)
        ext = ext.lower()
        
        if ext == '.json':
            return FileFormat.JSON
        elif ext == '.csv':
            return FileFormat.CSV
        else:
            return FileFormat.UNKNOWN
    
    def _check_not_empty(self) -> bool:
        """Check if the file is not empty"""
        if os.path.getsize(self.file_path) == 0:
            self.validation_errors.append("File is empty")
            return False
        return True
    
    def _validate_structure(self) -> bool:
        """Validate the internal structure of the file"""
        try:
            if self.file_format == FileFormat.JSON:
                return self._validate_json_structure()
            elif self.file_format == FileFormat.CSV:
                return self._validate_csv_structure()
        except Exception as e:
            self.validation_errors.append(f"Structure validation error: {str(e)}")
            return False
        
        return True
    
    def _validate_json_structure(self) -> bool:
        """Validate JSON file structure"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Check if JSON is not empty
            if not data:
                self.validation_errors.append("JSON file contains no data")
                return False
            
            # JSON should be either a dict or a list
            if not isinstance(data, (dict, list)):
                self.validation_errors.append("JSON must be an object or array")
                return False
            
            return True
            
        except json.JSONDecodeError as e:
            self.validation_errors.append(f"Invalid JSON format: {str(e)}")
            return False
        except UnicodeDecodeError:
            self.validation_errors.append("File encoding error. Expected UTF-8.")
            return False
    
    def _validate_csv_structure(self) -> bool:
        """Validate CSV file structure"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                # Try to read the first few rows
                csv_reader = csv.reader(f)
                rows = list(csv_reader)
            
            # Check if CSV has at least a header row
            if len(rows) < 1:
                self.validation_errors.append("CSV file has no rows")
                return False
            
            # Check if header exists and is not empty
            header = rows[0]
            if not header or all(cell.strip() == '' for cell in header):
                self.validation_errors.append("CSV file has no valid header")
                return False
            
            # Check if there's at least one data row
            if len(rows) < 2:
                self.validation_errors.append("CSV file has no data rows (only header)")
                return False
            
            return True
            
        except csv.Error as e:
            self.validation_errors.append(f"Invalid CSV format: {str(e)}")
            return False
        except UnicodeDecodeError:
            self.validation_errors.append("File encoding error. Expected UTF-8.")
            return False


def validate_input_file(file_path: str) -> Tuple[bool, FileFormat, list]:
    """
    Convenience function to validate an input file.
    
    Args:
        file_path (str): Path to the input file
        
    Returns:
        Tuple[bool, FileFormat, list]: Validation result, format, and errors
    """
    validator = DataValidator()
    return validator.validate_file(file_path)


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python data_validator.py <file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    is_valid, file_format, errors = validate_input_file(file_path)
    
    if is_valid:
        print(f"✅ File validation successful!")
        print(f"📄 Format: {file_format.value.upper()}")
    else:
        print(f"❌ File validation failed!")
        print(f"Errors:")
        for error in errors:
            print(f"  - {error}")
