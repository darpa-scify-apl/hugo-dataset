import re
import requests
from .base import Retriever

class wikipedia(Retriever):
    source = "wikipedia"
    extension = "txt"

    @classmethod
    def id_from_url(cls, url):
        match = re.search(r'wikipedia\.org/wiki/([^#?]+)', url)
        if not match:
            raise ValueError("Invalid Wikipedia URL format.")
        return match.group(1)

    @classmethod
    def get(cls, id):
        api_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{id}"
        response = requests.get(api_url)
        if response.status_code != 200:
            raise ValueError(f"Failed to fetch Wikipedia article summary: {response.status_code}")
        data = response.json()
        title = data.get("title", "")
        summary = data.get("extract", "")
        return dict(
            id=id,
            url=data.get("content_urls", {}).get("desktop", {}).get("page", api_url),
            source=cls.source,
            title=title,
            abs=summary,
            year=None  # Wikipedia does not have a publication year.
        )
