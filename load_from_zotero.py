from hugo_dataset.create_dataset import DatasetManager
from hugo_dataset.evidence import DocumentHandler
from pyzotero import zotero
from hugo_dataset.zotero_processor import ZoteroProcessor
import os


def load(dataset_dir, download_dir : str="data/downloads", doc_dir : str="data/docs"):
    os.makedirs(download_dir, exist_ok=True)

    zot = zotero.Zotero(os.environ["ZOTERO_LIBRARY"], "group", os.environ["ZOTERO_API_KEY"])
    items = zot.collection_items(os.environ["ZOTERO_COLLECTION"])
    zp = ZoteroProcessor(items=items, download_dir=download_dir)
    processed_items = zp.process()

    for p, key, dest in processed_items:
        #print(p)
        if key:
            with open(dest, 'wb') as out:
                out.write(zot.file(key))
        else:
            print("No file!", p.url)

    manager = DatasetManager(papers=[p[0] for p in processed_items],
        document_handler=DocumentHandler(doc_dir=doc_dir),
        dataset_dir=dataset_dir
        ) # Process the predefined list of papers.
    manager.process_all(additional_directories=[download_dir])
    manager.save_dataset()

if __name__ == "__main__":
    load(download_dir = "data/zotero", doc_dir="data/msd_docs", dataset_dir="data/materials_sciences_demo")