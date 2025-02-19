from datasets import Dataset, DatasetDict 
from .evidence import PDFHandler, Paper
from pydantic import BaseModel

class DatasetManager(BaseModel): 
  sources : list[dict[str, str]] = [ 
      {"source": "arxiv", "license_type": "CC BY 4.0"}, 
      {"source": "acl anthology", "license_type": "ACL License"} 
    ] 
  # Define an initial list of Paper objects. 
  papers : list[Paper]
  pdf_handler : PDFHandler = PDFHandler()
  dataset_dir: str ="data/evidence_dataset"

  def process_all(self):
    """
    Process (download and compute hash for) all papers in the list.
    """
    for paper in self.papers:
        try:
            pdf_path = paper.process(self.pdf_handler)
            print(f"Processed {paper.id}, computed hash: {paper.hash}")
        except Exception as e:
            print(f"Error processing {paper.id}: {e}")

  def add_paper_from_url(self, url):
    """
    Add and process a new paper from a given URL (arXiv or ACL Anthology).
    """
    try:
        paper = Paper.from_url(url)
        paper.process(self.pdf_handler)
        self.papers.append(paper)
        print(f"Added paper {paper.id} with hash: {paper.hash}")
    except Exception as e:
        print(f"Failed to add paper from {url}: {e}")

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
    print(f"Dataset successfully saved to '{self.dataset_dir}'")

def main(): 
  manager = DatasetManager(papers=[ 
    Paper( id="1809.09600", url="https://arxiv.org/pdf/1809.09600.pdf", source="arXiv", year="2018"), 
    Paper( id="2009.07758", url="https://arxiv.org/pdf/2009.07758.pdf", source="arXiv", year="2020"), 
    Paper( id="N19-1423", url="https://aclanthology.org/N19-1423.pdf", source="ACL Anthology", year="2019") ],
    pdf_handler=PDFHandler(pdf_dir="data/cpdfs")
    ) # Process the predefined list of papers.
  manager.process_all()
  # Add new papers directly by url.
  print("\nAdding a new paper from an arXiv url...")
  manager.add_paper_from_url("https://arxiv.org/pdf/2301.12345.pdf")

  print("\nAdding a new paper from an ACL Anthology url...")
  manager.add_paper_from_url("https://aclanthology.org/P16-1174")

  # Save the dataset.
  manager.save_dataset()

if __name__ == "__main__": 
  main()