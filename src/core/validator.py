"""
Step 1: File Validation Module
Handles basic file system checks like existence and size.
"""
import os
from typing import Tuple, List

class ValidationResult:
    """Standardized error object for file validation."""
    def __init__(self, is_valid: bool, errors: List[str], file_path: str):
        self.is_valid = is_valid
        self.errors = errors
        self.file_path = file_path

class FileValidator:
    """Validates physical file properties."""
    
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB limit

    @staticmethod
    def validate(file_path: str) -> ValidationResult:
        """Checks existence, readability, and size."""
        errors = []
        
        if not os.path.exists(file_path):
            return ValidationResult(False, [f"File not found: {file_path}"], file_path)
            
        if not os.path.isfile(file_path):
            return ValidationResult(False, [f"Path is not a file: {file_path}"], file_path)
            
        if not os.access(file_path, os.R_OK):
            errors.append(f"File is not readable: {file_path}")
            
        if os.path.getsize(file_path) > FileValidator.MAX_FILE_SIZE:
            errors.append("File size exceeds 100MB limit.")
            
        if os.path.getsize(file_path) == 0:
            errors.append("File is empty.")
            
        return ValidationResult(len(errors) == 0, errors, file_path)
