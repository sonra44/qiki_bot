import json
import os
import logging
from typing import Any, Dict

log = logging.getLogger(__name__)


def safe_load(path: str) -> Dict[str, Any]:
    """Load JSON data from ``path`` safely."""
    if not os.path.exists(path):
        log.warning("File not found: %s", path)
        return {}
    try:
        with open(path, "r") as f:
            content = f.read()
            if not content.strip():
                log.warning("File empty: %s", path)
                return {}
            return json.loads(content)
    except Exception as exc:
        log.error("Error reading %s: %s", path, exc)
        return {}


def safe_dump(path: str, data: Dict[str, Any]) -> None:
    """Write ``data`` to ``path`` safely."""
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as exc:
        log.error("Error writing %s: %s", path, exc)

