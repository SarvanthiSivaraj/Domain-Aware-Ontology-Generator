"""
Step 7: Entity Identification Module
Identifies domain entities present in the dataset by matching fields against domain mappings.
"""
from typing import List, Dict, Any, Set
from src.core.parsed_data import ParsedData
from src.domain.domain_loader import DomainConfig

class EntityIdentifier:
    """
    Identifies which entities (Classes) from the domain rules are present
    in the current dataset.
    """

    def __init__(self, domain_config: DomainConfig):
        self.domain_config = domain_config

    def identify(self, parsed_data: ParsedData) -> Dict[str, Dict[str, Any]]:
        """
        Identifies entities based on domain mappings and schema metadata.
        
        Returns:
            Dict mapping EntityName -> {
                'fields': List of associated fields,
                'anchor_field': The primary ID field for this entity,
                'confidence': match score
            }
        """
        identified_entities = {}
        available_fields = parsed_data.get_fields()
        
        # Iterating through all entities defined in the domain configuration
        for entity in self.domain_config.entities:
            # Get fields that the domain expects for this entity
            expected_fields = self.domain_config.get_fields_for_entity(entity)
            
            # Find which of these expected fields are actually in our dataset
            matched_fields = [f for f in expected_fields if f in available_fields]
            
            if not matched_fields:
                continue

            # Find the "Anchor Field" (the ID)
            anchor_field = None
            for field in matched_fields:
                metadata = parsed_data.get_field_metadata(field)
                if metadata and metadata.is_identifier:
                    anchor_field = field
                    break
            
            # Confidence is simply percentage of expected fields found
            confidence = len(matched_fields) / len(expected_fields) if expected_fields else 0.5

            identified_entities[entity] = {
                'fields': matched_fields,
                'anchor_field': anchor_field,
                'confidence': confidence
            }

        return identified_entities
