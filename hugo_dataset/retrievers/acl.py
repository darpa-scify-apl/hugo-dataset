import re
import requests
from bs4 import BeautifulSoup
from .base import Retriever

class acl(Retriever):
    source = "acl anthology"
    license = "acl"

    @classmethod
    def id_from_url(cls, url):
        match = re.search(r'aclanthology.org/([a-zA-Z0-9.\-]+)', url)
        if not match:
            raise ValueError("Invalid ACL Anthology URL format.")
        acl_id = match.group(1)
        if acl_id.endswith(".pdf"):
            acl_id = acl_id[:-4]
        return acl_id

    @classmethod
    def get(cls, id, **kwargs):
        paper_url = f"https://aclanthology.org/{id}"
        response = requests.get(paper_url)
        if response.status_code != 200:
            raise ValueError(f"Failed to fetch ACL Anthology page: {response.status_code}")
        soup = BeautifulSoup(response.text, 'html.parser')
        title_tag = soup.find('h2', id="title")
        title = title_tag.text.strip() if title_tag else ""
        abstract_tag = soup.find('div', class_="card-body acl-abstract")
        abstract = abstract_tag.text.strip() if abstract_tag else ""
        dt_tag = soup.find('dt', text='Year:')
        year = None
        if dt_tag:
            dd_tag = dt_tag.find_next_sibling('dd')
            if dd_tag:
                year = dd_tag.text.strip()
        return dict(
            title=title,
            abs=abstract,
            id=id,
            url=paper_url,
            source=cls.source,
            year=year
        )
