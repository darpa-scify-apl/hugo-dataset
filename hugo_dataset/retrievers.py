import re
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import requests


class Retriever:
    source : str = "None"

    @classmethod
    def id_from_url(cls, url):
        pass

    @classmethod
    def from_url(cls, url):
        return cls.get(cls.id_from_url(url))
    
    @classmethod
    def get(cls, id):
        pass


class acl(Retriever):
    source : str = "acl anthology"

    @classmethod
    def id_from_url(cls, url):
        # Ensure the URL is valid and extract the ACL ID
        match = re.search(r'aclanthology.org/([a-zA-Z0-9.\-]+)', url)
        if not match:
            raise ValueError("Invalid ACL Anthology URL format.")
        acl_id = match.group(1)

        if acl_id.endswith(".pdf"):  # Remove ".pdf" if in the URL
            acl_id = acl_id[:-4]
        return acl_id

    @classmethod
    def get(cls, id):
        # URL for the paper page (not the PDF)
        paper_url = f"https://aclanthology.org/{id}"
    
        # Send a GET request to fetch the page
        response = requests.get(paper_url)
        if response.status_code != 200:
            raise ValueError(f"Failed to fetch ACL Anthology page: {response.status_code}")
    
        # Parse the page using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
    
        # Extract title
        title_tag = soup.find('h2', id="title")
        title = title_tag.text.strip() if title_tag else ""
    
        # Extract abstract
        abstract_tag = soup.find('div', class_="card-body acl-abstract")
        abstract = abstract_tag.text.strip() if abstract_tag else ""

        dt_tag = soup.find('dt', text='Year:')

        # Get the corresponding <dd> tag (the next sibling)
        if dt_tag:
            dd_tag = dt_tag.find_next_sibling('dd')
        if dd_tag:
            year = dd_tag.text.strip()
    
        return dict(
            title=title,
            abs=abstract,
            id=id,
            url=paper_url,
            source="acl anthology",
            year=year
        )

class arxiv(Retriever):
    source : str = "arxiv"

    @classmethod
    def id_from_url(cls, url):
        match = re.search(r'arxiv.org/(?:abs|pdf)/([a-zA-Z0-9.]+)', url)
        if not match:
            raise ValueError("Invalid arXiv URL format.")
        arxiv_id =  match.group(1)
        if arxiv_id.endswith(".pdf"):
            arxiv_id = arxiv_id[:-4]
        return arxiv_id

    @classmethod
    def get(cls, id):
        # Use the arXiv ID to fetch metadata through the API.
        metadata_url = f"http://export.arxiv.org/api/query?id_list={id}"
        response = requests.get(metadata_url)
        if response.status_code != 200:
            raise ValueError(f"Unable to fetch metadata for arXiv ID {id}.")

        # Parse the XML response to extract needed information.
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
            source="arxiv",
            title=title,
            abs=abstract,
            year=year
        )

GETTERS = {"arxiv": arxiv, 'acl anthology': acl}

def get(source, id):
    g = GETTERS.get(source)
    if not g:
        raise NotImplementedError(f"No getter for {source} has been implemented")
    return g.get(id)