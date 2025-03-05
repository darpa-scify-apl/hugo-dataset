import json
import os
import re

from .base import Retriever

from pydantic import BaseModel

def get_mp(id="mp-1105139"):
    import os
    from mp_api.client import MPRester
    with MPRester(api_key=os.environ.get("MP_API_KEY")) as mpr:
        data = mpr.materials.search(material_ids=[id])
    
    return data

class mp(Retriever):
    source : str = "materialsproject"
    extension : str = "json"

    @classmethod
    def id_from_url(cls, url):
        match = re.search(r'materialsproject.org/materials/([a-zA-Z0-9.-]+)', url)
        if not match:
            raise ValueError("Invalid materialsproject URL format.")
        mp_id = match.group(1)
        return mp_id

    @classmethod
    def from_url(cls, url):
        return cls.get(cls.id_from_url(url))
    
    @classmethod
    def get(cls, id, **kwargs):
        raise NotImplementedError(f"{cls} - get not implemented - ensure metadata in entry")

    @classmethod
    def _get_remote(cls, url: str, target: str, **kwargs):
        """
        Retrieve the file from the remote URL.
        """
        from . import logger
        logger.info(f"Retrieving {url} from remote source")
        try:
            response = get_mp(cls.id_from_url(url))
        except Exception as e:
            logger.debug(e)
            logger.debug(f"Failed to retrieve {url}!")
            raise Exception(f"Failed to download document from {url}")
        if os.path.isdir(target):
            target = os.path.join(target, f"{cls.id_from_url(url)}.{cls.extension}")
            with open(target, "w") as f:
                json.dump([r.dict() for r in response], f)
            return target
        else:
            logger.debug(f"Failed to write document {url}!")
            raise Exception(f"Failed to write mp_id {url}")

