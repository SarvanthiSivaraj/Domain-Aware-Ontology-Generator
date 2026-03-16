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

    def __init__(self, output_base_dir: str = "output"):
        """
        Initialize the OWLExporter.

        Args:
            output_base_dir: Base directory for all generated outputs.
        """
        self.output_base_dir = output_base_dir

    def export(self, ontology: Ontology, domain_name: str, source_filename: str = None) -> str:
        """
        Export the ontology to an OWL file.

        Args:
            ontology: The Owlready2 ontology object to export.
            domain_name: Name of the domain (used in the folder name).
            source_filename: Original source file name (used in output filename if provided).

        Returns:
            str: Absolute path to the generated .owl file.
        """
        # Sub-folder per domain for better organization
        domain_dir = os.path.join(self.output_base_dir, domain_name.lower())
        os.makedirs(domain_dir, exist_ok=True)

        # Build the output filename
        if source_filename:
            # Use source name (without extension) if provided
            base_name = os.path.splitext(os.path.basename(source_filename))[0]
            filename = f"{base_name}_ontology.owl"
        else:
            filename = f"{domain_name.lower()}_ontology.owl"
            
        output_path = os.path.join(domain_dir, filename)

        # Serialize to RDF/XML format
        ontology.save(file=output_path, format="rdfxml")

        return os.path.abspath(output_path)
