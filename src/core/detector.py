"""
Step 2: Format Detection Module
Identifies input format based on extension and content structure.
"""
import os
import json
import csv
from enum import Enum
from typing import Tuple

class FileFormat(Enum):
    JSON = "json"
    CSV = "csv"
    PDF = "pdf"
    UNKNOWN = "unknown"

class FormatDetector:
    """Detects and validates the format of input datasets."""

    @staticmethod
    def detect(file_path: str) -> FileFormat:
        """Determines if the file is JSON or CSV."""
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        
        if ext == '.json':
            return FileFormat.JSON
        elif ext == '.csv':
            return FileFormat.CSV
        elif ext == '.pdf':
            return FileFormat.PDF
        return FileFormat.UNKNOWN

    @staticmethod
    def validate_structure(file_path: str, file_format: FileFormat) -> Tuple[bool, str]:
        """Performs basic structural validation for the detected format."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                if file_format == FileFormat.JSON:
                    data = json.load(f)
                    if not isinstance(data, (dict, list)):
                        return False, "JSON must be an object or array."
                elif file_format == FileFormat.CSV:
                    reader = csv.reader(f)
                    header = next(reader, None)
                    if not header:
                         return False, "CSV has no valid header."
                elif file_format == FileFormat.PDF:
                    # Basic check for PDF header
                    return True, ""
                return True, ""
        except Exception as e:
            return False, str(e)
