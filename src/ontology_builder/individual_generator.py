"""
Step 11: Individual Generation Module
Converts dataset records into OWL Individuals (instances) of the classes
defined in Step 10, populating data properties and establishing object property links.
"""
from typing import Dict, Any, List
from src.core.parsed_data import ParsedData
from src.ontology_builder.ontology_builder import OntologyBuilder
import re


class IndividualGenerator:
    """
    Step 11: Generates OWL Individuals from dataset records.

    For each record:
    1. Determines which entity/class it belongs to (via anchor field).
    2. Creates a named individual: {EntityName}_{anchor_value}.
    3. Sets data property values from the record.
    4. Links individuals via object properties where applicable.
    """

    def __init__(self, builder: OntologyBuilder):
        """
        Initialize the IndividualGenerator.

        Args:
            builder: The OntologyBuilder from Step 10 (contains ontology, classes, properties).
        """
        self.builder = builder
        self.ontology = builder.ontology
        self.individuals = {}  # Maps "EntityName_ID" -> individual instance
        self.stats = {}  # Maps EntityName -> count of individuals created

    def generate(
        self,
        parsed_data: ParsedData,
        entities: Dict[str, Dict[str, Any]],
        attributes: Dict[str, Dict[str, Any]],
        relationships: List[Dict[str, Any]],
    ) -> Dict[str, int]:
        """
        Generate OWL Individuals from parsed data records.

        Args:
            parsed_data: The ParsedData object with all records.
            entities: Step 7 output.
            attributes: Step 8 output.
            relationships: Step 9 output.

        Returns:
            Dict mapping EntityName -> count of individuals created.
        """
        records = parsed_data.get_records()

        with self.ontology:
            # Phase 1: Create individuals and set data properties
            for record in records:
                self._create_individuals_from_record(record, entities, attributes)

            # Phase 2: Link individuals via object properties
            for record in records:
                self._link_individuals(record, entities, relationships)

        return self.stats

    def _create_individuals_from_record(
        self,
        record: Dict[str, Any],
        entities: Dict[str, Dict[str, Any]],
        attributes: Dict[str, Dict[str, Any]],
    ):
        """Create an individual for each entity that matches this record."""
        for entity_name, entity_info in entities.items():
            anchor_field = entity_info.get("anchor_field")
            if not anchor_field or anchor_field not in record:
                continue

            anchor_value = record.get(anchor_field)
            if anchor_value is None:
                continue

            # Create a safe individual name
            safe_name = self._make_safe_name(f"{entity_name}_{anchor_value}")

            # Skip if already created
            if safe_name in self.individuals:
                continue

            # Get the OWL class
            owl_class = self.builder.classes.get(entity_name)
            if not owl_class:
                continue

            # Create the individual
            individual = owl_class(safe_name)
            self.individuals[safe_name] = individual

            # Update stats
            self.stats[entity_name] = self.stats.get(entity_name, 0) + 1

            # Set data property values
            entity_attrs = attributes.get(entity_name, {})
            for attr in entity_attrs.get("attributes", []):
                field_name = attr["field"]
                if field_name in record and record[field_name] is not None:
                    prop = self.builder.data_properties.get(field_name)
                    if prop:
                        try:
                            setattr(individual, field_name, [record[field_name]])
                        except Exception:
                            # If type mismatch, store as string
                            setattr(individual, field_name, [str(record[field_name])])

    def _link_individuals(
        self,
        record: Dict[str, Any],
        entities: Dict[str, Dict[str, Any]],
        relationships: List[Dict[str, Any]],
    ):
        """Establish object property links between individuals."""
        for rel in relationships:
            source_entity = rel["source"]
            target_entity = rel["target"]
            prop_name = rel["property_name"]
            via_field = rel["via_field"]

            # Get source entity anchor
            source_info = entities.get(source_entity, {})
            source_anchor = source_info.get("anchor_field")
            if not source_anchor or source_anchor not in record:
                continue

            # Get the linking field value
            if via_field not in record or record[via_field] is None:
                continue

            source_id = record.get(source_anchor)
            target_id = record.get(via_field)

            if source_id is None or target_id is None:
                continue

            source_name = self._make_safe_name(f"{source_entity}_{source_id}")
            target_name = self._make_safe_name(f"{target_entity}_{target_id}")

            source_ind = self.individuals.get(source_name)
            target_ind = self.individuals.get(target_name)

            if source_ind and target_ind:
                obj_prop = self.builder.object_properties.get(prop_name)
                if obj_prop:
                    try:
                        current = getattr(source_ind, prop_name, [])
                        if target_ind not in current:
                            setattr(source_ind, prop_name, current + [target_ind])
                    except Exception:
                        pass

    @staticmethod
    def _make_safe_name(name: str) -> str:
        """Convert a value into a safe OWL individual name."""
        # Replace non-alphanumeric characters with underscores
        safe = re.sub(r'[^a-zA-Z0-9_]', '_', str(name))
        # Ensure it doesn't start with a digit
        if safe and safe[0].isdigit():
            safe = f"_{safe}"
        return safe

    def get_individuals_summary(self) -> List[Dict[str, Any]]:
        """Return a summary of all created individuals."""
        summary = []
        for name, individual in self.individuals.items():
            summary.append({
                "name": name,
                "type": type(individual).__name__,
            })
        return summary
