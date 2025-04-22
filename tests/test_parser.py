"""
HTML Parser test
"""
import sys
import pytest
import yaml
from pathlib import Path

# Add project root to PYTHONPATH for imports
PROJECT_ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.services.html_parser import parse_html
from app.utils.helper_functions import load_data_config


def write_yaml(tmp_path, content):
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    cfg_file = config_dir / "settings.yaml"
    cfg_file.write_text(yaml.safe_dump(content), encoding="utf-8")
    return cfg_file


def test_load_config_missing_file(monkeypatch):
    import app.utils.helper_functions as hf

    fake = Path("nonexistent.yaml")
    monkeypatch.setattr(hf, "CONFIG_FILE", fake)
    with pytest.raises(FileNotFoundError):
        load_data_config()


def test_parse_html_success(tmp_path):
    raw_dir = tmp_path / "raw"
    plain_dir = tmp_path / "plaintext"
    raw_dir.mkdir()
    # Simple HTML file
    html_content = "<html><body><h1>Title</h1><p>Paragraph1</p></body></html>"
    html_file = raw_dir / "test.html"
    html_file.write_text(html_content, encoding="utf-8")

    parse_html(raw_dir, plain_dir, delay=0)

    out_file = plain_dir / "test.txt"
    assert out_file.exists()
    text = out_file.read_text(encoding="utf-8")
    assert "Title" in text
    assert "Paragraph1" in text


def test_parse_html_no_html(tmp_path):
    raw_dir = tmp_path / "raw_empty"
    plain_dir = tmp_path / "plaintext"
    raw_dir.mkdir()
    with pytest.raises(FileNotFoundError):
        parse_html(raw_dir, plain_dir, delay=0)
