"""Default runtime logs live with per-user Nexus data, outside the source tree."""
import os
from pathlib import Path


def default_runtime_log_dir() -> Path:
    local_app_data = os.environ.get("LOCALAPPDATA", "").strip()
    if local_app_data and Path(local_app_data).is_absolute():
        data_root = Path(local_app_data)
    else:
        data_root = Path.home() / "AppData" / "Local"
    return data_root / "Nexus Desktop AI" / "logs"
