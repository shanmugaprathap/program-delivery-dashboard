"""YAML configuration loader."""

from pathlib import Path

import yaml

_CONFIG_DIR = Path(__file__).resolve().parent.parent.parent / "config"
_DEFAULT_PATH = _CONFIG_DIR / "settings.yaml"
_EXAMPLE_PATH = _CONFIG_DIR / "settings.example.yaml"

_config: dict | None = None


def load_config(path: Path | None = None) -> dict:
    """Load and cache settings from YAML. Falls back to example config."""
    global _config
    if _config is not None and path is None:
        return _config

    config_path = path or _DEFAULT_PATH
    if not config_path.exists():
        config_path = _EXAMPLE_PATH

    with open(config_path) as f:
        _config = yaml.safe_load(f) or {}
    return _config


def get(key: str, default=None):
    """Get a top-level config value."""
    return load_config().get(key, default)


def get_nested(section: str, key: str, default=None):
    """Get a nested config value like get_nested('jira', 'server')."""
    return load_config().get(section, {}).get(key, default)
