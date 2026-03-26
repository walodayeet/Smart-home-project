"""
Configuration and utility functions for face recognition system.
"""

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict


@dataclass
class RecognitionConfig:
    """Configuration for face recognition."""

    tolerance: float = 0.6
    model: str = "hog"
    upsample: int = 1
    data_dir: str = "data"
    camera_index: int = 0
    frame_resize: float = 0.5
    recognition_interval: int = 5

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "RecognitionConfig":
        return cls(
            **{
                key: value
                for key, value in config_dict.items()
                if key in cls.__dataclass_fields__
            }
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tolerance": self.tolerance,
            "model": self.model,
            "upsample": self.upsample,
            "data_dir": self.data_dir,
            "camera_index": self.camera_index,
            "frame_resize": self.frame_resize,
            "recognition_interval": self.recognition_interval,
        }


def load_config(config_path: str = "config/settings.json") -> RecognitionConfig:
    default_config = RecognitionConfig()

    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as handle:
                config_dict = json.load(handle)
            return RecognitionConfig.from_dict(config_dict)
        except (json.JSONDecodeError, TypeError) as exc:
            print(f"Warning: Could not load config from {config_path}: {exc}")
            print("Using default configuration")

    return default_config


def save_config(
    config: RecognitionConfig, config_path: str = "config/settings.json"
) -> bool:
    try:
        Path(config_path).parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, "w", encoding="utf-8") as handle:
            json.dump(config.to_dict(), handle, indent=2)
        return True
    except Exception as exc:
        print(f"Error saving config: {exc}")
        return False


def ensure_directories(data_dir: str = "data") -> Dict[str, Path]:
    dirs = {
        "data": Path(data_dir),
        "images": Path(data_dir) / "images",
        "models": Path("models"),
        "config": Path("config"),
    }

    for path in dirs.values():
        path.mkdir(parents=True, exist_ok=True)

    return dirs


def validate_image_path(image_path: str) -> bool:
    valid_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff"}
    path = Path(image_path)
    return path.exists() and path.suffix.lower() in valid_extensions


def get_camera_list() -> list[int]:
    import cv2

    cameras: list[int] = []
    for index in range(10):
        capture = cv2.VideoCapture(index)
        if capture.isOpened():
            cameras.append(index)
            capture.release()
    return cameras


def format_confidence(confidence: float) -> str:
    return f"{confidence * 100:.1f}%"


def create_sample_config(config_path: str = "config/settings.json") -> None:
    config = RecognitionConfig()
    save_config(config, config_path)
    print(f"Sample configuration created at: {config_path}")


def resize_frame(frame, scale: float = 0.5):
    import cv2

    return cv2.resize(frame, (0, 0), fx=scale, fy=scale)


def convert_to_rgb(frame):
    import cv2

    return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)


def convert_to_bgr(frame):
    import cv2

    return cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
