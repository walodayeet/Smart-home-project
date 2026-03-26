"""
Unit tests for face recognition system.
"""

import os
import shutil
import tempfile
import unittest
from pathlib import Path

import numpy as np

from face_database import FaceDatabase
from face_recognizer import FaceRecognizer
from utils import RecognitionConfig, format_confidence, validate_image_path


class TestFaceRecognizer(unittest.TestCase):
    def setUp(self):
        self.recognizer = FaceRecognizer(tolerance=0.6, model="hog")

    def test_initialization(self):
        self.assertEqual(self.recognizer.tolerance, 0.6)
        self.assertEqual(self.recognizer.model, "hog")
        self.assertEqual(len(self.recognizer.known_face_encodings), 0)
        self.assertEqual(len(self.recognizer.known_face_names), 0)

    def test_clear_database(self):
        self.recognizer.known_face_encodings = [np.zeros(128)]
        self.recognizer.known_face_names = ["Test"]
        self.recognizer.clear_database()
        self.assertEqual(len(self.recognizer.known_face_encodings), 0)
        self.assertEqual(len(self.recognizer.known_face_names), 0)

    def test_get_known_faces_count(self):
        self.assertEqual(self.recognizer.get_known_faces_count(), 0)
        self.recognizer.known_face_names = ["Person1", "Person2"]
        self.assertEqual(self.recognizer.get_known_faces_count(), 2)


class TestFaceDatabase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db = FaceDatabase(self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_initialization(self):
        self.assertTrue(Path(self.temp_dir).exists())
        self.assertTrue(Path(self.temp_dir, "images").exists())
        self.assertEqual(self.db.get_face_count(), 0)

    def test_add_and_get_face(self):
        dummy_image = Path(self.temp_dir, "test_image.jpg")
        dummy_image.touch()

        success = self.db.add_face(
            "person_1", str(dummy_image), "John Doe", [0.1] * 128
        )
        self.assertTrue(success)
        self.assertEqual(self.db.get_face_count(), 1)

        face_info = self.db.get_face_info("person_1")
        self.assertIsNotNone(face_info)
        self.assertEqual(face_info["name"], "John Doe")

    def test_update_name(self):
        dummy_image = Path(self.temp_dir, "test_image.jpg")
        dummy_image.touch()

        self.db.add_face("person_1", str(dummy_image), "John Doe")
        success = self.db.update_name("person_1", "Jane Doe")
        self.assertTrue(success)

        face_info = self.db.get_face_info("person_1")
        self.assertEqual(face_info["name"], "Jane Doe")

    def test_remove_face(self):
        dummy_image = Path(self.temp_dir, "test_image.jpg")
        dummy_image.touch()

        self.db.add_face("person_1", str(dummy_image), "John Doe")
        self.assertEqual(self.db.get_face_count(), 1)

        success = self.db.remove_face("person_1")
        self.assertTrue(success)
        self.assertEqual(self.db.get_face_count(), 0)

    def test_clear_all(self):
        for index in range(3):
            dummy_image = Path(self.temp_dir, f"test_image_{index}.jpg")
            dummy_image.touch()
            self.db.add_face(f"person_{index}", str(dummy_image), f"Person {index}")

        self.assertEqual(self.db.get_face_count(), 3)
        success = self.db.clear_all()
        self.assertTrue(success)
        self.assertEqual(self.db.get_face_count(), 0)


class TestUtils(unittest.TestCase):
    def test_recognition_config_defaults(self):
        config = RecognitionConfig()
        self.assertEqual(config.tolerance, 0.6)
        self.assertEqual(config.model, "hog")
        self.assertEqual(config.data_dir, "data")

    def test_recognition_config_from_dict(self):
        config_dict = {
            "tolerance": 0.5,
            "model": "cnn",
            "data_dir": "custom_data",
        }
        config = RecognitionConfig.from_dict(config_dict)
        self.assertEqual(config.tolerance, 0.5)
        self.assertEqual(config.model, "cnn")
        self.assertEqual(config.data_dir, "custom_data")

    def test_recognition_config_to_dict(self):
        config = RecognitionConfig(tolerance=0.5, model="cnn")
        config_dict = config.to_dict()
        self.assertEqual(config_dict["tolerance"], 0.5)
        self.assertEqual(config_dict["model"], "cnn")

    def test_validate_image_path(self):
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as handle:
            temp_path = handle.name

        try:
            self.assertTrue(validate_image_path(temp_path))
            self.assertFalse(validate_image_path("/non/existent/file.jpg"))

            with tempfile.NamedTemporaryFile(
                suffix=".txt", delete=False
            ) as invalid_handle:
                invalid_path = invalid_handle.name
            self.assertFalse(validate_image_path(invalid_path))
            os.unlink(invalid_path)
        finally:
            os.unlink(temp_path)

    def test_format_confidence(self):
        self.assertEqual(format_confidence(0.85), "85.0%")
        self.assertEqual(format_confidence(0.5), "50.0%")
        self.assertEqual(format_confidence(1.0), "100.0%")


if __name__ == "__main__":
    unittest.main()
