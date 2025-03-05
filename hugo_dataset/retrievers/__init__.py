from .acl import acl
from .arxiv import arxiv
from .wikipedia import wikipedia
from .mp import mp
from .elsevier import elsevier
from .springer import springer
from .aps import aps
from .sciencedirect import sciencedirect

from hugo_dataset.logger import get_logger
logger = get_logger(__name__+".retrievers")

# Build the initial GETTERS dictionary from all included retrievers
GETTERS = {
    acl.source: acl,
    arxiv.source: arxiv,
    wikipedia.source: wikipedia,
    mp.source: mp,
    elsevier.source : elsevier,
    springer.source : springer,
    aps.source: aps,
    sciencedirect.source: sciencedirect,
}

def register_retriever(retriever_cls):
    """
    Register a new retriever class.

    The retriever class must have a 'source' attribute that uniquely identifies it.
    For example:
        class myRetriever(Retriever):
            source = "my_source"
            ...
    
    Args:
        retriever_cls: A class that extends the Retriever base class.
    """
    if not hasattr(retriever_cls, 'source'):
        raise AttributeError("The retriever class must have a 'source' attribute.")
    GETTERS[retriever_cls.source] = retriever_cls

def get(source, id, **kwargs):
    """
    Retrieve metadata using the retriever associated with the given source.

    Args:
        source (str): The key identifying the source.
        id (str): The identifier for the document.

    Returns:
        dict: Metadata about the document.
    """
    getter = GETTERS.get(source)
    if not getter:
        logger.debug(f"get: No getter for {source} has been implemented")
        raise NotImplementedError(f"No getter for {source} has been implemented")
    return getter.get(id, **kwargs)

def get_document(source, url, target, **kwargs):
    """
    Download the document from the given URL using the retriever associated with the source.

    Args:
        source (str): The key identifying the source.
        url (str): The URL of the document.
        target (str): The local file path where the document should be saved.

    Returns:
        str: The target file path if successful.
    """
    getter = GETTERS.get(source)
    if not getter:
        logger.debug(f"get_document: No getter for {source} has been implemented")
        raise NotImplementedError(f"No document getter for {source} has been implemented")
    return getter.get_document(url, target, **kwargs)

def get_id_from_url(source=None, url=None, **kwargs):
    """
    Retrieve metadata using the retriever associated with the given source.

    Args:
        source (str): The key identifying the source.
        id (str): The identifier for the document.

    Returns:
        dict: Metadata about the document.
    """
    logger.debug(f"getting id from url: {url}")
    if source is None:
        import urllib
        source = urllib.parse.urlparse(url).netloc.split(".")[-2] 
    getter = GETTERS.get(source)
    if not getter:
        logger.debug(f"get_id_for_url: No getter for {source} has been implemented")
        raise NotImplementedError(f"No getter for {source} has been implemented")
    return getter.id_from_url(url, **kwargs)