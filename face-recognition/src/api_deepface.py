from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from deepface import DeepFace
from flask import Flask, jsonify, request
from flask_cors import CORS
from PIL import Image

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024

DATA_DIR = Path("data")
IMAGES_DIR = DATA_DIR / "images"
DB_FILE = DATA_DIR / "face_db.json"

MODEL_NAME = "Facenet512"
DETECTOR_BACKEND = "opencv"
DISTANCE_METRIC = "cosine"
THRESHOLD = 0.40


def load_face_database() -> dict[str, Any]:
    if not DB_FILE.exists():
        return {}
    
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_face_database(db: dict[str, Any]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2)


@app.get("/health")
def health() -> Any:
    return jsonify({"status": "ok", "engine": "DeepFace", "model": MODEL_NAME})


@app.post("/recognize")
def recognize() -> Any:
    uploaded_file = request.files.get("image")
    if uploaded_file is None or uploaded_file.filename == "":
        logger.warning("Recognize request missing image")
        return jsonify({"message": "Missing image upload"}), 400

    logger.info(f"Processing recognition request: {uploaded_file.filename}")
    db = load_face_database()
    
    if not db:
        logger.info("No faces registered in database")
        return jsonify({
            "ownerRecognized": False,
            "message": "No registered faces in database",
            "primaryMatch": None,
            "faces": []
        })

    try:
        temp_path = DATA_DIR / "temp_upload.jpg"
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        
        image = Image.open(uploaded_file.stream).convert("RGB")
        image.save(temp_path)

        registered_images = []
        for person_id, person_data in db.items():
            img_path = person_data.get("image_path")
            if img_path and Path(img_path).exists():
                registered_images.append({
                    "path": img_path,
                    "name": person_data["name"],
                    "person_id": person_id
                })

        if not registered_images:
            return jsonify({
                "ownerRecognized": False,
                "message": "No valid face images found in database",
                "primaryMatch": None,
                "faces": []
            })

        best_match = None
        best_distance = float('inf')
        best_name = "Unknown"

        for reg_face in registered_images:
            try:
                result = DeepFace.verify(
                    img1_path=str(temp_path),
                    img2_path=reg_face["path"],
                    model_name=MODEL_NAME,
                    detector_backend=DETECTOR_BACKEND,
                    distance_metric=DISTANCE_METRIC,
                    enforce_detection=True
                )
                
                distance = result.get("distance", 1.0)
                verified = result.get("verified", False)
                
                if verified and distance < best_distance:
                    best_distance = distance
                    best_name = reg_face["name"]
                    best_match = {
                        "name": best_name,
                        "confidence": round(distance, 4),
                        "id": reg_face["person_id"]
                    }
            
            except Exception as e:
                logger.debug(f"Verification failed against {reg_face['name']}: {e}")
                continue

        if temp_path.exists():
            temp_path.unlink()

        owner_recognized = best_match is not None
        
        if owner_recognized:
            logger.info(f"Owner recognized: {best_name} (distance: {best_distance:.4f})")
        else:
            logger.info("Unknown visitor detected")
        
        response = {
            "ownerRecognized": owner_recognized,
            "message": f"Welcome back, {best_name}!" if owner_recognized else "Unknown visitor detected",
            "primaryMatch": best_match,
            "faces": [best_match] if best_match else []
        }
        
        return jsonify(response)

    except Exception as exc:
        logger.error(f"Recognition failed: {exc}", exc_info=True)
        return jsonify({"message": f"Failed to process image: {exc}"}), 500


@app.post("/register")
def register() -> Any:
    uploaded_file = request.files.get("image")
    name = request.form.get("name")
    
    if not uploaded_file or not name:
        logger.warning("Register request missing image or name")
        return jsonify({"message": "Missing image or name"}), 400

    logger.info(f"Registering new face: {name}")

    try:
        db = load_face_database()
        
        person_count = len(db)
        person_id = f"{name.lower().replace(' ', '_')}_{person_count + 1}"
        
        IMAGES_DIR.mkdir(parents=True, exist_ok=True)
        image_path = IMAGES_DIR / f"{person_id}.jpg"
        
        image = Image.open(uploaded_file.stream).convert("RGB")
        image.save(image_path)
        
        try:
            DeepFace.extract_faces(
                img_path=str(image_path),
                detector_backend=DETECTOR_BACKEND,
                enforce_detection=True
            )
        except Exception as e:
            if image_path.exists():
                image_path.unlink()
            logger.warning(f"Face detection failed for {name}: {e}")
            return jsonify({"message": f"No face detected in image: {e}"}), 400
        
        db[person_id] = {
            "name": name,
            "image_path": str(image_path),
            "person_id": person_id
        }
        
        save_face_database(db)
        
        logger.info(f"Successfully registered {name} (ID: {person_id})")
        return jsonify({
            "message": f"Successfully registered {name}",
            "id": person_id,
            "name": name
        })
    
    except Exception as exc:
        return jsonify({"message": f"Failed to register face: {exc}"}), 500


@app.get("/faces")
def list_faces() -> Any:
    db = load_face_database()
    
    faces = [
        {
            "person_id": person_id,
            "name": data["name"],
            "image_path": data.get("image_path", "")
        }
        for person_id, data in db.items()
    ]
    
    return jsonify({
        "count": len(faces),
        "faces": faces
    })


@app.delete("/faces/<person_id>")
def delete_face(person_id: str) -> Any:
    db = load_face_database()
    
    if person_id not in db:
        return jsonify({"message": "Face not found"}), 404
    
    img_path = Path(db[person_id].get("image_path", ""))
    if img_path.exists():
        img_path.unlink()
    
    del db[person_id]
    save_face_database(db)
    
    return jsonify({"message": f"Deleted {person_id}"})


if __name__ == "__main__":
    print("=" * 60)
    print("DeepFace Face Recognition API")
    print("=" * 60)
    print(f"Model: {MODEL_NAME}")
    print(f"Detector: {DETECTOR_BACKEND}")
    print(f"Data Directory: {DATA_DIR.absolute()}")
    print("=" * 60)
    print("\nEndpoints:")
    print("  GET  /health      - Health check")
    print("  POST /recognize   - Recognize face")
    print("  POST /register    - Register face")
    print("  GET  /faces       - List faces")
    print("  DELETE /faces/<id> - Delete face")
    print("\nServer: http://0.0.0.0:5000")
    print("=" * 60)
    
    app.run(host="0.0.0.0", port=5000, debug=False)
