import sys
import ctypes
import os
import datetime
import logging
from pathlib import Path
from typing import Optional

from utils.storage import create_scan_directory, save_json
from models import CollectionManifest, SystemInventory
from collectors.hardware import collect_os_info, collect_hardware_info

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def is_admin() -> bool:
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except AttributeError:
        return False

def check_disk_space(path: Path, min_bytes: int = 100 * 1024 * 1024) -> bool:
    try:
        if hasattr(os, 'statvfs'):
            st = os.statvfs(path)
            free = st.f_bavail * st.f_frsize
            return free > min_bytes
        else:
            import ctypes
            free_bytes = ctypes.c_ulonglong(0)
            ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p(str(path)), None, None, ctypes.pointer(free_bytes))
            return free_bytes.value > min_bytes
    except Exception as e:
        logger.warning(f"Could not reliably determine free space: {e}")
        return True

def run_collection(output_dir: Optional[str] = None):
    print("Starting System Atlas (Read-Only Inventory)...")

    base_out = output_dir if output_dir else os.path.join(os.getcwd(), "SystemAtlas", "Scans")

    try:
        scan_dir = create_scan_directory(base_out)
        logger.info(f"Scan directory established: {scan_dir}")
    except PermissionError:
        logger.error("Insufficient permissions to create output directory. Exiting.")
        sys.exit(1)

    if not check_disk_space(scan_dir.parent):
        logger.error("Insufficient disk space on destination drive. Need at least 100MB.")
        sys.exit(1)

    elevated = is_admin()
    if elevated:
        logger.info("Running with elevated privileges.")
    else:
        logger.info("Running as Standard User.")

    start_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
    scan_id = scan_dir.name

    manifest = CollectionManifest(
        scan_id=scan_id,
        start_time=start_time,
        is_elevated=elevated
    )

    inventory = SystemInventory()

    # --- Phase 1: Hardware & OS ---
    print("Collecting OS Information...")
    os_info, os_manifest = collect_os_info()
    inventory.os_info = os_info
    manifest.collectors["OS_Info"] = os_manifest

    print("Collecting Hardware Information...")
    hw_info, hw_manifest = collect_hardware_info()
    inventory.hardware_info = hw_info
    manifest.collectors["Hardware_Info"] = hw_manifest

    # Finalize
    print("Finalizing exports...")
    save_json(manifest.to_dict(), scan_dir / "Collection-Manifest.json")

    # Save inventory using dataclass conversion helper if available, or manual dictionary mapping
    inventory_dict = {
        "os_info": inventory.os_info,
        "hardware_info": inventory.hardware_info
    }
    save_json(inventory_dict, scan_dir / "System-Inventory.json")

    print(f"Collection complete. Data saved to {scan_dir}")

if __name__ == "__main__":
    run_collection()
