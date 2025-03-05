import os
import shutil
import requests
import re

from .base import Retriever

class aps(Retriever):
    source : str = "aps"
    extension : str = "pdf"
    license = "aps"

    @classmethod
    def id_from_url(cls, url):
        match = re.search(r'doi/([a-zA-Z0-9\/\.]+)', url)
        if not match:
            raise ValueError("Invalid aps URL format.")
        el_id = match.group(1)
        return el_id.replace("/", "_")

    @classmethod
    def _get_remote(cls, url: str, target: str, **kwargs):
        """
        Retrieve the file from the remote URL.
        """
        raise NotImplementedError("Remote access for elsevier not implemented.")