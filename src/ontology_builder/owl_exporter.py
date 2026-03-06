"""
Step 12: OWL File Generation Module
Serializes the constructed ontology (with individuals) to an OWL/RDF-XML file.
"""
import os
from owlready2 import Ontology


class OWLExporter:
    """
    Step 12: Exports the OWL ontology to a .owl file.

    Serializes the Owlready2 ontology object into OWL/RDF-XML format
    and saves it to the output directory.
    """

    def __init__(self, output_dir: str = "output"):
        """
        Initialize the OWLExporter.

        Args:
            output_dir: Directory to save the generated .owl file.
        """
        self.output_dir = output_dir

    def export(self, ontology: Ontology, domain_name: str) -> str:
        """
        Export the ontology to an OWL file.

        Args:
            ontology: The Owlready2 ontology object to export.
            domain_name: Name of the domain (used in the filename).

        Returns:
            str: Absolute path to the generated .owl file.
        """
        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)

        # Build the output filename
        filename = f"{domain_name.lower()}_ontology.owl"
        output_path = os.path.join(self.output_dir, filename)

        # Serialize to RDF/XML format
        ontology.save(file=output_path, format="rdfxml")

        return os.path.abspath(output_path)
