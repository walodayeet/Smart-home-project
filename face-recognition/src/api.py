"""
HTTP API for the standalone face-recognition project.
Exposes a minimal endpoint for the Android demo app.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

import numpy as np
from flask import Flask, jsonify, request
from PIL import Image

from face_database import FaceDatabase
from face_recognizer import FaceRecognizer


app = Flask(__name__)


def load_config(config_path: str = "config/settings.json") -> dict[str, Any]:
    default_config: dict[str, Any] = {
        "tolerance": 0.6,
        "model": "hog",
        "data_dir": "data",
    }

    try:
        with open(config_path, "r", encoding="utf-8") as handle:
            config = json.load(handle)
            default_config.update(config)
    except FileNotFoundError:
        pass

    return default_config


def build_recognizer(config: dict[str, Any]) -> FaceRecognizer:
    db = FaceDatabase(config["data_dir"])
    recognizer = FaceRecognizer(
        tolerance=config["tolerance"],
        model=config["model"],
    )

    for person_id, face_info in db.get_all_faces().items():
        encoding = db.get_encoding(person_id)
        if encoding is not None:
            recognizer.known_face_encodings.append(np.array(encoding))
            recognizer.known_face_names.append(face_info["name"])

    return recognizer


def result_to_dict(
    result: tuple[tuple[int, int, int, int], str, float],
) -> dict[str, Any]:
    (top, right, bottom, left), name, confidence = result
    return {
        "name": name,
        "confidence": round(float(confidence), 4),
        "top": int(top),
        "right": int(right),
        "bottom": int(bottom),
        "left": int(left),
    }


def select_primary_match(
    results: list[tuple[tuple[int, int, int, int], str, float]],
) -> Optional[dict[str, Any]]:
    recognized = [result for result in results if result[1] != "Unknown"]
    if not recognized:
        return None

    best_result = max(recognized, key=lambda item: item[2])
    return result_to_dict(best_result)


@app.get("/health")
def health() -> Any:
    return jsonify({"status": "ok"})


@app.post("/recognize")
def recognize() -> Any:
    uploaded_file = request.files.get("image")
    if uploaded_file is None or uploaded_file.filename == "":
        return jsonify({"message": "Missing image upload"}), 400

    config = load_config()
    recognizer = build_recognizer(config)

    try:
        image = Image.open(uploaded_file.stream).convert("RGB")
        np_image = np.array(image)
        results = recognizer.recognize_faces(np_image)
    except Exception as exc:  # pragma: no cover - defensive runtime handling
        return jsonify({"message": f"Failed to process image: {exc}"}), 500

    primary_match = select_primary_match(results)
    owner_recognized = primary_match is not None

    response = {
        "ownerRecognized": owner_recognized,
        "message": "Owner recognized"
        if owner_recognized
        else "Unknown visitor detected",
        "primaryMatch": primary_match,
        "faces": [result_to_dict(result) for result in results],
    }
    return jsonify(response)


if __name__ == "__main__":
    config_path = Path("config/settings.json")
    if not config_path.exists():
        print("Warning: config/settings.json not found. Using defaults.")
    app.run(host="0.0.0.0", port=5000, debug=False)
