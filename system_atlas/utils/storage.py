import os
import json
import datetime
import tempfile
from pathlib import Path

def create_scan_directory(base_dir: str = "SystemAtlas/Scans") -> Path:
    """Creates a unique timestamped scan folder."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    scan_dir = Path(base_dir) / timestamp

    try:
        scan_dir.mkdir(parents=True, exist_ok=False)
        scan_dir.chmod(0o700)
        return scan_dir
    except FileExistsError:
        # Fallback if somehow triggered in same second
        scan_dir = Path(base_dir) / f"{timestamp}_1"
        scan_dir.mkdir(parents=True, exist_ok=False)
        scan_dir.chmod(0o700)
        return scan_dir
    except PermissionError as e:
        raise PermissionError(f"Cannot create scan directory in {base_dir}. Check permissions.") from e

def save_json(data: dict, filepath: Path) -> None:
    """Saves a dictionary to a JSON file safely."""
    # Write to a secure temp file first for atomic-like save
    fd, temp_path = tempfile.mkstemp(dir=filepath.parent, prefix=filepath.stem + '_', suffix='.tmp', text=True)
    temp_filepath = Path(temp_path)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        # Replace original file
        os.replace(temp_path, filepath)
    except Exception as e:
        if temp_filepath.exists():
            temp_filepath.unlink()
        raise e
