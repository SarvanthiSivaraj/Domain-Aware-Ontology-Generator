"""
Step 9: Relationship Detection Module
Infers Object Properties (links between entities) using domain-configured rules
and automatic foreign key inference.
"""
from typing import Dict, Any, List
from src.core.parsed_data import ParsedData
from src.domain.domain_loader import DomainConfig
from src.core.llm_service import LLMService


class RelationshipDetector:
    """
    Detects relationships (Object Properties) between identified entities.

    Uses two strategies:
    1. Domain-configured relationships — explicit rules from the domain config.
    2. Foreign key inference — if Entity A contains Entity B's anchor field,
       infer a link A → B.
    """

    def detect(
        self,
        entities: Dict[str, Dict[str, Any]],
        domain_config: DomainConfig,
        parsed_data: ParsedData,
        llm_service: LLMService = None
    ) -> List[Dict[str, Any]]:
        """
        Detect relationships between identified entities.

        Args:
            entities: Output of Step 7 — EntityName -> {fields, anchor_field, confidence}
            domain_config: The active DomainConfig with optional relationship rules.
            parsed_data: The ParsedData object.

        Returns:
            List of relationship dicts, each with:
                - source: source entity name
                - target: target entity name
                - property_name: OWL Object Property name
                - via_field: the linking field
                - detection_method: 'domain_rule' or 'foreign_key_inference'
        """
        relationships = []
        seen = set()  # Track (source, target, via_field) to avoid duplicates

        # --- Strategy 1: Domain-configured relationships ---
        for rule in domain_config.relationships:
            source = rule.get("source")
            target = rule.get("target")
            prop = rule.get("property_name")
            via = rule.get("via_field")

            # Only include if both entities were identified in the dataset
            if source in entities and target in entities:
                key = (source, target, via)
                if key not in seen:
                    relationships.append({
                        "source": source,
                        "target": target,
                        "property_name": prop,
                        "via_field": via,
                        "detection_method": "domain_rule",
                    })
                    seen.add(key)

        # --- Strategy 2: Foreign key inference ---
        # Build a map of anchor_field -> entity_name for quick lookup
        anchor_to_entity = {}
        for ent_name, info in entities.items():
            anchor = info.get("anchor_field")
            if anchor:
                anchor_to_entity[anchor] = ent_name

        # For each entity, check if any of its fields match another entity's anchor
        for ent_name, info in entities.items():
            for field in info.get("fields", []):
                # Skip the entity's own anchor
                if field == info.get("anchor_field"):
                    continue

                if field in anchor_to_entity:
                    target_entity = anchor_to_entity[field]
                    # Don't create a self-relationship
                    if target_entity == ent_name:
                        continue

                    key = (ent_name, target_entity, field)
                    if key not in seen:
                        # Generate a default property name: "relatedTo{Target}"
                        prop_name = f"relatedTo{target_entity}"
                        relationships.append({
                            "source": ent_name,
                            "target": target_entity,
                            "property_name": prop_name,
                            "via_field": field,
                            "detection_method": "foreign_key_inference",
                        })
                        seen.add(key)

        # --- Strategy 3: LLM Inference ---
        if llm_service and llm_service.is_available():
            text_context = ""
            if parsed_data.file_format == 'pdf':
                text_context = "\n".join([r.get('text_content', '') for r in parsed_data.get_records()[:3]])
            
            if text_context:
                llm_rels = llm_service.infer_relationships(list(entities.keys()), text_context)
                for rel in llm_rels:
                    source = rel.get("source")
                    target = rel.get("target")
                    prop = rel.get("property")
                    
                    if source in entities and target in entities:
                        key = (source, target, prop)
                        if key not in seen:
                            relationships.append({
                                "source": source,
                                "target": target,
                                "property_name": prop,
                                "via_field": "llm_inferred",
                                "detection_method": "llm_inference",
                                "description": rel.get("description")
                            })
                            seen.add(key)

        return relationships
