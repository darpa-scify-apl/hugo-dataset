from pyzotero import zotero
from hugo_dataset.zotero_processor import process_zotero_items
import os

zot = zotero.Zotero(os.environ["ZOTERO_LIBRARY"], "group", os.environ["ZOTERO_API_KEY"])
items = zot.collection_items(os.environ["ZOTERO_COLLECTION"])
process_zotero_items(items, download_dir="data/zotero")