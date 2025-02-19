import os 
from . import retrievers
import requests 
import hashlib
from pydantic import BaseModel, ConfigDict, StringConstraints
from typing_extensions import Annotated

DEFAULT_LICENSES = {
    "arxiv": "cc by 4.0", 
    "acl anthology": "acl license"
}

class PDFHandler(BaseModel): 
    pdf_dir : str = "data/pdfs"

    def compute_hash(self, file_path, hash_algo="md5"):
        """
        Compute the hash of a file using a given algorithm.
        """
        if hash_algo == "md5":
            hasher = hashlib.md5()
        elif hash_algo == "sha256":
            hasher = hashlib.sha256()
        else:
            raise ValueError("Unsupported hash algorithm.")

        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    def hydrate(self, paper):
        """
        Download the PDF for the given paper.
        The file is saved under a hierarchical directory structure based on the paper license and source.
        """
        # Use the paper’s license field or default to 'unknown'
        license_type = (paper.license_type or "unknown").lower()
        source = (paper.source or "unknown").lower()
        paper_id = paper.id
        pdf_url = paper.url

        # Create directories: pdf_dir/license/source
        target_dir = os.path.join(self.pdf_dir, license_type, source)
        os.makedirs(target_dir, exist_ok=True)

        pdf_path = os.path.join(target_dir, f"{paper_id}.pdf")
        response = requests.get(pdf_url)
        if response.status_code == 200:
            with open(pdf_path, "wb") as f:
                f.write(response.content)
            return pdf_path
        else:
            raise Exception(f"Failed to download PDF from {pdf_url}")

class Paper(BaseModel): 
    model_config = ConfigDict(coerce_numbers_to_str=True)
    
    id : str
    url : str
    source : Annotated[str, StringConstraints(to_lower=True)]
    year : str | None = None
    license_type : Annotated[str, StringConstraints(to_lower=True)] = "unknown"
    hash : str | None = None
    title : str | None = None
    abs : str | None = None
    
    @classmethod
    def from_metadata(cls, metadata):
        """
        Create a Paper instance from a dictionary containing metadata.
        """
        return cls(**metadata)

    @classmethod
    def from_url(cls, url):
        """
        Create a Paper instance by parsing an arXiv or ACL Anthology url.
        """
        if "arxiv.org" in url:
            # Try to extract the arXiv id.
            return cls(**retrievers.arxiv.from_url(url))
        elif "aclanthology.org" in url:
            # Try to extract the ACL Anthology id.
            return cls(**retrievers.acl.from_url(url)) 
        else:
            raise ValueError("url must be either an arXiv or ACL Anthology link.")

    def process(self, pdf_handler):
        """
        Download the paper's PDF and compute its hash.
        """
        if self.license_type == "unknown":
            self.license_type = DEFAULT_LICENSES.get(self.source, "unknown")
            
        pdf_path = pdf_handler.hydrate(self)
        if not self.title or not self.abs:
            data = retrievers.get(self.source, self.id)
            self.title = data['title']
            self.abs = data['abs']
        self.hash = pdf_handler.compute_hash(pdf_path)
        return pdf_path



