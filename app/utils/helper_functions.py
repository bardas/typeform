import yaml
from pathlib import Path
from typing import Dict, Any


CONFIG_FILE = Path("configs/settings.yaml")


def load_data_config(config_path: Path = CONFIG_FILE, section="data") -> Dict[str, Any]:
    """
    Load and return the 'data' section from the YAML config file.

    :param config_path: Configuration file path.
    :param section: Section name to get the configuration from.
    :return: Configuration dictionary.
    """

    if not config_path.is_file():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    try:
        raw = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    except Exception as e:
        raise RuntimeError(f"Failed to parse YAML at {config_path}: {e}")

    section_cfg = raw.get(section)
    if not isinstance(section_cfg, dict):
        raise KeyError(f"Missing or invalid {section} section in config")
    return section_cfg


def prepare_prompt_phi(context="", comment=""):
    """
    Prepare prompt for the requirements Phi model

    :param context: Context retrieved from retrieve_context.
    :param comment: Prompt to be given to the model.
    :return:
    """

    # initialize prompt template for the MiniChat model
    prompt_template_w_context = (
        lambda context, comment: f"""
    {context}

    You have access to the above context. Answer the following question:
    {comment}?
    """
    )
    # create prompt for the model
    prompt = prompt_template_w_context(context, comment)
    return prompt


def get_phi_role():
    """Function that returns a text specifying the role of the chatbot"""

    role = """You are a virtual assistant expert at answering form related questions with
     access to the following context."""
    return role
