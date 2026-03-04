import sys
import argparse
from src.core.validator import FileValidator
from src.core.detector import FormatDetector, FileFormat
from src.parsers.parser_factory import create_parser
from src.schema.schema_extractor import SchemaExtractor

def run_pipeline(file_path: str):
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
    except Exception as e:
        print(f"❌ Parsing failed: {str(e)}")
        return None

    print(f"\n--- Phase 2: Structural Analysis ---")
    # Step 4: Schema Extraction
    print(f"[4/12] Extracting schema...")
    extractor = SchemaExtractor()
    schema_result = extractor.analyze(parsed_data.get_records())
    
    parsed_data.set_field_metadata(schema_result['field_metadata'])
    # Merge hierarchy
    current_hierarchy = parsed_data.get_hierarchy()
    current_hierarchy.update(schema_result['hierarchy'])
    parsed_data.set_hierarchy(current_hierarchy)
    
    print(f"✅ Schema extraction complete. Fields detected: {len(parsed_data.get_fields())}")
    return parsed_data

def main():
    parser = argparse.ArgumentParser(description="Multi-Domain Aware OWL Ontology Generator")
    parser.add_argument("--input", "-i", required=True, help="Path to input dataset (JSON/CSV)")
    args = parser.parse_args()
    
    parsed_data = run_pipeline(args.input)
    if parsed_data:
        print(f"\n{parsed_data.summary()}")
        print("\nPhase 2 (Step 4) Complete! Ready for Step 5 (Domain Detection).")

if __name__ == "__main__":
    main()
