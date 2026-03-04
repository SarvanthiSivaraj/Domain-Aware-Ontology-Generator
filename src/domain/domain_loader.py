"""
Step 6: Domain Knowledge Loader Module
Loads specific rules and entity mappings for a detected domain.
"""
import os
import json
from typing import Dict, Optional

class DomainLoader:
    """Loads domain-specific configuration files."""

    def __init__(self, rules_dir: str = "config/domain_rules"):
        self.rules_dir = rules_dir

    def load(self, domain_name: str) -> Optional[Dict]:
        """Loads the JSON rule file for the given domain name."""
        if domain_name == "Generic":
             return self._get_generic_rules()

        filename = f"{domain_name.lower()}.json"
        path = os.path.join(self.rules_dir, filename)

        if not os.path.exists(path):
            return self._get_generic_rules()

        with open(path, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return self._get_generic_rules()

    def _get_generic_rules(self) -> Dict:
        """Returns a minimal set of generic rules."""
        return {
            "domain_name": "Generic",
            "keywords": [],
            "entities": ["Thing"],
            "mappings": {}
        }
