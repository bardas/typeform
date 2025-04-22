"""
app/services/html_parser.py

Parse Help Center HTML into plaintext .txt files.
"""

import sys
import time
import logging
import yaml
from pathlib import Path
from bs4 import BeautifulSoup

from app.utils.logging import setup_logging
from app.utils.helper_functions import load_data_config

# Initialize logging
setup_logging()
logger = logging.getLogger(__name__)


def parse_html(in_dir: Path, out_dir: Path, delay: float) -> None:
    """
    Convert all .html files in `raw_dir` into .txt files in `out_dir`.
    :param in_dir: Directory containing source HTML files.
    :param out_dir: Directory to write plaintext .txt files.
    :param delay: Seconds to sleep between files
    :return:
    """

    raw_dir = Path(in_dir)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    html_files = list(raw_dir.glob("*.html"))
    if not html_files:
        raise FileNotFoundError(f"No .html files found in: {raw_dir}")

    for html_file in html_files:
        try:
            logger.info(f"Reading {html_file.name}")
            content = html_file.read_text(encoding="utf-8", errors="ignore")
            soup = BeautifulSoup(content, "html.parser")
            text_blob = soup.get_text(separator="\n", strip=True)
            out_path = out_dir / f"{html_file.stem}.txt"
            out_path.write_text(text_blob, encoding="utf-8")
            logger.info(f"Wrote {out_path.name}")
            time.sleep(delay)
        except Exception as e:
            logger.error(f"Failed processing {html_file.name}: {e}")

    logger.info("HTML parsing complete.")


def main() -> None:
    try:
        cfg = load_data_config()
        parse_html(
            in_dir=Path(cfg["raw_html_dir"]),
            out_dir=Path(cfg["plaintext_dir"]),
            delay=float(cfg.get("sleep_secs", 0.5)),
        )
    except Exception as e:
        logger.critical(f"Fatal error in HTML parsing: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
