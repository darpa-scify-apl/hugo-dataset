import os
import shutil
import requests
import re

from .base import Retriever

class springer(Retriever):
    source : str = "springer"
    extension : str = "pdf"
    license = "springer"

    @classmethod
    def id_from_url(cls, url):
        match = re.search(r'springer.com/([a-zA-Z0-9\.]+\/[0-9-_]+)', url)
        if not match:
            raise ValueError("Invalid springer URL format.")
        el_id = match.group(1)
        return el_id

    @classmethod
    def _get_remote(cls, url: str, target: str, **kwargs):
        """
        Retrieve the file from the remote URL.
        """
        raise NotImplementedError("Remote access for elsevier not implemented.")