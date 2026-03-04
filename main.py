import sys
import argparse
from src.core.validator import FileValidator
from src.core.detector import FormatDetector, FileFormat
from src.parsers.parser_factory import create_parser

def run_phase1(file_path: str):
    print(f"\n--- Phase 1: Core Foundation ---")
    
    # Step 1: File Validation
    print(f"[1/12] Validating file: {file_path}")
    is_valid, errors = FileValidator.validate(file_path)
    if not is_valid:
        print(f"❌ Validation failed: {errors}")
        return None
    
    # Step 2: Format Detection
    print(f"[2/12] Detecting format...")
    fmt = FormatDetector.detect(file_path)
    if fmt == FileFormat.UNKNOWN:
        print(f"❌ Unsupported format.")
        return None
    
    is_struct_valid, error = FormatDetector.validate_structure(file_path, fmt)
    if not is_struct_valid:
        print(f"❌ Structural validation failed: {error}")
        return None
    
    print(f"✅ Format detected: {fmt.value.upper()}")
    
    # Step 3: Data Parsing
    print(f"[3/12] Parsing data...")
    try:
        parser = create_parser(fmt)
        parsed_data = parser.parse(file_path)
        print(f"✅ Data parsing successful. Total records: {parsed_data.get_record_count()}")
        return parsed_data
    except Exception as e:
        print(f"❌ Parsing failed: {str(e)}")
        return None

def main():
    parser = argparse.ArgumentParser(description="Multi-Domain Aware OWL Ontology Generator")
    parser.add_argument("--input", "-i", required=True, help="Path to input dataset (JSON/CSV)")
    args = parser.parse_args()
    
    parsed_data = run_phase1(args.input)
    if parsed_data:
        print("\nPhase 1 Complete! Ready for Step 4 (Schema Extraction).")

if __name__ == "__main__":
    main()
