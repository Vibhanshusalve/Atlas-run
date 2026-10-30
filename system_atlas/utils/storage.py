import os
import json
import datetime
from pathlib import Path

def create_scan_directory(base_dir: str = "SystemAtlas/Scans") -> Path:
    """Creates a unique timestamped scan folder."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    scan_dir = Path(base_dir) / timestamp

    try:
        scan_dir.mkdir(parents=True, exist_ok=False)
        return scan_dir
    except FileExistsError:
        # Fallback if somehow triggered in same second
        scan_dir = Path(base_dir) / f"{timestamp}_1"
        scan_dir.mkdir(parents=True, exist_ok=False)
        return scan_dir
    except PermissionError as e:
        raise PermissionError(f"Cannot create scan directory in {base_dir}. Check permissions.") from e

def save_json(data: dict, filepath: Path) -> None:
    """Saves a dictionary to a JSON file safely."""
    # Write to a temp file first for atomic-like save
    temp_filepath = filepath.with_suffix('.tmp')
    try:
        with open(temp_filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        # Replace original file
        temp_filepath.replace(filepath)
    except Exception as e:
        if temp_filepath.exists():
            temp_filepath.unlink()
        raise e
