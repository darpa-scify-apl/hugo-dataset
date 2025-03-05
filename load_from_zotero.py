from hugo_dataset.create_dataset import DatasetManager
from hugo_dataset.evidence import DocumentHandler
from pyzotero import zotero
from hugo_dataset.zotero_processor import ZoteroProcessor
import os

download_dir = "data/zotero"
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
    document_handler=DocumentHandler(doc_dir="data/evidence")
    ) # Process the predefined list of papers.
manager.process_all(additional_directories=[download_dir])
manager.save_dataset()