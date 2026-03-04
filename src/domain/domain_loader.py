"""
Step 6: Domain Knowledge Loader Module
Loads specific rules and entity mappings for a detected domain.
"""
import os
import json
from typing import Dict, List, Optional

class DomainConfig:
    """Formal object representing the knowledge of a domain."""
    def __init__(self, data: Dict):
        self.name = data.get("domain_name", "Generic")
        self.keywords = data.get("keywords", [])
        self.entities = data.get("entities", [])
        self.mappings = data.get("mappings", {})  # Entity-to-field mappings
        self.relationships = data.get("relationships", []) # New for Phase 4

    def get_fields_for_entity(self, entity_name: str) -> List[str]:
        return self.mappings.get(entity_name, [])

    def __repr__(self):
        return f"<DomainConfig name='{self.name}' entities={len(self.entities)}>"

class DomainLoader:
    """Loads domain-specific configuration files into DomainConfig objects."""

    def __init__(self, rules_dir: str = "config/domain_rules"):
        self.rules_dir = rules_dir

    def load(self, domain_name: str) -> DomainConfig:
        """Loads the JSON rule file for the given domain name."""
        if domain_name == "Generic":
             return DomainConfig(self._get_generic_rules())

        filename = f"{domain_name.lower()}.json"
        path = os.path.join(self.rules_dir, filename)

        if not os.path.exists(path):
            return DomainConfig(self._get_generic_rules())

        with open(path, "r") as f:
            try:
                data = json.load(f)
                return DomainConfig(data)
            except json.JSONDecodeError:
                return DomainConfig(self._get_generic_rules())

    def _get_generic_rules(self) -> Dict:
        """Returns a minimal set of generic rules."""
        return {
            "domain_name": "Generic",
            "keywords": [],
            "entities": ["Thing"],
            "mappings": {}
        }
