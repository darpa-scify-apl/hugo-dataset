from datasets import load_from_disk
import argparse

def main():
    parser = argparse.ArgumentParser(
        description="Load dataset and hydrate PDFs for allowed licenses."
    )
    parser.add_argument(
        "--dataset",
        type=str,
        default="data/evidence_dataset",
        help="where to load the dataset from"
    )
    
    parser.add_argument(
        "--target",
        type=str,
        default="SciFy/sample-evidence",
        help="Where to upload the dataset to"
    )
    
    parser.add_argument(
        "--public",
        type=bool,
        default=False,
        help="Where to upload the dataset to"
    )
    
    args = parser.parse_args()
    
    dataset = load_from_disk(args.dataset)
    dataset.push_to_hub(args.target, private=not args.public)

if __name__ == "__main__":
    main() 