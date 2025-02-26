import os
import shutil
import requests

class Retriever:
    source : str = "None"
    extension : str = "pdf"

    @classmethod
    def id_from_url(cls, url):
        raise NotImplementedError("id_from_url not implemented")

    @classmethod
    def from_url(cls, url):
        return cls.get(cls.id_from_url(url))
    
    @classmethod
    def get(cls, id, **kwargs):
        raise NotImplementedError("get not implemented")

    @classmethod
    def _copy_file(cls, source, target):
        from . import logger
        try:
            if not os.path.isfile(target):
                fname = os.path.split(source)[1]
                target = os.path.join(target, fname)
            if os.path.abspath(source) == os.path.abspath(target):
                logger.info(f"{source} == {target} (no copy necessary)")
                return target
            else:
                logger.info(f"copying {source} to {target}")
                shutil.copy2(source, target)
                return target
        except Exception as e:
            logger.debug("Failed to copy")
            raise e
        
    @classmethod
    def _get_local(cls, url: str, target: str, local_dir: str, walk=True, **kwargs):
        """
        Attempt to retrieve the file from a local directory if 'local_dir' is specified in kwargs.
        if walk == False, don't recursively search the directory
        """
        from . import logger
        if os.path.isfile(local_dir):
            return cls._copy_file(local_dir, target)
        elif walk:
            id = cls.id_from_url(url)
            for d, sub, f in os.walk(local_dir):
                for _f in f:
                    if id == os.path.splitext(_f):
                        p = os.path.join(d, _f)
                        cls._copy_file(p, target)
                        return target
        else:
            id = cls.id_from_url(url)
            p = os.path.join(local_dir, f"{p}.{cls.extension}")
            if os.path.isfile(p):
                cls._copy_file(p, target)
                return target
        return None

    @classmethod
    def _get_remote(cls, url: str, target: str, **kwargs):
        """
        Retrieve the file from the remote URL.
        """
        from . import logger
        logger.info(f"Retrieving {url} from remote source")
        try:
            response = requests.get(url)
        except Exception as e:
            logger.debug(e)
        if response.status_code == 200:
            if os.path.isdir(target):
                target = os.path.join(target, f"{cls.id_from_url(url)}.{cls.extension}")
            with open(target, "wb") as f:
                f.write(response.content)
            return target
        else:
            logger.debug(f"Failed to retrieve {url}!")
            raise Exception(f"Failed to download document from {url}")

    @classmethod
    def get_document(cls, url: str, target: str, offline=False, **kwargs):
        """
        Retrieve the document from either a local directory or a remote URL.
        Extra kwargs (e.g. local_dir) are passed to the helper methods.
        if offline == True, don't go to remote sources
        """
        local_dir = kwargs.get("local_dir")
        if local_dir:
            local = cls._get_local(url, target, **kwargs)
            if local:
                return local
        if offline:
            return None
        return cls._get_remote(url, target, **kwargs)
