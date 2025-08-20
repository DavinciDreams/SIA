import os
import json
from typing import Any, Dict, Optional

DASHBOARD_STATE_PATH = os.getenv("SIA_DASHBOARD_STATE_PATH", "./sia_data/dashboard_state.json")
USER_PREFS_PATH = os.getenv("SIA_USER_PREFS_PATH", "./sia_data/user_prefs.json")


def save_dashboard_state(state: Dict[str, Any], path: Optional[str] = None) -> None:
    """Persist dashboard state to disk as JSON."""
    _save_json(state, path or DASHBOARD_STATE_PATH)


def load_dashboard_state(path: Optional[str] = None) -> Dict[str, Any]:
    """Load dashboard state from disk, or return empty dict if not found."""
    return _load_json(path or DASHBOARD_STATE_PATH)


def save_user_preferences(prefs: Dict[str, Any], path: Optional[str] = None) -> None:
    """Persist user preferences to disk as JSON."""
    _save_json(prefs, path or USER_PREFS_PATH)


def load_user_preferences(path: Optional[str] = None) -> Dict[str, Any]:
    """Load user preferences from disk, or return empty dict if not found."""
    return _load_json(path or USER_PREFS_PATH)


def _save_json(data: Dict[str, Any], path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def _load_json(path: str) -> Dict[str, Any]:
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except Exception:
            return {}