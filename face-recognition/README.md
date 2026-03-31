# Face Recognition Service

DeepFace-based face recognition API for the Smart Home project.

This service is the current backend used by the Android app. It accepts a camera image, compares it against locally registered faces, and returns whether the owner was recognized.

## Current runtime entrypoint

Use this API server:

```bash
python src/api_deepface.py
```

> Note: `src/main.py` and `src/api.py` still exist in the repository, but the active flow for the Android app is the DeepFace API in `src/api_deepface.py`.

## Features

- DeepFace-based face verification
- Local face registration and storage
- HTTP API for Android app integration
- Health check endpoint
- Face listing and deletion endpoints
- CORS enabled for local development

## Dependencies

From `requirements.txt`:

- `deepface>=0.0.79`
- `flask>=3.0.0`
- `flask-cors>=6.0.0`
- `opencv-python>=4.8.0`
- `pillow>=10.0.0`
- `tf-keras>=2.21.0`
- `tensorflow>=2.21.0`
- `requests>=2.31.0`

## Project structure

```text
face-recognition/
├── config/              # Optional config files from older flow
├── data/                # Runtime database and stored face images
│   ├── face_db.json     # Registered face metadata
│   └── images/          # Saved face images
├── face-venv/           # Local virtual environment (if created)
├── src/
│   ├── api_deepface.py  # Current DeepFace API server
│   ├── api.py           # Older Flask API implementation
│   └── main.py          # Older CLI workflow
├── tests/
├── requirements.txt
└── README.md
```

## Installation

From the `face-recognition` directory:

```bash
python -m venv face-venv
face-venv\Scripts\activate
pip install -r requirements.txt
```

## Run the API

```bash
python src/api_deepface.py
```

When the server starts, it listens on:

```text
http://0.0.0.0:5000
```

For the Android emulator, the app should call:

```text
http://10.0.2.2:5000
```

## API endpoints

### `GET /health`
Health check.

Example response:

```json
{
  "status": "ok",
  "engine": "DeepFace",
  "model": "Facenet512"
}
```

### `POST /recognize`
Recognize a face from an uploaded image.

Form field:
- `image`: uploaded JPEG/PNG image

Example response when matched:

```json
{
  "ownerRecognized": true,
  "message": "Welcome back, John!",
  "primaryMatch": {
    "name": "John",
    "confidence": 0.1234,
    "id": "john_1"
  },
  "faces": [
    {
      "name": "John",
      "confidence": 0.1234,
      "id": "john_1"
    }
  ]
}
```

Example response when no match exists:

```json
{
  "ownerRecognized": false,
  "message": "Unknown visitor detected",
  "primaryMatch": null,
  "faces": []
}
```

### `POST /register`
Register a new face.

Form fields:
- `name`: person name
- `image`: uploaded image containing one face

Example response:

```json
{
  "message": "Successfully registered John",
  "id": "john_1",
  "name": "John"
}
```

### `GET /faces`
List all registered faces.

Example response:

```json
{
  "count": 1,
  "faces": [
    {
      "person_id": "john_1",
      "name": "John",
      "image_path": "data/images/john_1.jpg"
    }
  ]
}
```

### `DELETE /faces/<person_id>`
Delete a registered face.

Example:

```bash
curl -X DELETE http://127.0.0.1:5000/faces/john_1
```

## Register and test from the command line

### Register a face

```bash
curl -X POST http://127.0.0.1:5000/register \
  -F "name=John" \
  -F "image=@test_image.jpg"
```

### Recognize a face

```bash
curl -X POST http://127.0.0.1:5000/recognize \
  -F "image=@test_image.jpg"
```

### List faces

```bash
curl http://127.0.0.1:5000/faces
```

## Android app integration

The Android app is configured to send camera frames to this service.

Expected local development flow:
1. Start `python src/api_deepface.py`
2. Register at least one face with `POST /register`
3. Run the Android app in the emulator
4. Trigger face recognition from the camera screen

If the API is not running, the app will fail to reach the recognition service.

## Runtime details

Current defaults in `src/api_deepface.py`:

- Model: `Facenet512`
- Detector backend: `opencv`
- Distance metric: `cosine`
- Threshold: `0.40`
- Max upload size: `10 MB`

## Notes

- Face data is stored locally under `data/`
- Registered image paths are persisted in `data/face_db.json`
- Recognition compares the uploaded image against every registered face image
- If no registered faces exist, `/recognize` returns `ownerRecognized: false`

## Troubleshooting

### Server starts but recognition fails
- Make sure the uploaded image contains a clear face
- Make sure at least one face has been registered first
- Check Python logs printed by `api_deepface.py`

### Android emulator cannot connect
- Ensure the API is running on port `5000`
- Use `10.0.2.2` from the emulator, not `localhost`

### TensorFlow / DeepFace install issues
- Recreate the virtual environment
- Reinstall with `pip install -r requirements.txt`
- Confirm your Python version is compatible with the installed TensorFlow package
