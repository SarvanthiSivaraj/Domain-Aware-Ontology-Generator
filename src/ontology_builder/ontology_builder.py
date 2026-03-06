"""
Step 10: Ontology Construction Module
Programmatically builds an OWL ontology model using Owlready2 from the
semantic inference results (entities, attributes, relationships).
"""
from typing import Dict, Any, List
from owlready2 import get_ontology, Thing, DataProperty, ObjectProperty, FunctionalProperty
import owlready2


# Mapping from XSD type strings to Owlready2 Python types
XSD_TO_PYTHON = {
    "xsd:string": str,
    "xsd:integer": int,
    "xsd:float": float,
    "xsd:boolean": bool,
    "xsd:dateTime": str,  # Owlready2 stores datetime as string
}


class OntologyBuilder:
    """
    Step 10: Constructs an OWL ontology from the semantic inference results.

    Creates:
    - OWL Classes from identified entities (Step 7)
    - Data Properties from classified attributes (Step 8)
    - Object Properties from detected relationships (Step 9)
    """

    def __init__(self, base_iri: str = "http://example.org/ontology/"):
        """
        Initialize the OntologyBuilder.

        Args:
            base_iri: Base IRI for the ontology namespace.
        """
        self.base_iri = base_iri
        self.ontology = None
        self.classes = {}
        self.data_properties = {}
        self.object_properties = {}

    def build(
        self,
        domain_name: str,
        entities: Dict[str, Dict[str, Any]],
        attributes: Dict[str, Dict[str, Any]],
        relationships: List[Dict[str, Any]],
    ):
        """
        Build the OWL ontology from semantic inference results.

        Args:
            domain_name: Name of the detected domain (used in IRI).
            entities: Step 7 output — EntityName -> {fields, anchor_field, confidence}
            attributes: Step 8 output — EntityName -> {anchor_field, attributes: [...]}
            relationships: Step 9 output — list of relationship dicts.

        Returns:
            The constructed owlready2 ontology object.
        """
        # Create ontology with domain-specific IRI
        iri = f"{self.base_iri}{domain_name.lower()}#"
        self.ontology = get_ontology(iri)

        with self.ontology:
            # 1. Create OWL Classes
            self._create_classes(entities)

            # 2. Create Data Properties
            self._create_data_properties(attributes)

            # 3. Create Object Properties
            self._create_object_properties(relationships)

        return self.ontology

    def _create_classes(self, entities: Dict[str, Dict[str, Any]]):
        """Create an OWL Class for each identified entity."""
        for entity_name in entities:
            # Dynamically create a class that inherits from Thing
            owl_class = type(entity_name, (Thing,), {"namespace": self.ontology})
            self.classes[entity_name] = owl_class

    def _create_data_properties(self, attributes: Dict[str, Dict[str, Any]]):
        """Create OWL Data Properties for each entity's attributes."""
        for entity_name, info in attributes.items():
            owl_class = self.classes.get(entity_name)
            if not owl_class:
                continue

            for attr in info.get("attributes", []):
                field_name = attr["field"]
                xsd_type = attr.get("xsd_type", "xsd:string")
                python_type = XSD_TO_PYTHON.get(xsd_type, str)

                # Create a Data Property with domain and range
                prop = type(
                    field_name,
                    (DataProperty,),
                    {
                        "namespace": self.ontology,
                        "domain": [owl_class],
                        "range": [python_type],
                    },
                )
                self.data_properties[field_name] = prop

    def _create_object_properties(self, relationships: List[Dict[str, Any]]):
        """Create OWL Object Properties from detected relationships."""
        for rel in relationships:
            source_class = self.classes.get(rel["source"])
            target_class = self.classes.get(rel["target"])
            prop_name = rel["property_name"]

            if not source_class or not target_class:
                continue

            prop = type(
                prop_name,
                (ObjectProperty,),
                {
                    "namespace": self.ontology,
                    "domain": [source_class],
                    "range": [target_class],
                },
            )
            self.object_properties[prop_name] = prop

    def get_summary(self) -> Dict[str, Any]:
        """Return a summary of the constructed ontology."""
        return {
            "iri": self.ontology.base_iri if self.ontology else None,
            "classes": list(self.classes.keys()),
            "data_properties": list(self.data_properties.keys()),
            "object_properties": list(self.object_properties.keys()),
        }
