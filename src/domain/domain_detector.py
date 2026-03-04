"""
Step 5: Domain Detection Module
Identifies the domain of a dataset based on field names and content.
"""
import os
import json
from typing import Dict, List, Tuple, Optional

class DomainDetector:
    """Detects the domain of a dataset using keyword matching."""

    def __init__(self, rules_dir: str = "config/domain_rules"):
        self.rules_dir = rules_dir
        self.domains = self._load_rules()

    def _load_rules(self) -> List[Dict]:
        """Loads all domain JSON rules from the config directory."""
        domain_rules = []
        if not os.path.exists(self.rules_dir):
            return domain_rules

        for filename in os.listdir(self.rules_dir):
            if filename.endswith(".json"):
                with open(os.path.join(self.rules_dir, filename), "r") as f:
                    try:
                        rule = json.load(f)
                        domain_rules.append(rule)
                    except json.JSONDecodeError:
                        continue
        return domain_rules

    def detect(self, field_names: List[str]) -> Tuple[str, float]:
        """
        Detects the domain based on field name similarity to keywords.
        Returns (Domain Name, Confidence Score).
        """
        best_domain = "Generic"
        max_score = 0.0

        if not self.domains:
            return best_domain, 0.0

        for domain_rule in self.domains:
            score = 0
            keywords = domain_rule.get("keywords", [])
            
            for field in field_names:
                field_lower = field.lower()
                for kw in keywords:
                    if kw in field_lower:
                        score += 1
            
            # Normalize score (count of matches vs count of total fields)
            # This is a simple heuristic; can be improved.
            norm_score = score / len(field_names) if field_names else 0

            if norm_score > max_score:
                max_score = norm_score
                best_domain = domain_rule.get("domain_name", "Generic")

        # Threshold for detection
        if max_score < 0.1:
            return "Generic", max_score

        return best_domain, max_score
