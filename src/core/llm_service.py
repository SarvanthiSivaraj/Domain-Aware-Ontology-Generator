"""
LLM Service Module

Interacts with Gemini API to provide semantic reasoning, entity mapping,
and relationship inference for the ontology generation pipeline.
"""

import os
from google import genai
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class LLMService:
    """
    Service for interacting with Gemini API.
    
    Provides capabilities for:
    - Identifying classes and properties from text
    - Mapping dataset fields to ontological concepts
    - Inferring relationships between entities
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the LLM service.
        
        Args:
            api_key: Gemini API key. If None, looks for GEMINI_API_KEY in .env
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if self.api_key:
            try:
                self.client = genai.Client(api_key=self.api_key)
                self.model_id = 'gemini-1.5-flash'
            except Exception as e:
                print(f"Error initializing Gemini client: {e}")
                self.client = None
        else:
            self.client = None
            print("WARNING: Gemini API key not found. LLM-based features will be disabled.")
            
    def is_available(self) -> bool:
        """Check if the LLM service is available and configured."""
        return self.client is not None

    def analyze_text_for_entities(self, text: str, domain: str) -> List[Dict[str, Any]]:
        """
        Analyze text to identify potential ontology entities and attributes.
        
        Args:
            text: Unstructured text to analyze
            domain: The suspected domain (e.g., Cybersecurity)
            
        Returns:
            List of identified entities and their suggested properties
        """
        if not self.is_available():
            return []
            
        prompt = f"""
        Analyze the following text from the {domain} domain.
        Identify the core entities (Classes) and their attributes (Data Properties).
        Format the output as a JSON list of objects:
        [{{ "entity": "ClassName", "attributes": ["attr1", "attr2"], "description": "brief description" }}]
        
        Text:
        {text[:4000]}  # Trim to avoid token limits
        """
        
        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt
            )
            # Basic JSON extraction
            content = response.text
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
                
            import json
            return json.loads(content)
        except Exception as e:
            print(f"Error in LLM entity analysis: {str(e)}")
            return []

    def infer_relationships(self, entities: List[str], text: str) -> List[Dict[str, Any]]:
        """
        Infer relationships (Object Properties) between identified entities.
        
        Args:
            entities: List of entity names
            text: Source text for context
            
        Returns:
            List of relationship objects
        """
        if not self.is_available():
            return []
            
        entities_str = ", ".join(entities)
        prompt = f"""
        Given the following entities: {entities_str}
        Identify relationships (Object Properties) between them based on this text:
        {text[:4000]}
        
        Format the output as a JSON list:
        [{{ "source": "EntityA", "target": "EntityB", "property": "hasRelationship", "description": "context" }}]
        """
        
        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt
            )
            content = response.text
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            import json
            return json.loads(content)
        except Exception as e:
            print(f"Error in LLM relationship inference: {str(e)}")
            return []
