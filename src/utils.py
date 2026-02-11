from __future__ import annotations
from typing import Any, Dict
import yaml

def load_yaml(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

def load_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def safe_format(template: str, **kwargs: Any) -> str:
    # very small helper so missing keys don't crash students
    for k, v in kwargs.items():
        template = template.replace("{" + k + "}", str(v))
    return template
