from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel


class RecognitionStatus(str, Enum):
    RECOGNIZED = "recognized"
    UNKNOWN = "unknown"
    MASKED = "masked"
    ERROR = "error"


class RecognitionResult(BaseModel):
    """Face recognition result."""

    status: RecognitionStatus
    person_id: Optional[str] = None
    person_name: Optional[str] = None
    confidence: float
    timestamp: datetime
    message: str
    requires_action: bool = False


class FaceVerificationResponse(BaseModel):
    """Face verification response for protected actions."""

    verified: bool
    allowed: bool
    token: Optional[str] = None
    expires_at: Optional[datetime] = None
    device_id: Optional[str] = None
    action: Optional[str] = None
    result: RecognitionResult


class DeviceType(str, Enum):
    LOCK = "lock"
    LIGHT = "light"
    BLINDS = "blinds"
    CAMERA = "camera"
    SENSOR = "sensor"


class DeviceStatus(BaseModel):
    """Device status model."""

    id: str
    name: str
    type: DeviceType
    online: bool
    state: str
    battery_level: Optional[int] = None
    last_seen: datetime
    metadata: Dict[str, Any] = {}


class DeviceCommand(BaseModel):
    """Device command model."""

    action: str
    parameters: Optional[Dict[str, Any]] = None
    verification_token: Optional[str] = None


class ToggleDeviceRequest(BaseModel):
    """Toggle device request model."""

    verification_token: Optional[str] = None


class CameraFeed(BaseModel):
    """Camera feed model."""

    id: str
    name: str
    location: str
    status: str
    resolution: str
    fps: int
    stream_url: Optional[str] = None


class VoiceCommand(BaseModel):
    """Voice command model."""

    text: str
    confidence: Optional[float] = None
    timestamp: Optional[datetime] = None


class SystemStatus(BaseModel):
    """System status model."""

    status: str
    timestamp: datetime
    mode: str
    cameras_online: int
    devices_online: int
    total_devices: int
    recent_events: int


class AccessLogEntry(BaseModel):
    """Access log entry model."""

    id: str
    timestamp: datetime
    person_name: Optional[str]
    person_id: Optional[str]
    camera_id: str
    camera_name: str
    event_type: str
    confidence: Optional[float]
    image_url: Optional[str] = None
