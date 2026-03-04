import sys
import argparse
from src.core.validator import FileValidator
from src.core.detector import FormatDetector, FileFormat
from src.parsers.parser_factory import create_parser
from src.schema.schema_extractor import SchemaExtractor
from src.domain.domain_detector import DomainDetector
from src.domain.domain_loader import DomainLoader

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

    print(f"\n--- Phase 3: Domain Awareness ---")
    # Step 5: Domain Detection
    print(f"[5/12] Detecting domain...")
    detector = DomainDetector()
    domain, confidence = detector.detect(parsed_data.get_fields())
    print(f"✅ Domain detected: {domain} (Confidence: {confidence:.2f})")

    # Step 6: Domain Knowledge Loading
    print(f"[6/12] Loading domain knowledge...")
    loader = DomainLoader()
    domain_config = loader.load(domain)
    
    if domain_config:
        print(f"✅ Loaded {len(domain_config.get('entities', []))} entity rules for {domain}.")
    
    return parsed_data, domain, domain_config

def main():
    parser = argparse.ArgumentParser(description="Multi-Domain Aware OWL Ontology Generator")
    parser.add_argument("--input", "-i", required=True, help="Path to input dataset (JSON/CSV)")
    args = parser.parse_args()
    
    result = run_pipeline(args.input)
    if result:
        parsed_data, domain, domain_config = result
        print(f"\n{parsed_data.summary()}")
        print(f"\nActive Domain: {domain}")
        print("Phase 3 Complete! Ready for Step 7 (Entity Identification).")

if __name__ == "__main__":
    main()
