"""
Logger Setup
"""

import logging
import logging.config
from pathlib import Path
import yaml


def setup_logging(
    default_path: str = "configs/logging_config.yaml",
    default_level: int = logging.INFO,
) -> None:
    """
    Setup logging configuration
    :param default_path:  Config file path
    :param default_level: Logging level
    :return:
    """

    path = Path(default_path)
    if path.is_file():
        with open(path, "rt") as f:
            config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(
            level=default_level,
            format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
