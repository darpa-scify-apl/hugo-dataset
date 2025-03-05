import json
import os
#import shutil 
#import requests 
import hashlib
from hugo_dataset import retrievers
from pydantic import BaseModel, ConfigDict, StringConstraints
from typing_extensions import Annotated

from hugo_dataset.logger import get_logger
logger = get_logger("evidence")

DEFAULT_LICENSES = lambda x: retrievers.GETTERS.get(x, retrievers.base.Retriever).license
UNKNOWN_LICENSE = DEFAULT_LICENSES("None")

class DocumentHandler(BaseModel): 
    doc_dir : str = "data/docs"
    local_dir : str | list[str] = []
    store_file : str | None = None
    _local_store : dict[str, str] | None = None
    move : bool = False # Whether a file should be copied or moved.

    @property
    def local_store(self):
        if self._local_store is None:
            if not self.store_file:
                self.store_file = os.path.join(self.doc_dir, ".store.json")
            if os.path.isfile(self.store_file):
                with open(self.store_file) as inp:
                    try:
                        self._local_store = json.load(inp)
                    except:
                        logger.info("Failed to load index from {self.store_file}.")
                        self._local_store = {}
            else:
                self._local_store = {}
        return self._local_store
    
    def close(self):
        """WARNING: Your index will be overwritten when you call close()"""
        with open(self.store_file, 'w') as out:
            logger.debug(self._local_store)
            json.dump(self._local_store, out)
    
    def index(self, additional_directories: list[str] | None=None):
        """
        re-index the doc dir. Do not remove non-existent files.
        """
        indexes = [self.doc_dir]
        if type(self.local_dir) == str:
            indexes.append(self.local_dir)
        elif type(self.local_dir) == list:
            indexes += [l for l in self.local_dir]
        if additional_directories:
            # Add the destination location last to reduce unnecessary copying
            indexes = additional_directories + indexes
        for _dir in indexes:
            logger.debug(f"indexing documents in {_dir}")
            found = 0
            updated = 0
            pre = len(self.local_store)
            for d, sub, f in os.walk(_dir):
                for _f in f:
                    id = os.path.splitext(_f)[0]
                    existing = self.local_store.get(id)
                    self.local_store[id] = os.path.join(d, _f)
                    found += 1
                    updated += 1 if existing != self.local_store[id] else 0
            logger.info(f"Found {found} files in {_dir}. Updated {updated} out of {pre} provided file paths")

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

    def hydrate(self, paper, local_dir=None, ext='pdf', offline=False):
        """
        Download the PDF for the given paper.
        The file is saved under a hierarchical directory structure based on the paper license and source.
        """
        # Use the paper’s license field or default to 'unknown'
        license_type = (paper.license_type or UNKNOWN_LICENSE).lower()
        source = (paper.source or UNKNOWN_LICENSE).lower()
        paper_id = paper.id
        doc_url = paper.url
        
        # Create directories: doc_dir/license/source
        target_dir = os.path.join(self.doc_dir, license_type, source)
        os.makedirs(target_dir, exist_ok=True)

        local_dir = self.local_store.get(paper_id, local_dir)
        if local_dir and not os.path.exists(local_dir):
            logger.info(f"Warning: A doc path was provided for {paper_id} but the file was not found.")

        logger.info(f"retrieving {doc_url} from {local_dir if local_dir else doc_url}")
        ret = retrievers.get_document(source, doc_url, target=target_dir, local_dir=local_dir, offline=offline)
        logger.info(f"hydration - retrieved to {ret}")
        return ret

class Evidence(BaseModel):
    pass

class Paper(Evidence): 
    model_config = ConfigDict(coerce_numbers_to_str=True)
    
    id : str
    url : str
    source : Annotated[str, StringConstraints(to_lower=True)]
    year : str | None = None
    license_type : Annotated[str, StringConstraints(to_lower=True)] = UNKNOWN_LICENSE
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

    def process(self, document_handler: DocumentHandler, offline=False):
        """
        Download the paper's PDF and compute its hash.
        """
        if self.license_type == UNKNOWN_LICENSE:
            self.license_type = DEFAULT_LICENSES(self.source)
            
        logger.info(f"Hydrating {self.source}-{self.id}")
        doc_path = document_handler.hydrate(self)

        if not self.title or not self.abs:
            logger.info(f"retrieving metadata: {self.id}")
            try:
                data = retrievers.get(self.source, self.id)
                self.title = data['title']
                self.abs = data['abs']
            except Exception as e:
                logger.debug(f"Failed to retrieve metadata for {self.id}: {e}")

        if doc_path:
            logger.info(f"Computing hash for {self.id}")
            self.hash = document_handler.compute_hash(doc_path)
        else:
            logger.info(f"Unable to compute hash for {self.id}, no file found")
        return doc_path



