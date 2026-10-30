from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
import datetime

class CollectionState(Enum):
    COMPLETE = "Complete"
    PARTIAL = "Partial"
    UNAVAILABLE = "Unavailable"
    NOT_COLLECTED = "Not collected"

@dataclass
class ManifestEntry:
    collector_name: str
    status: CollectionState
    start_time: str
    end_time: str
    record_count: int = 0
    errors: List[str] = field(default_factory=list)
    exclusions: List[str] = field(default_factory=list)

@dataclass
class CollectionManifest:
    scan_id: str
    start_time: str
    is_elevated: bool
    collectors: Dict[str, ManifestEntry] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "scan_id": self.scan_id,
            "start_time": self.start_time,
            "is_elevated": self.is_elevated,
            "collectors": {
                k: {
                    "status": v.status.value,
                    "start_time": v.start_time,
                    "end_time": v.end_time,
                    "record_count": v.record_count,
                    "errors": v.errors,
                    "exclusions": v.exclusions
                } for k, v in self.collectors.items()
            }
        }

@dataclass
class SystemInventory:
    os_info: Dict[str, Any] = field(default_factory=dict)
    hardware_info: Dict[str, Any] = field(default_factory=dict)
    # Additional sections will be added as collectors are built
