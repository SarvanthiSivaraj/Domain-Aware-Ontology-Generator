import sys
import argparse
from src.core.validator import FileValidator
from src.core.detector import FormatDetector, FileFormat
from src.parsers.parser_factory import create_parser
from src.schema.schema_extractor import SchemaExtractor
from src.domain.domain_detector import DomainDetector
from src.domain.domain_loader import DomainLoader
from src.analyzers.entity_identifier import EntityIdentifier
from src.analyzers.attribute_classifier import AttributeClassifier
from src.analyzers.relationship_detector import RelationshipDetector
from src.ontology_builder.ontology_builder import OntologyBuilder
from src.ontology_builder.individual_generator import IndividualGenerator
from src.ontology_builder.owl_exporter import OWLExporter

def run_pipeline(file_path: str):
    print(f"\n--- Phase 1: Core Foundation ---")
    
    # Step 1: File Validation
    print(f"[1/12] Validating file: {file_path}")
    validation_result = FileValidator.validate(file_path)
    if not validation_result.is_valid:
        print(f"❌ Validation failed: {validation_result.errors}")
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
    
    parsed_data.set_field_metadata(schema_result.field_metadata)
    # Merge hierarchy
    current_hierarchy = parsed_data.get_hierarchy()
    current_hierarchy.update(schema_result.hierarchy)
    parsed_data.set_hierarchy(current_hierarchy)
    
    print(f"✅ Schema extraction complete. Fields detected: {len(schema_result.fields)}")

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
    print(f"✅ Loaded DomainConfig for: {domain_config.name}")

    print(f"\n--- Phase 4: Semantic Inference ---")
    # Step 7: Entity Identification
    print(f"[7/12] Identifying entities...")
    identifier = EntityIdentifier(domain_config)
    entities = identifier.identify(parsed_data)
    
    for ent_name, info in entities.items():
        anchor = info['anchor_field'] or "None"
        print(f"✅ Identified Entity: {ent_name} (Anchor: {anchor}, Match: {info['confidence']*100:.0f}%)")

    # Step 8: Attribute Classification
    print(f"[8/12] Classifying attributes...")
    classifier = AttributeClassifier()
    attributes = classifier.classify(entities, parsed_data)

    for ent_name, info in attributes.items():
        anchor = info['anchor_field'] or "None"
        attr_list = [a['field'] for a in info['attributes']]
        print(f"✅ {ent_name}: Anchor={anchor}, DataProperties={attr_list}")
        for attr in info['attributes']:
            print(f"     ↳ {attr['field']}: {attr['data_type']} → {attr['xsd_type']}")

    # Step 9: Relationship Detection
    print(f"[9/12] Detecting relationships...")
    rel_detector = RelationshipDetector()
    relationships = rel_detector.detect(entities, domain_config, parsed_data)

    for rel in relationships:
        print(f"✅ {rel['source']} --{rel['property_name']}--> {rel['target']} (via: {rel['via_field']}, method: {rel['detection_method']})")

    if not relationships:
        print("ℹ️  No relationships detected between identified entities.")

    print(f"\n--- Phase 5: Ontology Construction ---")
    # Step 10: Ontology Construction
    print(f"[10/12] Constructing ontology...")
    builder = OntologyBuilder()
    ontology = builder.build(domain_config.name, entities, attributes, relationships)
    summary = builder.get_summary()

    print(f"✅ Ontology IRI: {summary['iri']}")
    print(f"✅ OWL Classes: {summary['classes']}")
    print(f"✅ Data Properties: {summary['data_properties']}")
    print(f"✅ Object Properties: {summary['object_properties']}")

    # Step 11: Individual Generation
    print(f"[11/12] Generating individuals...")
    generator = IndividualGenerator(builder)
    ind_stats = generator.generate(parsed_data, entities, attributes, relationships)

    for ent_name, count in ind_stats.items():
        print(f"✅ {ent_name}: {count} individuals created")

    ind_summary = generator.get_individuals_summary()
    for ind in ind_summary:
        print(f"     ↳ {ind['name']} (type: {ind['type']})")

    total_inds = sum(ind_stats.values())
    print(f"✅ Total: {total_inds} individuals generated")

    # Step 12: OWL File Generation
    print(f"[12/12] Exporting OWL file...")
    exporter = OWLExporter()
    output_path = exporter.export(ontology, domain_config.name)
    print(f"✅ OWL file saved to: {output_path}")

    return parsed_data, domain_config, entities, attributes, relationships, ontology, builder, generator, output_path

def main():
    parser = argparse.ArgumentParser(description="Multi-Domain Aware OWL Ontology Generator")
    parser.add_argument("--input", "-i", required=True, help="Path to input dataset (JSON/CSV)")
    args = parser.parse_args()
    
    result = run_pipeline(args.input)
    if result:
        parsed_data, domain_config, entities, attributes, relationships, ontology, builder, generator, output_path = result
        print(f"\n{parsed_data.summary()}")
        print(f"\nActive Domain: {domain_config.name}")
        print(f"Identified Entities: {', '.join(entities.keys())}")
        total_attrs = sum(len(a['attributes']) for a in attributes.values())
        print(f"Classified Attributes: {total_attrs} data properties across {len(attributes)} entities")
        print(f"Detected Relationships: {len(relationships)} object properties")
        summary = builder.get_summary()
        print(f"Ontology: {len(summary['classes'])} classes, {len(summary['data_properties'])} data props, {len(summary['object_properties'])} object props")
        total_inds = sum(generator.stats.values()) if generator.stats else 0
        print(f"Individuals: {total_inds} instances created")
        print(f"Output: {output_path}")
        print("\n\u2705 All 12 Steps Complete! Pipeline finished successfully.")

if __name__ == "__main__":
    main()
