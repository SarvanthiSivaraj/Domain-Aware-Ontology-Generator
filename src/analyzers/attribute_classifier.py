"""
Step 8: Attribute Classification Module
Classifies entity fields into Data Properties (attributes) with XSD type mappings
for OWL ontology construction.
"""
from typing import Dict, Any, List
from src.core.parsed_data import ParsedData


# Mapping from internal DataType values to XSD types for OWL
XSD_TYPE_MAP = {
    "string": "xsd:string",
    "integer": "xsd:integer",
    "float": "xsd:float",
    "boolean": "xsd:boolean",
    "datetime": "xsd:dateTime",
    "null": "xsd:string",
    "unknown": "xsd:string",
}


class AttributeClassifier:
    """
    Classifies fields of identified entities into Data Properties (Attributes).

    For each entity from Step 7, this module:
    1. Separates anchor/ID fields from descriptive attribute fields.
    2. Maps each attribute's detected data type to its XSD equivalent.
    3. Produces a structured classification result ready for ontology construction.
    """

    def classify(self, entities: Dict[str, Dict[str, Any]], parsed_data: ParsedData) -> Dict[str, Dict[str, Any]]:
        """
        Classify fields of each identified entity into data properties.

        Args:
            entities: Output of Step 7 (EntityIdentifier.identify()).
                      Maps EntityName -> {'fields', 'anchor_field', 'confidence'}
            parsed_data: The ParsedData object containing field metadata.

        Returns:
            Dict mapping EntityName -> {
                'anchor_field': str or None,
                'attributes': List of dicts with keys:
                    - 'field': field name
                    - 'data_type': detected type string
                    - 'xsd_type': XSD equivalent for OWL
                    - 'nullable': whether the field allows nulls
                    - 'unique_count': number of unique values
            }
        """
        classification = {}

        for entity_name, entity_info in entities.items():
            anchor = entity_info.get("anchor_field")
            fields = entity_info.get("fields", [])

            attributes = []
            for field in fields:
                # Skip the anchor/ID field — it identifies individuals, not a data property
                if field == anchor:
                    continue

                metadata = parsed_data.get_field_metadata(field)
                if metadata is None:
                    continue

                data_type = metadata.data_type
                xsd_type = XSD_TYPE_MAP.get(data_type, "xsd:string")

                attributes.append({
                    "field": field,
                    "data_type": data_type,
                    "xsd_type": xsd_type,
                    "nullable": metadata.nullable,
                    "unique_count": metadata.unique_count,
                })

            classification[entity_name] = {
                "anchor_field": anchor,
                "attributes": attributes,
            }

        return classification
