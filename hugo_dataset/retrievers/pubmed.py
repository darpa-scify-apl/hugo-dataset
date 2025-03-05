import re
import requests
from .base import Retriever

class pubmed(Retriever):
    source = "pubmed"
    extension = "pdf"
    license = "pubmed"

    @classmethod
    def id_from_url(cls, url):
        match = re.search(r'pubmed\.ncbi\.nlm\.nih\.gov/(\d+)', url)
        if not match:
            raise ValueError("Invalid PubMed URL format.")
        return match.group(1)

    @classmethod
    def get(cls, id, **kwargs):
        raise ValueError("PubMed terms and conditions prevents use of this function")
        return False
        api_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={id}&retmode=json"
        response = requests.get(api_url)
        if response.status_code != 200:
            raise ValueError(f"Failed to fetch PubMed metadata for id {id}")
        data = response.json()
        result = data.get("result", {}).get(id)
        if not result:
            raise ValueError(f"No metadata found for PubMed ID {id}")
        title = result.get("title", "")
        pubdate = result.get("pubdate", "")
        year = None
        if pubdate:
            match_year = re.search(r'(\d{4})', pubdate)
            if match_year:
                year = match_year.group(1)
        return dict(
            id=id,
            url=f"https://pubmed.ncbi.nlm.nih.gov/{id}/",
            source=cls.source,
            title=title,
            abs="",
            year=year
        )
