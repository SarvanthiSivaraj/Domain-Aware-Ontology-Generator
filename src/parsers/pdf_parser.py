"""
PDF Parser Module

Extracts text from PDF files into structured data for downstream processing.
"""

import fitz  # PyMuPDF
from typing import Dict, Any, List
from src.parsers.base_parser import BaseParser
from src.core.parsed_data import ParsedData


class PDFParser(BaseParser):
    """
    Parser for PDF files.
    
    Features:
    - Extracts text from each page using PyMuPDF
    - Stores each page's content as a separate record
    - Preserves basic metadata (page number)
    """
    
    def parse(self, file_path: str) -> ParsedData:
        """
        Parse a PDF file.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            ParsedData: Parsed data with each page as a record
        """
        records = []
        
        try:
            doc = fitz.open(file_path)
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text()
                
                # Each page is a record
                records.append({
                    'page_number': page_num + 1,
                    'text_content': text.strip(),
                    '_entity_type': 'pdf_page'
                })
            doc.close()
        except Exception as e:
            raise ValueError(f"Failed to parse PDF: {str(e)}")
        
        # Create ParsedData object
        parsed_data = ParsedData(source_file=file_path, file_format='pdf')
        parsed_data.set_records(records)
        
        return parsed_data
