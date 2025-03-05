import os
import urllib
from pydantic import BaseModel
from hugo_dataset import retrievers
from hugo_dataset.evidence import Paper

def process_zotero_items(items, download_dir=None):
    """
    Process a list of Zotero JSON items and return a list of dictionaries
    representing papers with keys:
      - 'id': the Zotero key
      - 'title': the paper title
      - 'abstract': the abstract (if any)
      - 'year': extracted from 'parsedDate' or 'date'
      - 'url': the URL of the paper
      - 'source': the publisher (extracted from extra or fallback fields)
      - 'document_path': path to the downloaded document (if an attachment exists)
      
    Args:
        items (list): A list of Zotero JSON dictionaries.
        download_dir (str): Optional. The directory where downloaded documents reside.
    
    Returns:
        list: A list of processed paper dictionaries.
    """
    # Build a mapping from parent item id to attachment data.
    attachments = {}
    for item in items:
        data = item.get("data", {})
        item_type = data.get("itemType", "")
        if item_type == "attachment":
            parent = data.get("parentItem")
            if parent:
                # For simplicity, if multiple attachments exist, take the first one.
                attachments[parent] = data

    processed = []
    for item in items:
        data = item.get("data", {})
        item_type = data.get("itemType", "")
        # Skip attachment items—they will be merged with their parent.
        if item_type == "attachment":
            continue

        paper = {}

        paper["title"] = data.get("title", "")
        paper["abstract"] = data.get("abstractNote", "")

        # Determine the year from 'parsedDate' (preferred) or 'date'.
        parsed_date = data.get("parsedDate")
        if parsed_date and len(parsed_date) >= 4:
            paper["year"] = parsed_date[:4]
        else:
            date_str = data.get("date", "")
            paper["year"] = date_str[:4] if date_str and len(date_str) >= 4 else ""

        paper["url"] = data.get("url", "")

        # Determine the source (publisher) from the extra field if present.
        extra = data.get("extra", "")
        import urllib
        if data.get("url"):
            source = urllib.parse.urlparse(data['url']).netloc.split(".")[-2] 
        elif "Publisher:" in extra:
            # Extract publisher name after "Publisher:".
            # This simple implementation takes the entire remainder; adjust as needed.
            source = extra.split("Publisher:")[-1].strip()
        else:
            # Fallback: for journal articles use 'publicationTitle', for webpages use 'websiteTitle'
            if data.get("itemType") == "journalArticle":
                source = data.get("publicationTitle", "")
            elif data.get("itemType") == "webpage":
                source = data.get("websiteTitle", "")
        paper["source"] = source

        # Use the item's key as the id.
        paper["id"] = retrievers.get_id_from_url(url=paper['url']) 
        

        # If an attachment exists for this paper, include its document path.
        # The attachment is identified by its 'parentItem' key.
        attach = attachments.get(item["key"])
        if attach:
            filename = attach.get("filename", "")
            if filename:
                if download_dir:
                    document_path = os.path.join(download_dir, filename)
                else:
                    document_path = filename
                paper["document_path"] = document_path

        processed.append(paper)

    return processed


class ZoteroProcessor(BaseModel):
    items: list[dict]
    download_dir: str | None = None

    def _build_attachments_mapping(self) -> dict:
        """
        Build a mapping from parent item id to attachment data.
        If multiple attachments exist for a paper, the first encountered is used.
        """
        attachments = {}
        for item in self.items:
            data = item.get("data", {})
            item_type = data.get("itemType", "")
            if item_type == "attachment":
                parent = data.get("parentItem")
                if parent:
                    attachments[parent] = data
        return attachments

    def _extract_year(self, data: dict) -> str:
        """
        Extract the year from the parsedDate field (preferred) or from date.
        """
        parsed_date = data.get("parsedDate")
        if parsed_date and len(parsed_date) >= 4:
            return parsed_date[:4]
        date_str = data.get("date", "")
        return date_str[:4] if date_str and len(date_str) >= 4 else ""

    def _extract_source(self, data: dict) -> str:
        """
        Determine the source (publisher) of the paper.
        It first uses the URL if available, then looks for 'Publisher:' in the extra field,
        and finally falls back to publicationTitle or websiteTitle based on the itemType.
        """
        extra = data.get("extra", "")
        url = data.get("url", "")
        if url:
            # This extracts the second-level domain (e.g., "example" from "www.example.com")
            return urllib.parse.urlparse(url).netloc.split(".")[-2]
        elif "Publisher:" in extra:
            return extra.split("Publisher:")[-1].strip()
        else:
            item_type = data.get("itemType", "")
            if item_type == "journalArticle":
                return data.get("publicationTitle", "")
            elif item_type == "webpage":
                return data.get("websiteTitle", "")
        return ""

    def process(self) -> list[Paper]:
        """
        Process the Zotero items and return a list of Paper objects.
        
        For each non-attachment item, the method extracts:
            - title, abstract (mapped to Paper.abs), year, URL, and source.
            - a unique id generated from the URL.
            - document_path if an attachment exists.
        """
        attachments = self._build_attachments_mapping()
        papers = []
        for item in self.items:
            data = item.get("data", {})
            item_type = data.get("itemType", "")
            # Skip attachments – they are merged with their parent items.
            if item_type == "attachment":
                continue

            title = data.get("title", "")
            abstract = data.get("abstractNote", "")
            year = self._extract_year(data)
            url = data.get("url", "")
            source = self._extract_source(data)
            paper_id = retrievers.get_id_from_url(url=url)
            
            # Check if there's an attachment for this paper.
            key = None
            dest = None
            attachment = attachments.get(item["key"])
            if attachment:
                #filename = attachment.get("filename", "")
                #if filename:
                #    document_path = os.path.join(self.download_dir, filename) if self.download_dir else filename
                key = attachment.get("key")
                dest = f"{self.download_dir}/{paper_id}.{attachment.get('filename', 'txt').split('.')[-1]}"

            paper = Paper(
                id=paper_id,
                url=url,
                source=source,
                year=year,
                title=title,
                abs=abstract
            )
            papers.append((paper, key, dest))
        return papers