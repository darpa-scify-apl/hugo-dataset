from datasets import Dataset, DatasetDict 
from hugo_dataset.evidence import DocumentHandler, Paper
from pydantic import BaseModel

from hugo_dataset.logger import get_logger
logger = get_logger(__name__ + ".create_dataset")

class DatasetManager(BaseModel): 
  # Define an initial list of Paper objects. 
  papers : list[Paper]
  document_handler : DocumentHandler = DocumentHandler()
  dataset_dir: str ="data/evidence_dataset"

  def process_all(self, additional_directories : list[str]=None, store_file : str = None):
    """
    Process (download and compute hash for) all papers in the list.
    """
    self.document_handler.store_file=store_file
    self.document_handler.index(additional_directories=additional_directories)
    for paper in self.papers:
        try:
            path = paper.process(self.document_handler)
            logger.info(f"Processed {paper.id}, computed hash: {paper.hash}")
        except Exception as e:
            logger.debug(f"Error processing {paper.id}: {e}")
    self.document_handler.close()

  def add_paper_from_url(self, url):
    """
    Add and process a new paper from a given URL (arXiv or ACL Anthology).
    """
    try:
        paper = Paper.from_url(url)
        paper.process(self.document_handler)
        logger.info(f"Added paper {paper.id} with hash: {paper.hash}")
        self.papers.append(paper)
    except Exception as e:
        logger.debug(f"Failed to add paper from {url}: {e}")

  def save_dataset(self):
    """
    Convert the papers list and sources into a DatasetDict and save
    the dataset to disk.
    """
    # Convert each Paper instance to its dictionary representation.
    papers_data = [paper.__dict__ for paper in self.papers]
    papers_dataset = Dataset.from_list(papers_data)
    #sources_dataset = Dataset.from_list(self.sources)
    dataset = DatasetDict({
        "papers": papers_dataset,
    })
    dataset.save_to_disk(self.dataset_dir)
    logger.info(f"Dataset successfully saved to '{self.dataset_dir}'")

def main(): 
  manager = DatasetManager(papers=[ 
    Paper( id="1809.09600", url="https://arxiv.org/pdf/1809.09600.pdf", source="arXiv", year="2018"), 
    Paper( id="2009.07758", url="https://arxiv.org/pdf/2009.07758.pdf", source="arXiv", year="2020"), 
    Paper( id="N19-1423", url="https://aclanthology.org/N19-1423.pdf", source="ACL Anthology", year="2019") ],
    document_handler=DocumentHandler(doc_dir="data/cpdfs")
    ) # Process the predefined list of papers.
  manager.process_all(additional_directories=["data/arxiv_sample"])
  # Add new papers directly by url.
  logger.info("\nAdding a new paper from an arXiv url...")
  manager.add_paper_from_url("https://arxiv.org/pdf/2301.12345.pdf")

  logger.info("\nAdding a new paper from an ACL Anthology url...")
  manager.add_paper_from_url("https://aclanthology.org/P16-1174")

  # Save the dataset.
  manager.save_dataset()

if __name__ == "__main__": 
  main()