import os

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
        # Use the item's key as the id.
        paper["id"] = data.get("key", "")
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
        source = ""
        if "Publisher:" in extra:
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

        # If an attachment exists for this paper, include its document path.
        # The attachment is identified by its 'parentItem' key.
        attach = attachments.get(paper["id"])
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

