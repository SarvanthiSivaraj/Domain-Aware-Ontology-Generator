# Domain-Aware OWL Ontology Generation Framework

## Overview

Ontology engineering plays a critical role in knowledge representation, semantic data integration, and intelligent data analysis. This project presents a **Domain-Aware OWL Ontology Generation Framework** that automates the transformation of structured datasets (CSV/JSON) into semantic ontologies. 

Unlike generic converters, this framework uses **Domain Awareness** to perform semantic inference, automatically constructing ontology classes, properties, and relationships that are contextually accurate for domains like Cybersecurity, Healthcare, and Finance.

The generated ontologies are exported in **OWL (Web Ontology Language)** format and are compatible with **Protégé** and reasoning engines.

---

## The 12-Step Architecture

The system follows a rigorous 12-step pipeline divided into five functional phases:

### Phase 1: Core Foundation
1.  **File Validation**: Ensures file existence, readability, and size constraints.
2.  **Format Detection**: Automatically identifies JSON or CSV formats.
3.  **Data Parsing**: Ingests raw data and flattens nested structures (JSON).

### Phase 2: Structural Analysis
4.  **Schema Extraction**: Analyzes data types, identifies IDs, and detects prefix-based hierarchies.

### Phase 3: Domain Awareness
5.  **Domain Detection**: Uses keyword-based scoring to identify the dataset's domain.
6.  **Domain Knowledge Loading**: Loads specific entity rules and mapping configurations for the detected domain.

### Phase 4: Semantic Inference Engine
7.  **Entity Identification**: Maps dataset fields to domain entities (Ontology Classes).
8.  **Attribute Classification**: Classifies fields as Data Properties (Attributes).
9.  **Relationship Detection**: Infers Object Properties (Links) between entities.

### Phase 5: Ontology Construction
10. **Ontology Construction**: Programmatically builds the OWL model using Owlready2.
11. **Individual Generation**: Converts dataset records into ontology individuals (Instances).
12. **OWL File Generation**: Serializes the final model into a `.owl` file.

---

## Project Structure

```text
Domain-Aware-Ontology-Generator/
├── config/
│   └── domain_rules/       # JSON configuration for domain-specific keywords and mappings
├── src/
│   ├── core/               # Steps 1-2: validator.py, detector.py
│   ├── parsers/            # Step 3: JSON and CSV parsing logic
│   ├── schema/             # Step 4: Schema extraction and metadata
│   ├── domain/             # Steps 5-6: Domain detection and knowledge loading
│   ├── analyzers/          # Steps 7-9: Semantic inference modules
│   ├── ontology_builder/   # Step 10: OWL construction logic
│   └── utils/              # Datatype detection and helper utilities
├── tests/
│   └── test_data/          # Sample datasets (Cybersecurity, Healthcare, Users)
├── output/                 # Destination for generated OWL files
├── main.py                 # Primary entry point for the pipeline
└── requirements.txt
```

---

## Installation

1. Clone the repository:
   ```bash
   git clone <repository_url>
   cd Domain-Aware-Ontology-Generator
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## Usage

The framework is executed via `main.py`. Provide the path to your dataset using the `--input` or `-i` flag.

### Run Cybersecurity Example (JSON)
```bash
python main.py --input tests/test_data/sample_cybersecurity.json
```

### Run Healthcare/User Example (CSV)
```bash
python main.py --input tests/test_data/sample_users.csv
```

---

## Current Status

| Phase | Status | Steps Covered |
|---|---|---|
| **Phase 1: Foundation** | ✅ Complete | 1, 2, 3 |
| **Phase 2: Structural** | ✅ Complete | 4 |
| **Phase 3: Domain** | ✅ Complete | 5, 6 |
| **Phase 4: Semantic** | ✅ Complete | 7, 8, 9 |
| **Phase 5: Construction** | ✅ Complete | 10, 11, 12 |

---

## Technical Outcomes
- **Step 1**: Returns a formal `ValidationResult` object.
- **Step 4**: Generates a `SchemaMetadata` object including type-sniffing and prefix hierarchies.
- **Step 6**: Produces an active `DomainConfig` object containing entity-to-field mappings.
- **Step 7**: Successfully identifies core Entities and their "Anchor" ID fields.
- **Step 8**: Classifies entity fields as Data Properties with XSD type mappings (`xsd:string`, `xsd:integer`, `xsd:float`, `xsd:boolean`, `xsd:dateTime`).
- **Step 9**: Detects Object Properties (relationships) between entities via domain rules and foreign key inference.
- **Step 10**: Constructs OWL ontology model using Owlready2 with Classes, Data Properties, and Object Properties.
- **Step 11**: Generates OWL Individuals from dataset records with data property values and object property links.
- **Step 12**: Exports the final ontology to `.owl` (RDF/XML) format, compatible with Protégé and reasoning engines.
