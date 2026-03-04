"""
Step 1: File Validation Module
Handles basic file system checks like existence and size.
"""
import os
from typing import Tuple, List

class FileValidator:
    """Validates physical file properties."""
    
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB limit

    @staticmethod
    def validate(file_path: str) -> Tuple[bool, List[str]]:
        """Checks existence, readability, and size."""
        errors = []
        
        if not os.path.exists(file_path):
            return False, [f"File not found: {file_path}"]
            
        if not os.path.isfile(file_path):
            return False, [f"Path is not a file: {file_path}"]
            
        if not os.access(file_path, os.R_OK):
            errors.append(f"File is not readable: {file_path}")
            
        if os.path.getsize(file_path) > FileValidator.MAX_FILE_SIZE:
            errors.append("File size exceeds 100MB limit.")
            
        if os.path.getsize(file_path) == 0:
            errors.append("File is empty.")
            
        return len(errors) == 0, errors
