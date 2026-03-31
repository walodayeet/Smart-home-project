#!/usr/bin/env python3
"""
Helper script to register a face using webcam.
Usage: python register_face.py "Your Name"
"""

from __future__ import annotations

import sys
from collections import deque
from pathlib import Path
from typing import Any

import cv2
import requests

API_URL = "http://localhost:5000/register"
PREVIEW_WINDOW_TITLE = "Register Face - Press SPACE to capture"
FRAME_BUFFER_SIZE = 8
TARGET_WIDTH = 1280
TARGET_HEIGHT = 720

FaceBox = tuple[int, int, int, int]
FrameEntry = tuple[Any, list[FaceBox]]


def configure_camera(cap: cv2.VideoCapture) -> None:
    """Apply a higher-resolution webcam configuration when supported."""
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, TARGET_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, TARGET_HEIGHT)
    cap.set(cv2.CAP_PROP_FPS, 30)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)


def scale_faces(faces: list[FaceBox], scale: float) -> list[FaceBox]:
    """Scale detected face boxes back to the original frame size."""
    if scale == 1.0:
        return faces

    scaled_faces: list[FaceBox] = []
    for x, y, w, h in faces:
        scaled_faces.append(
            (
                int(x / scale),
                int(y / scale),
                int(w / scale),
                int(h / scale),
            )
        )
    return scaled_faces


