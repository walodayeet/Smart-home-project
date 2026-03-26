"""
Core face recognition module.
Handles face detection, encoding, and recognition.
"""

import pickle
from typing import List, Optional, Tuple

import cv2
import face_recognition
import numpy as np


class FaceRecognizer:
    """Main class for face recognition operations."""

    def __init__(self, tolerance: float = 0.6, model: str = "hog"):
        """
        Initialize the face recognizer.

        Args:
            tolerance: Face matching tolerance (lower = stricter, default 0.6)
            model: Detection model - 'hog' (faster) or 'cnn' (more accurate)
        """
        self.tolerance = tolerance
        self.model = model
        self.known_face_encodings: List[np.ndarray] = []
        self.known_face_names: List[str] = []

    def load_image(self, image_path: str) -> np.ndarray:
        """Load an image from file path."""
        return face_recognition.load_image_file(image_path)

    def detect_faces(
        self, image: np.ndarray, upsample: int = 1
    ) -> List[Tuple[int, int, int, int]]:
        """
        Detect faces in an image.

        Args:
            image: Input image (RGB format)
            upsample: Number of times to upsample image

        Returns:
            List of face locations as (top, right, bottom, left)
        """
        return face_recognition.face_locations(
            image,
            number_of_times_to_upsample=upsample,
            model=self.model,
        )

    def encode_faces(
        self,
        image: np.ndarray,
        face_locations: Optional[List[Tuple[int, int, int, int]]] = None,
    ) -> List[np.ndarray]:
        """Generate face encodings from an image."""
        return face_recognition.face_encodings(
            image,
            known_face_locations=face_locations,
        )

    def add_known_face(self, image_path: str, name: str) -> bool:
        """Add a known face to memory."""
        try:
            image = self.load_image(image_path)
            face_locations = self.detect_faces(image)

            if not face_locations:
                print(f"No face found in {image_path}")
                return False

            if len(face_locations) > 1:
                print(f"Multiple faces found in {image_path}, using the first one")

            encodings = self.encode_faces(image, [face_locations[0]])
            if not encodings:
                print(f"Could not encode face from {image_path}")
                return False

            self.known_face_encodings.append(encodings[0])
            self.known_face_names.append(name)
            return True
        except Exception as exc:
            print(f"Error adding face from {image_path}: {exc}")
            return False

    def recognize_faces(
        self, image: np.ndarray
    ) -> List[Tuple[Tuple[int, int, int, int], str, float]]:
        """
        Recognize faces in an image.

        Returns:
            List of tuples: (face_location, name, confidence)
        """
        face_locations = self.detect_faces(image)
        face_encodings = self.encode_faces(image, face_locations)

        results: List[Tuple[Tuple[int, int, int, int], str, float]] = []

        for face_location, face_encoding in zip(face_locations, face_encodings):
            name = "Unknown"
            confidence = 0.0

            if self.known_face_encodings:
                matches = face_recognition.compare_faces(
                    self.known_face_encodings,
                    face_encoding,
                    tolerance=self.tolerance,
                )
                face_distances = face_recognition.face_distance(
                    self.known_face_encodings,
                    face_encoding,
                )

                if True in matches:
                    best_match_index = int(np.argmin(face_distances))
                    if matches[best_match_index]:
                        name = self.known_face_names[best_match_index]
                        confidence = float(1.0 - face_distances[best_match_index])

            results.append((face_location, name, confidence))

        return results

    def save_database(self, filepath: str) -> bool:
        """Save known faces database to file."""
        try:
            data = {
                "encodings": self.known_face_encodings,
                "names": self.known_face_names,
            }
            with open(filepath, "wb") as handle:
                pickle.dump(data, handle)
            return True
        except Exception as exc:
            print(f"Error saving database: {exc}")
            return False

    def load_database(self, filepath: str) -> bool:
        """Load known faces database from file."""
        try:
            with open(filepath, "rb") as handle:
                data = pickle.load(handle)
            self.known_face_encodings = data["encodings"]
            self.known_face_names = data["names"]
            return True
        except Exception as exc:
            print(f"Error loading database: {exc}")
            return False

    def clear_database(self) -> None:
        """Clear all known faces."""
        self.known_face_encodings = []
        self.known_face_names = []

    def get_known_faces_count(self) -> int:
        """Return the number of known faces."""
        return len(self.known_face_names)


def draw_face_boxes(
    image: np.ndarray,
    results: List[Tuple[Tuple[int, int, int, int], str, float]],
    font_scale: float = 0.6,
    thickness: int = 2,
) -> np.ndarray:
    """Draw bounding boxes and labels on detected faces."""
    for (top, right, bottom, left), name, confidence in results:
        color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
        cv2.rectangle(image, (left, top), (right, bottom), color, thickness)

        label = f"{name} ({confidence:.2f})"
        label_size, _ = cv2.getTextSize(
            label,
            cv2.FONT_HERSHEY_SIMPLEX,
            font_scale,
            thickness,
        )
        label_top = max(top, label_size[1] + 10)

        cv2.rectangle(
            image,
            (left, label_top - label_size[1] - 10),
            (left + label_size[0], label_top),
            color,
            cv2.FILLED,
        )
        cv2.putText(
            image,
            label,
            (left, label_top - 5),
            cv2.FONT_HERSHEY_SIMPLEX,
            font_scale,
            (255, 255, 255),
            thickness,
        )

    return image
