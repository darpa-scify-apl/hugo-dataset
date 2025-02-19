import argparse
from typing_extensions import Annotated
from datasets import load_from_disk
from .evidence import PDFHandler, Paper
from pydantic import BaseModel, ConfigDict, StringConstraints

from . import logger
logger = logger.getChild("loader")

try:
    from rich import print
except:
    pass

class DatasetLoader(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    dataset_dir : str
    allowed_licenses : list[Annotated[str, StringConstraints(to_lower=True)]]
    pdf_handler : PDFHandler = PDFHandler()
    sources_mapping : dict[str, str] = {}
    papers : list[Paper] = []
    dataset : any = None

    def load_dataset(self):
        # Load the Hugging Face DatasetDict from disk.
        if not self.dataset:
            self.dataset = load_from_disk(self.dataset_dir)

        self.papers = [Paper.from_metadata(paper) for paper in self.dataset["papers"]]

    def process_papers(self):
        logger.info("\nProcessing papers:")

        for paper in self.papers:
            if "all" in self.allowed_licenses or paper.license_type not in self.allowed_licenses:
                logger.info(f"Skipping {paper.id} due to disallowed license '{paper.license_type}'.")
                continue

            try:
                # Download and verify the paper.
                pdf_path = paper.process(self.pdf_handler)

                if paper.hash == paper.hash:
                    logger.info(f"{paper.id} verified successfully with hash {paper.hash}")
                else:
                    logger.info(f"Hash mismatch for {paper.id}: Expected {paper.hash}, got {paper.hash}")
            except Exception as e:
                logger.info(f"Error processing {paper.id}: {e}")


def main():
    # Configure argument parser.
    parser = argparse.ArgumentParser(
        description="Load dataset and hydrate PDFs for allowed licenses."
    )
    parser.add_argument(
        "--allowed-licenses",
        nargs="+",
        required=True,
        help="List of allowed licenses (e.g., 'CC BY 4.0', 'ACL License')"
    )
    args = parser.parse_args()
    allowed_licenses = [e.lower() for e in args.allowed_licenses]

    # Path to the dataset on disk
    dataset_dir = "data/evidence_dataset"

    # Initialize and load DatasetLoader
    dataset_loader = DatasetLoader(dataset_dir=dataset_dir, allowed_licenses=allowed_licenses)
    dataset_loader.load_dataset()

    # Process papers with allowed licenses
    dataset_loader.process_papers()
    print(dataset_loader.dataset)
    print(dataset_loader.papers)


if __name__ == "__main__":
    main()
