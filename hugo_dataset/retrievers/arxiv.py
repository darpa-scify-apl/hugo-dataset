import re
import requests
import xml.etree.ElementTree as ET
from .base import Retriever

class arxiv(Retriever):
    source = "arxiv"

    @classmethod
    def id_from_url(cls, url):
        match = re.search(r'arxiv.org/(?:abs|pdf)/([a-zA-Z0-9.]+)', url)
        if not match:
            raise ValueError("Invalid arXiv URL format.")
        arxiv_id = match.group(1)
        if arxiv_id.endswith(".pdf"):
            arxiv_id = arxiv_id[:-4]
        return arxiv_id

    @classmethod
    def get(cls, id, **kwargs):
        metadata_url = f"http://export.arxiv.org/api/query?id_list={id}"
        response = requests.get(metadata_url)
        if response.status_code != 200:
            raise ValueError(f"Unable to fetch metadata for arXiv ID {id}.")
        try:
            root = ET.fromstring(response.content)
            entry = root.find("{http://www.w3.org/2005/Atom}entry")
            if entry is None:
                raise ValueError(f"No metadata found for arXiv ID {id}.")
            title = entry.find("{http://www.w3.org/2005/Atom}title").text.strip()
            abstract = entry.find("{http://www.w3.org/2005/Atom}summary").text.strip()
            year = entry.find("{http://www.w3.org/2005/Atom}published").text.strip().split("-")[0]
        except Exception as e:
            raise ValueError(f"Error parsing metadata for arXiv ID {id}: {e}")
        return dict(
            id=id,
            url=f"https://arxiv.org/pdf/{id}.pdf",
            source=cls.source,
            title=title,
            abs=abstract,
            year=year
        )
