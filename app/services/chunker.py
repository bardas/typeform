"""
Split plaintext documents into overlapping chunks for embedding or retrieval.

"""

import sys
import logging
from pathlib import Path

from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.utils.logging import setup_logging
from app.utils.helper_functions import load_data_config

# Initialize logging
setup_logging()
logger = logging.getLogger(__name__)


def chunk_files(
    input_dir: Path, output_dir: Path, chunk_size: int, chunk_overlap: int
) -> None:
    """
    Read all .txt files in `input_dir`, split into overlapping chunks,
    and write each chunk as a separate file in `output_dir`.
    """
    if not input_dir.is_dir():
        raise FileNotFoundError(f"Input directory not found: {input_dir}")

    txt_paths = list(input_dir.glob("*.txt"))
    if not txt_paths:
        raise FileNotFoundError(f"No .txt files found in: {input_dir}")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    for txt_path in txt_paths:
        try:
            logger.info(f"Reading {txt_path.name}")
            content = txt_path.read_text(encoding="utf-8")
            chunks = splitter.split_text(content)
            logger.info(f"{txt_path.name} → {len(chunks)} chunks")
            for idx, chunk in enumerate(chunks):
                (output_dir / f"{txt_path.stem}_chunk_{idx}.txt").write_text(
                    chunk, encoding="utf-8"
                )
        except Exception as e:
            logger.error(f"Error processing {txt_path.name}: {e}")

    logger.info("Chunking complete.")


def main():
    """
    Entrypoint: load YAML config and run chunking.
    """
    try:
        cfg = load_data_config()
        input_dir = Path(cfg["plaintext_dir"])
        output_dir = Path(cfg["processed_dir"])
        chunk_size = int(cfg["chunk_size"])
        chunk_overlap = int(cfg["chunk_overlap"])

        chunk_files(input_dir, output_dir, chunk_size, chunk_overlap)
    except Exception as e:
        logger.critical(f"Fatal error in chunking: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
