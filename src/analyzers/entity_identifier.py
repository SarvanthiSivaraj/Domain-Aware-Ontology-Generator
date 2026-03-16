"""
Step 7: Entity Identification Module
Identifies domain entities present in the dataset by matching fields against domain mappings.
"""
from typing import List, Dict, Any, Set
from src.core.parsed_data import ParsedData
from src.domain.domain_loader import DomainConfig
from src.core.llm_service import LLMService

class EntityIdentifier:
    """
    Identifies which entities (Classes) from the domain rules are present
    in the current dataset.
    """

    def __init__(self, domain_config: DomainConfig, llm_service: LLMService = None):
        self.domain_config = domain_config
        self.llm_service = llm_service

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
        
        # --- Strategy 1: Domain Mapping ---
        for entity in self.domain_config.entities:
            expected_fields = self.domain_config.get_fields_for_entity(entity)
            matched_fields = [f for f in expected_fields if f in available_fields]
            
            if not matched_fields:
                continue

            anchor_field = None
            for field in matched_fields:
                metadata = parsed_data.get_field_metadata(field)
                if metadata and metadata.is_identifier:
                    anchor_field = field
                    break
            
            confidence = len(matched_fields) / len(expected_fields) if expected_fields else 0.5

            identified_entities[entity] = {
                'fields': matched_fields,
                'anchor_field': anchor_field,
                'confidence': confidence,
                'method': 'domain_mapping'
            }

        # --- Strategy 2: LLM Discovery (especially for PDF or unstructured) ---
        if self.llm_service and self.llm_service.is_available():
            # For PDF, use the first few pages of text for discovery
            text_context = ""
            if parsed_data.file_format == 'pdf':
                text_context = "\n".join([r.get('text_content', '') for r in parsed_data.get_records()[:3]])
            
            if text_context:
                llm_entities = self.llm_service.analyze_text_for_entities(text_context, self.domain_config.name)
                for item in llm_entities:
                    ent_name = item.get('entity')
                    if ent_name and ent_name not in identified_entities:
                        identified_entities[ent_name] = {
                            'fields': [], # Unstructured discovery doesn't map to specific dataset fields yet
                            'anchor_field': None,
                            'confidence': 0.8,
                            'method': 'llm_discovery',
                            'description': item.get('description')
                        }

        return identified_entities
