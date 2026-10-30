import platform
import datetime
import logging
from typing import Dict, Any, Tuple

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

from models import ManifestEntry, CollectionState

logger = logging.getLogger(__name__)

def collect_os_info() -> Tuple[Dict[str, Any], ManifestEntry]:
    """Collects basic OS information safely."""
    start_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
    errors = []

    os_info = {
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "architecture": platform.machine(),
        "processor": platform.processor(),
        "node_name": platform.node(),
    }

    try:
        # Avoid hanging on some systems
        os_info["win32_edition"] = platform.win32_edition()
    except Exception as e:
        errors.append(f"Failed to get win32_edition: {e}")

    end_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
    status = CollectionState.PARTIAL if errors else CollectionState.COMPLETE

    manifest = ManifestEntry(
        collector_name="OS_Info",
        status=status,
        start_time=start_time,
        end_time=end_time,
        record_count=len(os_info),
        errors=errors
    )

    return os_info, manifest

def collect_hardware_info() -> Tuple[Dict[str, Any], ManifestEntry]:
    """Collects hardware info using psutil."""
    start_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
    errors = []
    hw_info = {}

    if not HAS_PSUTIL:
        manifest = ManifestEntry(
            collector_name="Hardware_Info",
            status=CollectionState.UNAVAILABLE,
            start_time=start_time,
            end_time=start_time,
            errors=["psutil library not available."]
        )
        return hw_info, manifest

    try:
        hw_info["cpu_physical_cores"] = psutil.cpu_count(logical=False)
        hw_info["cpu_logical_cores"] = psutil.cpu_count(logical=True)
    except Exception as e:
        errors.append(f"CPU count error: {e}")

    try:
        mem = psutil.virtual_memory()
        hw_info["ram_total_bytes"] = mem.total
        hw_info["ram_available_bytes"] = mem.available
    except Exception as e:
        errors.append(f"Memory info error: {e}")

    try:
        partitions = []
        for part in psutil.disk_partitions(all=False):
            try:
                usage = psutil.disk_usage(part.mountpoint)
                partitions.append({
                    "device": part.device,
                    "mountpoint": part.mountpoint,
                    "fstype": part.fstype,
                    "opts": part.opts,
                    "total_bytes": usage.total,
                    "free_bytes": usage.free
                })
            except PermissionError:
                # Normal for some protected volumes
                partitions.append({
                    "device": part.device,
                    "mountpoint": part.mountpoint,
                    "error": "Permission Denied"
                })
        hw_info["disk_partitions"] = partitions
    except Exception as e:
        errors.append(f"Disk partition error: {e}")

    end_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
    status = CollectionState.PARTIAL if errors else CollectionState.COMPLETE

    manifest = ManifestEntry(
        collector_name="Hardware_Info",
        status=status,
        start_time=start_time,
        end_time=end_time,
        record_count=len(hw_info),
        errors=errors
    )

    return hw_info, manifest