def detect_faces_for_preview(
    frame: Any, face_cascade: cv2.CascadeClassifier
) -> list[FaceBox]:
    """Detect faces with a few more forgiving passes for webcam preview."""
    if face_cascade.empty():
        return []

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    equalized = cv2.equalizeHist(gray)
    min_face_size = max(60, min(frame.shape[0], frame.shape[1]) // 8)

    detection_passes = [
        (equalized, 1.0, 1.10, 5, min_face_size),
        (equalized, 1.0, 1.05, 4, max(48, min_face_size // 2)),
        (
            cv2.resize(equalized, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_LINEAR),
            1.5,
            1.10,
            4,
            min_face_size,
        ),
    ]

    for (
        candidate,
        scale,
        scale_factor,
        min_neighbors,
        candidate_min_face,
    ) in detection_passes:
        faces = face_cascade.detectMultiScale(
            candidate,
            scaleFactor=scale_factor,
            minNeighbors=min_neighbors,
            minSize=(candidate_min_face, candidate_min_face),
        )
        if len(faces) > 0:
            normalized_faces = [
                (int(x), int(y), int(w), int(h)) for x, y, w, h in faces.tolist()
            ]
            return scale_faces(normalized_faces, scale)

    return []


def frame_sharpness(frame: Any) -> float:
    """Estimate sharpness so we can pick a better frame from a short buffer."""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return float(cv2.Laplacian(gray, cv2.CV_64F).var())


def choose_best_frame(recent_frames: deque[FrameEntry]) -> FrameEntry | None:
    """Pick the sharpest recent frame, preferring one with a clearly visible face."""
    if not recent_frames:
        return None

    best_any: FrameEntry | None = None
    best_any_score = float("-inf")
    best_face_frame: FrameEntry | None = None
    best_face_score = float("-inf")

    for frame, faces in recent_frames:
        sharpness = frame_sharpness(frame)
        if sharpness > best_any_score:
            best_any = (frame, faces)
            best_any_score = sharpness

        if faces:
            largest_face_area = max(width * height for _, _, width, height in faces)
            face_score = largest_face_area + (sharpness * 10.0)
            if face_score > best_face_score:
                best_face_frame = (frame, faces)
                best_face_score = face_score

    return best_face_frame or best_any


def draw_preview(frame: Any, faces: list[FaceBox], name: str) -> Any:
    """Render registration hints and local face detection feedback."""
    display_frame = frame.copy()

    for x, y, w, h in faces:
        cv2.rectangle(display_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(
            display_frame,
            "Face Candidate",
            (x, max(25, y - 10)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (0, 255, 0),
            2,
        )

    cv2.putText(
        display_frame,
        "SPACE = Capture | ESC = Cancel",
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2,
    )

    if faces:
        status_text = f"Ready to capture for: {name}"
        status_color = (0, 255, 0)
    else:
        status_text = (
            "Detector missed the face? Press SPACE anyway and let the server validate."
        )
        status_color = (0, 215, 255)

    cv2.putText(
        display_frame,
        status_text,
        (10, 60),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.58,
        status_color,
        2,
    )

    return display_frame


def capture_and_register(name: str) -> bool:
    """Capture face from webcam and register it."""
    print(f"\n{'=' * 50}")
    print(f"Registering Face: {name}")
    print(f"{'=' * 50}\n")

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[ERROR] Could not open webcam")
        return False

    configure_camera(cap)

    print("[OK] Webcam opened successfully")
    print("\nInstructions:")
    print("  - Look directly at the camera")
    print("  - Ensure good lighting on your face")
    print("  - Keep your face centered and still")
    print("  - Press SPACE to capture the best recent frame")
    print("  - Press ESC to cancel\n")

    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )
    if face_cascade.empty():
        print(
            "[WARN] Local preview detector could not be loaded. The API will still validate the captured image."
        )

    recent_frames: deque[FrameEntry] = deque(maxlen=FRAME_BUFFER_SIZE)
    captured = False
    image_data: Any | None = None

    while not captured:
        ret, frame = cap.read()
        if not ret:
            print("[ERROR] Failed to read frame")
            break

        faces = detect_faces_for_preview(frame, face_cascade)
        recent_frames.append((frame.copy(), faces))
        display_frame = draw_preview(frame, faces, name)
        cv2.imshow(PREVIEW_WINDOW_TITLE, display_frame)

        key = cv2.waitKey(1) & 0xFF

        if key == 32:  # SPACE
            best_entry = choose_best_frame(recent_frames)
            if best_entry is None:
                print("[ERROR] No frame available to capture")
                continue

            image_data, best_faces = best_entry
            if best_faces:
                print(
                    f"[INFO] Capturing best recent frame with {len(best_faces)} detected face candidate(s)..."
                )
            else:
                print(
                    "[WARN] Local detector did not find a face, but capturing anyway so the API can validate it."
                )
            captured = True
        elif key == 27:  # ESC
            print("[CANCELLED] Registration cancelled")
            cap.release()
            cv2.destroyAllWindows()
            return False

    cap.release()
    cv2.destroyAllWindows()

    if image_data is None:
        print("[ERROR] No image captured")
        return False

    temp_path = Path("temp_register.jpg")
    cv2.imwrite(str(temp_path), image_data)

    print("[UPLOAD] Uploading to API...")

    try:
        with open(temp_path, "rb") as image_file:
            files = {"image": ("face.jpg", image_file, "image/jpeg")}
            data = {"name": name}
            response = requests.post(API_URL, files=files, data=data, timeout=10)

        temp_path.unlink(missing_ok=True)

        if response.status_code == 200:
            result = response.json()
            print("\n[SUCCESS] Registration successful!")
            print(f"   ID: {result.get('id', 'N/A')}")
            print(f"   Name: {result.get('name', name)}")
            print(f"   Message: {result.get('message', 'Face registered')}")
            return True

        print(f"\n[ERROR] Registration failed: {response.status_code}")
        print(f"   {response.text}")
        return False

    except requests.exceptions.ConnectionError:
        print("\n[ERROR] Could not connect to API server")
        print("   Make sure the server is running: python src/api_deepface.py")
        return False
    except Exception as exc:
        print(f"\n[ERROR] {exc}")
        return False


def main() -> None:
    if len(sys.argv) < 2:
        print('Usage: python register_face.py "Your Name"')
        print("\nExample:")
        print('  python register_face.py "Minh"')
        sys.exit(1)

    name = sys.argv[1]

    if not name.strip():
        print("[ERROR] Name cannot be empty")
        sys.exit(1)

    success = capture_and_register(name)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
