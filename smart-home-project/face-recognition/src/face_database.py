"""
Face database management module.
Handles storage and retrieval of face data.
"""

import json
import pickle
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class FaceDatabase:
    """Manages face data storage and retrieval."""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.images_dir = self.data_dir / "images"
        self.images_dir.mkdir(exist_ok=True)

        self.metadata_file = self.data_dir / "metadata.json"
        self.encodings_file = self.data_dir / "encodings.pkl"

        self.metadata: Dict = self._load_metadata()

    def _load_metadata(self) -> Dict:
        if self.metadata_file.exists():
            with open(self.metadata_file, "r", encoding="utf-8") as handle:
                return json.load(handle)
        return {"faces": {}}

    def _save_metadata(self) -> None:
        with open(self.metadata_file, "w", encoding="utf-8") as handle:
            json.dump(self.metadata, handle, indent=2)

    def add_face(
        self,
        person_id: str,
        image_path: str,
        name: str,
        encoding: Optional[List] = None,
    ) -> bool:
        try:
            image_ext = Path(image_path).suffix
            dest_path = self.images_dir / f"{person_id}{image_ext}"
            shutil.copy2(image_path, dest_path)

            self.metadata["faces"][person_id] = {
                "name": name,
                "image_path": str(dest_path),
                "added_at": datetime.now().isoformat(),
                "encoding_path": str(self.encodings_file) if encoding else None,
            }
            self._save_metadata()

            if encoding is not None:
                self._save_encoding(person_id, encoding)

            return True
        except Exception as exc:
            print(f"Error adding face: {exc}")
            return False

    def _save_encoding(self, person_id: str, encoding: List) -> None:
        encodings: Dict[str, List] = {}
        if self.encodings_file.exists():
            with open(self.encodings_file, "rb") as handle:
                encodings = pickle.load(handle)

        encodings[person_id] = encoding

        with open(self.encodings_file, "wb") as handle:
            pickle.dump(encodings, handle)

    def get_encoding(self, person_id: str) -> Optional[List]:
        if not self.encodings_file.exists():
            return None

        with open(self.encodings_file, "rb") as handle:
            encodings = pickle.load(handle)

        return encodings.get(person_id)

    def get_all_encodings(self) -> Dict[str, List]:
        if not self.encodings_file.exists():
            return {}

        with open(self.encodings_file, "rb") as handle:
            return pickle.load(handle)

    def get_face_info(self, person_id: str) -> Optional[Dict]:
        return self.metadata["faces"].get(person_id)

    def get_all_faces(self) -> Dict[str, Dict]:
        return self.metadata["faces"]

    def remove_face(self, person_id: str) -> bool:
        if person_id not in self.metadata["faces"]:
            return False

        try:
            face_info = self.metadata["faces"][person_id]
            image_path = Path(face_info["image_path"])
            if image_path.exists():
                image_path.unlink()

            if self.encodings_file.exists():
                with open(self.encodings_file, "rb") as handle:
                    encodings = pickle.load(handle)

                if person_id in encodings:
                    del encodings[person_id]
                    with open(self.encodings_file, "wb") as handle:
                        pickle.dump(encodings, handle)

            del self.metadata["faces"][person_id]
            self._save_metadata()
            return True
        except Exception as exc:
            print(f"Error removing face: {exc}")
            return False

    def update_name(self, person_id: str, new_name: str) -> bool:
        if person_id not in self.metadata["faces"]:
            return False

        self.metadata["faces"][person_id]["name"] = new_name
        self.metadata["faces"][person_id]["updated_at"] = datetime.now().isoformat()
        self._save_metadata()
        return True

    def get_face_count(self) -> int:
        return len(self.metadata["faces"])

    def clear_all(self) -> bool:
        try:
            for file in self.images_dir.iterdir():
                if file.is_file():
                    file.unlink()

            if self.encodings_file.exists():
                self.encodings_file.unlink()

            self.metadata = {"faces": {}}
            self._save_metadata()
            return True
        except Exception as exc:
            print(f"Error clearing database: {exc}")
            return False
