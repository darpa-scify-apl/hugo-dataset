# Hugo Dataset

**Library for Building and Loading the DARPA SciFy Evidence Dataset**

The **Hugo Dataset** repository provides a modular Python library for creating, processing, and managing datasets composed of scientific papers and evidence documents. It supports importing metadata and attachments (e.g., via Zotero), indexing and downloading PDFs, and uploading the final dataset (for example, to the Hugging Face Hub). This repository is now configured to work with [uv](https://astral.sh/uv) – a fast, unified Python project manager – for environment management, dependency resolution, and script execution.

# Quickstart

## Just the dataset

This gives you all the pointers to the documents you need (see [SciFy/materials_sciences_demo](https://huggingface.co/datasets/SciFy/materials_sciences_demo))

```bash
pip install datasets
```

In python:
```python
import datasets
ds = datasets.load_dataset("SciFy/materials_sciences_demo")
```

## With retrievers

```bash
git clone https://github.com/darpa-scify/hugo-dataset.git
cd hugo-dataset
uv sync
uv run python
```

In python:
```python
>>> from hugo_dataset.load_dataset import DatasetLoader
>>> ds = DatasetLoader(dataset_location="SciFy/materials_sciences_demo", remote=True, target_dir="data/msdtest", allowed_licenses=["all"])
>>> ds.load_dataset()
>>> ds.dataset
```

It is expected to get a number of errors of the form:
```bash
INFO     Error processing {DOCID}: Remote access for {SOURCE} not implemented load_dataset.py:64
```

---

## Table of Contents

- [Features](#features)
- [Directory Structure](#directory-structure)
- [Installation Using uv](#installation-using-uv)
- [Usage](#usage)
  - [Loading Data from Zotero](#loading-data-from-zotero)
  - [Uploading the Dataset](#uploading-the-dataset)
  - [Loading and Processing the Dataset](#loading-and-processing-the-dataset)
- [Architecture Overview](#architecture-overview)
- [Roadmap & Future Improvements](#roadmap--future-improvements)
- [Contributing](#contributing)
- [License](#license)

---

## Features

- **Dataset Creation & Management:** Build a dataset from a list of scientific papers.
- **Zotero Integration:** Import paper metadata and attachments from Zotero collections.
- **Document Hydration:** Download PDFs, compute hashes, and index documents.
- **Multiple Retrievers:** Support for various document sources (arXiv, ACL Anthology, etc.).
- **Upload Support:** Upload your dataset to remote hubs.
- **Fast CLI Operations with uv:** Leverage [uv](https://astral.sh/uv) for rapid virtual environment creation, dependency resolution, and script execution.

---

## Directory Structure

```
hugo-dataset/
├── README.md                # This file
├── load_from_zotero.py      # Script to import data from Zotero using uv run
├── pyproject.toml           # Project configuration (uv recognizes this file)
├── upload_dataset.py        # Script to upload the dataset (invoked via uv run)
└── hugo_dataset/            # Core Python package
    ├── __init__.py
    ├── create_dataset.py    # Main dataset creation logic
    ├── evidence.py          # Models and document processing logic
    ├── load_dataset.py      # Loader for processing the dataset
    ├── logger.py            # Custom logging configuration
    ├── zotero_processor.py  # Processes Zotero JSON items
    └── retrievers/          # Modules for retrieving documents from various sources
        ├── __init__.py
        ├── acl.py           # ACL Anthology retriever
        ├── aps.py           # APS retriever
        ├── arxiv.py         # arXiv retriever
        ├── base.py          # Base retriever class
        ├── elsevier.py      # Elsevier retriever (remote not yet implemented)
        ├── mp.py            # Materials Project retriever
        ├── pubmed.py        # PubMed retriever (with usage limitations)
        ├── sciencedirect.py # ScienceDirect retriever (remote not yet implemented)
        ├── springer.py      # Springer retriever (remote not yet implemented)
        └── wikipedia.py     # Wikipedia retriever
```

---

## Installation Using uv

uv is used to streamline the setup and execution of this repository. Follow these steps:

1. **Clone the Repository**

   ```bash
   git clone https://github.com/darpa-scify/hugo-dataset.git
   cd hugo-dataset
   ```

2. **Create a Virtual Environment with uv**

   uv automatically detects `pyproject.toml` and configures the project. Create an environment and install the repository in editable mode:

   ```bash
   uv sync
   ```

3. **(Optional) Install uv**

   If you haven’t already installed uv, you can use the standalone installer:

   - On macOS/Linux:

     ```bash
     curl -LsSf https://astral.sh/uv/install.sh | sh
     ```

   - On Windows:

     ```powershell
     powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
     ```

For more details on uv, see the [uv documentation](https://astral.sh/uv).

---

## Usage

With uv managing the environment and dependencies, you can run scripts using `uv run` (or its alias `uvx` for one-off tool invocations).

### `store_file`
You may provide a `store_file` containing a mapping from `id` to `file_path`:

```json
{
   "id1": "path/to/document1",
   "id2": "path/to/document2,
   ...
}
```

### Loading Data from Zotero

Before running the script, ensure you have set the required environment variables:

- `ZOTERO_LIBRARY`
- `ZOTERO_API_KEY`
- `ZOTERO_COLLECTION`

Run the Zotero loader using uv:

```bash
uv run load_from_zotero.py
```

### Loading and Processing an existing Dataset

```bash
uv run hugo_dataset/load_dataset.py --dataset data/evidence_dataset --allowed-licenses "cc by 4.0" "acl license" --store-file storefile.json
```

### Creating a dataset
```python
  manager = DatasetManager(papers=[ 
    Paper( id="1809.09600", url="https://arxiv.org/pdf/1809.09600.pdf", source="arXiv", year="2018"), 
    Paper( id="2009.07758", url="https://arxiv.org/pdf/2009.07758.pdf", source="arXiv", year="2020"), 
    Paper( id="N19-1423", url="https://aclanthology.org/N19-1423.pdf", source="ACL Anthology", year="2019") ],
    document_handler=DocumentHandler(doc_dir="data/cpdfs")
    ) # Process the predefined list of papers.
  # Load pdfs from an existing directory (Assumes appropriate retrievers are implemented)
  manager.process_all(additional_directories=["data/arxiv_sample"])
  # Add new papers directly by url. (Assumes appropriate retrievers are implemented)
  manager.add_paper_from_url("https://arxiv.org/pdf/2301.12345.pdf")

  # Save the dataset.
  manager.save_dataset()
```

### Uploading the Dataset

```bash
uv run upload_dataset.py --dataset data/evidence_dataset --target your-huggingface-organization/sample-evidence --public
```

## Retrievers

Retrievers are modular components responsible for fetching document metadata and downloading files from various external sources (such as arXiv, ACL Anthology, etc.). If you need to support a new source, you can implement a custom retriever by following these guidelines.

### Getting Documents

All retrievers have a `_get_local` and `_get_remote`. By default, `_get_local` searches any local directories provided for files with the name `{evidence_id}.{source_extension}`. You can override this as needed. Both `_get_local` and `_get_remote` receive an `evidence` object that extends `hugo_dataset.evidence.Evidence` that can be used to unify the document with your existing sources.

You can rewrite the implementation in `hugo_dataset.retrievers.base` or implement your own retrievers.

#### TODO
- [ ] A cleaner workflow for managing your own retriever workflows.


---

## Roadmap & Future Improvements

To further improve the repository, consider the following issues:

1. **Enhanced Error Handling & Logging**
2. **Remote Retrieval Enhancements**
3. **Testing & Continuous Integration**
4. **Unified CLI with uv**
5. **Documentation Improvements**
6. **Configuration File Support**
7. **Performance and Scalability**
8. **Extending Source Support**
9. **Refactoring and Code Quality**
10. **User Feedback & Examples**

---

## Contributing

Contributions are welcome! To get started:

1. **Fork the Repository**
2. **Create a Feature Branch:**  
   ```bash
   git checkout -b feature/my-new-feature
   ```
3. **Commit Your Changes:**  
   ```bash
   git commit -am 'Add new feature'
   ```
4. **Push to Your Branch:**  
   ```bash
   git push origin feature/my-new-feature
   ```
5. **Open a Pull Request**

---

## License

TBD

