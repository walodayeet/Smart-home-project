from datetime import datetime
from typing import Dict, List, Optional
import random

from app.models.schemas import DeviceStatus, DeviceType, DeviceCommand


class DeviceManager:
    """Manages smart home devices."""

    def __init__(self):
        self.devices: Dict[str, DeviceStatus] = {}
        self._initialize_devices()

    def _initialize_devices(self):
        """Initialize default devices."""
        now = datetime.now()

        self.devices = {
            "door_lock": DeviceStatus(
                id="door_lock",
                name="Front Door Lock",
                type=DeviceType.LOCK,
                online=True,
                state="locked",
                battery_level=85,
                last_seen=now,
                metadata={"auto_lock_delay": 30},
            ),
            "garage_lock": DeviceStatus(
                id="garage_lock",
                name="Garage Door",
                type=DeviceType.LOCK,
                online=True,
                state="locked",
                battery_level=72,
                last_seen=now,
                metadata={},
            ),
            "living_room_light": DeviceStatus(
                id="living_room_light",
                name="Living Room Light",
                type=DeviceType.LIGHT,
                online=True,
                state="off",
                last_seen=now,
                metadata={"brightness": 0, "color_temp": 4000},
            ),
            "kitchen_light": DeviceStatus(
                id="kitchen_light",
                name="Kitchen Light",
                type=DeviceType.LIGHT,
                online=True,
                state="on",
                last_seen=now,
                metadata={"brightness": 80, "color_temp": 4500},
            ),
            "bedroom_light": DeviceStatus(
                id="bedroom_light",
                name="Bedroom Light",
                type=DeviceType.LIGHT,
                online=True,
                state="off",
                last_seen=now,
                metadata={"brightness": 0, "color_temp": 2700},
            ),
            "bedroom_blinds": DeviceStatus(
                id="bedroom_blinds",
                name="Bedroom Blinds",
                type=DeviceType.BLINDS,
                online=True,
                state="closed",
                last_seen=now,
                metadata={"position": 0, "tilt": 0},
            ),
            "living_room_blinds": DeviceStatus(
                id="living_room_blinds",
                name="Living Room Blinds",
                type=DeviceType.BLINDS,
                online=True,
                state="open",
                last_seen=now,
                metadata={"position": 100, "tilt": 45},
            ),
        }

    def get_all_devices(self) -> List[DeviceStatus]:
        """Get all devices."""
        return list(self.devices.values())

    def get_device(self, device_id: str) -> Optional[DeviceStatus]:
        """Get a specific device."""
        return self.devices.get(device_id)

    def send_command(
        self, device_id: str, command: DeviceCommand
    ) -> Optional[DeviceStatus]:
        """Send a command to a device."""
        device = self.devices.get(device_id)
        if not device:
            return None

        action = command.action.lower()

        # Handle lock commands
        if device.type == DeviceType.LOCK:
            if action in ["lock", "secure"]:
                device.state = "locked"
            elif action in ["unlock", "open"]:
                device.state = "unlocked"

        # Handle light commands
        elif device.type == DeviceType.LIGHT:
            if action in ["turn_on", "on", "enable"]:
                device.state = "on"
                device.metadata["brightness"] = (
                    command.parameters.get("brightness", 100)
                    if command.parameters
                    else 100
                )
            elif action in ["turn_off", "off", "disable"]:
                device.state = "off"
                device.metadata["brightness"] = 0
            elif action == "set_brightness":
                brightness = (
                    command.parameters.get("brightness", 50)
                    if command.parameters
                    else 50
                )
                device.metadata["brightness"] = brightness
                device.state = "on" if brightness > 0 else "off"

        # Handle blind commands
        elif device.type == DeviceType.BLINDS:
            if action in ["open", "up"]:
                device.state = "open"
                device.metadata["position"] = 100
            elif action in ["close", "down"]:
                device.state = "closed"
                device.metadata["position"] = 0
            elif action == "set_position":
                position = (
                    command.parameters.get("position", 50) if command.parameters else 50
                )
                device.metadata["position"] = position
                device.state = (
                    "partially_open"
                    if 0 < position < 100
                    else ("open" if position == 100 else "closed")
                )

        device.last_seen = datetime.now()
        return device

    def toggle_device(self, device_id: str) -> Optional[DeviceStatus]:
        """Toggle a device on/off."""
        device = self.devices.get(device_id)
        if not device:
            return None

        if device.type == DeviceType.LOCK:
            device.state = "unlocked" if device.state == "locked" else "locked"
        elif device.type == DeviceType.LIGHT:
            if device.state == "on":
                device.state = "off"
                device.metadata["brightness"] = 0
            else:
                device.state = "on"
                device.metadata["brightness"] = 100
        elif device.type == DeviceType.BLINDS:
            if device.state in ["open", "partially_open"]:
                device.state = "closed"
                device.metadata["position"] = 0
            else:
                device.state = "open"
                device.metadata["position"] = 100

        device.last_seen = datetime.now()
        return device
