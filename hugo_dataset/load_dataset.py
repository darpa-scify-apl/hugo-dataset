import argparse
from typing_extensions import Annotated
from datasets import load_from_disk, load_dataset
from hugo_dataset.evidence import DocumentHandler, Paper
from pydantic import BaseModel, ConfigDict, StringConstraints

from hugo_dataset.logger import get_logger
logger = get_logger("loader", "INFO")

try:
    from rich import print
except:
    pass

class DatasetLoader(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    dataset_location : str
    target_dir : str | None = None
    remote : bool
    allowed_licenses : list[Annotated[str, StringConstraints(to_lower=True)]]
    _doc_handler : DocumentHandler | None = None
    local_dirs : list[str] = []
    sources_mapping : dict[str, str] = {}
    papers : list[Paper] = []
    dataset : any = None
    move : bool = False
    store_file : str | None = None

    @property
    def doc_handler(self):
        if self._doc_handler is None:
            self._doc_handler = DocumentHandler(
                local_dir=self.local_dirs, 
                doc_dir=self.target_dir, 
                move=self.move,
                store_file=self.store_file
                )
        return self._doc_handler

    def load_dataset(self):
        # Load the Hugging Face DatasetDict from disk.
        if not self.dataset:
            if  not self.remote:
                logger.debug("Trying to load from local directory")
                self.dataset = load_from_disk(self.dataset_location)
            else:
                logger.debug("Trying to load from remote directory")
                self.dataset = load_dataset(self.dataset_location)

        self.papers = [Paper.from_metadata(paper) for paper in self.dataset["papers"]]

    def process_papers(self):
        logger.info("\nProcessing papers:")
        self.doc_handler.index(additional_directories=self.local_dirs)

        for paper in self.papers:
            offline=False
            if "all" not in self.allowed_licenses and paper.license_type not in self.allowed_licenses:
                if self.local_dirs:
                    logger.info("License not found, searching local dirs only.")
                    offline = True
                else:
                    logger.info(f"Skipping {paper.id} due to disallowed license '{paper.license_type}'.")
                    continue

            try:
                # Download and verify the paper.
                pdf_path = paper.process(self.doc_handler, offline=offline)
            except Exception as e:
                logger.info(f"Error processing {paper.id}: {e}")

            try:
                if paper.hash == paper.hash:
                    logger.info(f"{paper.id} verified successfully with hash {paper.hash}")
                else:
                    logger.info(f"Hash mismatch for {paper.id}: Expected {paper.hash}, got {paper.hash}")
            except Exception as e:
                logger.info(f"Error computing hash for {paper.id}: {e}")


def main():
    # Configure argument parser.
    parser = argparse.ArgumentParser(
        description="Load dataset and hydrate PDFs for allowed licenses."
    )
    parser.add_argument(
        "--dataset",
        type=str,
        default="data/evidence_dataset",
        help="where to load the dataset from"
    )
    parser.add_argument(
        "--remote",
        action='store_true',
        default=False,
        help="Load from huggingface (default: False)"
    )

    parser.add_argument(
        "--local-dir",
        metavar="L",
        nargs="+",
        default=[],
        type=str,
        help="local directories containing evidence files"
    )
    parser.add_argument(
        "--allowed-licenses",
        nargs="+",
        required=True,
        help="List of allowed licenses (e.g., 'CC BY 4.0', 'ACL License')"
    )

    parser.add_argument(
        "--target-dir",
        type=str,
        default="data/docs",
        help="Where to store data documents"
    )

    parser.add_argument(
        "--move",
        action="store_true",
        default=False,
        help="move files when processing data instead of copying (use at your own risk for now)"
    )

    parser.add_argument(
        "--store_file",
        default=None,
        type=str,
        help="A json mapping from id to filepath"
    )
    args = parser.parse_args()
    allowed_licenses = [e.lower() for e in args.allowed_licenses]

    # Path to the dataset on disk
    dataset_location = args.dataset
    local_dirs = args.local_dir
    remote = args.remote
    target_dir = args.target_dir
    move = args.move
    store_file = args.store_file

    # Initialize and load DatasetLoader
    dataset_loader = DatasetLoader(dataset_location=dataset_location,
                                   target_dir=target_dir,
                                   allowed_licenses=allowed_licenses, 
                                   local_dirs=local_dirs, 
                                   remote=remote,
                                   move=move,
                                   store_file=store_file
                                   )
    dataset_loader.load_dataset()

    # Process papers with allowed licenses
    dataset_loader.process_papers()
    print(dataset_loader.dataset)
    print(dataset_loader.papers)


if __name__ == "__main__":
    main()
