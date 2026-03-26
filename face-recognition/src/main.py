"""
Main application entry point for face recognition system.
Provides CLI interface for training and recognition.
"""

import json
import os
from pathlib import Path
from typing import Optional

import click
import cv2
import numpy as np

from face_database import FaceDatabase
from face_recognizer import FaceRecognizer, draw_face_boxes


def load_config(config_path: str = "config/settings.json") -> dict:
    """Load configuration from JSON file."""
    default_config = {
        "tolerance": 0.6,
        "model": "hog",
        "data_dir": "data",
        "camera_index": 0,
        "frame_resize": 0.5,
        "recognition_interval": 5,
    }

    try:
        with open(config_path, "r", encoding="utf-8") as handle:
            config = json.load(handle)
            default_config.update(config)
    except FileNotFoundError:
        pass

    return default_config


@click.group()
@click.option(
    "--config",
    "config_path",
    default="config/settings.json",
    help="Configuration file path",
)
@click.pass_context
def cli(ctx, config_path: str):
    """Face Recognition System CLI."""
    ctx.ensure_object(dict)
    ctx.obj["config"] = load_config(config_path)


@cli.command()
@click.argument("name")
@click.option(
    "--image", "image_path", help="Image file path (if not provided, uses camera)"
)
@click.option("--camera", default=0, help="Camera index")
@click.pass_context
def add(ctx, name: str, image_path: Optional[str], camera: int):
    """Add a new face to the database."""
    config = ctx.obj["config"]
    db = FaceDatabase(config["data_dir"])
    recognizer = FaceRecognizer(
        tolerance=config["tolerance"],
        model=config["model"],
    )

    if image_path:
        if not os.path.exists(image_path):
            click.echo(f"Error: Image file not found: {image_path}")
            return

        success = recognizer.add_known_face(image_path, name)
        if success:
            image = recognizer.load_image(image_path)
            locations = recognizer.detect_faces(image)
            encoding = recognizer.encode_faces(image, [locations[0]])[0]

            person_id = f"{name.lower().replace(' ', '_')}_{db.get_face_count() + 1}"
            db.add_face(person_id, image_path, name, encoding.tolist())
            recognizer.save_database(str(Path(config["data_dir"]) / "faces.pkl"))
            click.echo(f"Added {name} to database")
        else:
            click.echo(f"Failed to add {name}")
        return

    click.echo("Press 's' to save, 'q' to quit")
    cap = cv2.VideoCapture(camera)
    if not cap.isOpened():
        click.echo(f"Error: Could not open camera {camera}")
        return

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                continue

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            locations = recognizer.detect_faces(rgb_frame)

            display_frame = frame.copy()
            for top, right, bottom, left in locations:
                cv2.rectangle(
                    display_frame, (left, top), (right, bottom), (0, 255, 0), 2
                )

            cv2.imshow("Add Face - Press s to save, q to quit", display_frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            if key == ord("s") and locations:
                encoding = recognizer.encode_faces(rgb_frame, [locations[0]])[0]
                person_id = (
                    f"{name.lower().replace(' ', '_')}_{db.get_face_count() + 1}"
                )
                image_file = Path(config["data_dir"]) / "images" / f"{person_id}.jpg"
                image_file.parent.mkdir(parents=True, exist_ok=True)
                cv2.imwrite(str(image_file), frame)

                db.add_face(person_id, str(image_file), name, encoding.tolist())
                recognizer.known_face_encodings.append(encoding)
                recognizer.known_face_names.append(name)
                recognizer.save_database(str(Path(config["data_dir"]) / "faces.pkl"))
                click.echo(f"Added {name} to database")
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()


@cli.command()
@click.option("--camera", default=0, help="Camera index")
@click.option("--tolerance", type=float, help="Recognition tolerance")
@click.pass_context
def recognize(ctx, camera: int, tolerance: Optional[float]):
    """Start real-time face recognition."""
    config = ctx.obj["config"]
    if tolerance is not None:
        config["tolerance"] = tolerance

    db = FaceDatabase(config["data_dir"])
    recognizer = FaceRecognizer(
        tolerance=config["tolerance"],
        model=config["model"],
    )

    faces = db.get_all_faces()
    for person_id, face_info in faces.items():
        encoding = db.get_encoding(person_id)
        if encoding is not None:
            recognizer.known_face_encodings.append(np.array(encoding))
            recognizer.known_face_names.append(face_info["name"])

    click.echo(f"Loaded {recognizer.get_known_faces_count()} known faces")
    click.echo("Press 'q' to quit")

    cap = cv2.VideoCapture(camera)
    if not cap.isOpened():
        click.echo(f"Error: Could not open camera {camera}")
        return

    frame_count = 0
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                continue

            frame_count += 1
            if frame_count % config["recognition_interval"] != 0:
                cv2.imshow("Face Recognition", frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
                continue

            small_frame = cv2.resize(
                frame,
                (0, 0),
                fx=config["frame_resize"],
                fy=config["frame_resize"],
            )
            rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
            results = recognizer.recognize_faces(rgb_frame)

            scale = 1 / config["frame_resize"]
            scaled_results = []
            for (top, right, bottom, left), name, confidence in results:
                scaled_results.append(
                    (
                        (
                            int(top * scale),
                            int(right * scale),
                            int(bottom * scale),
                            int(left * scale),
                        ),
                        name,
                        confidence,
                    )
                )

            display_frame = draw_face_boxes(frame, scaled_results)
            cv2.imshow("Face Recognition", display_frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()


@cli.command("list-faces")
@click.pass_context
def list_faces(ctx):
    """List all faces in the database."""
    config = ctx.obj["config"]
    db = FaceDatabase(config["data_dir"])

    faces = db.get_all_faces()
    if not faces:
        click.echo("No faces in database")
        return

    click.echo(f"\n{'ID':<30} {'Name':<30} {'Added':<25}")
    click.echo("-" * 85)
    for person_id, face_info in faces.items():
        added_at = face_info.get("added_at", "Unknown")[:19]
        click.echo(f"{person_id:<30} {face_info['name']:<30} {added_at:<25}")

    click.echo(f"\nTotal: {len(faces)} face(s)")


@cli.command()
@click.argument("person_id")
@click.pass_context
def remove(ctx, person_id: str):
    """Remove a face from the database."""
    config = ctx.obj["config"]
    db = FaceDatabase(config["data_dir"])

    if db.remove_face(person_id):
        click.echo(f"Removed {person_id}")
    else:
        click.echo(f"Face not found: {person_id}")


@cli.command()
@click.confirmation_option(prompt="Are you sure you want to clear all faces?")
@click.pass_context
def clear(ctx):
    """Clear all faces from the database."""
    config = ctx.obj["config"]
    db = FaceDatabase(config["data_dir"])

    if db.clear_all():
        recognizer = FaceRecognizer()
        recognizer.clear_database()
        recognizer.save_database(str(Path(config["data_dir"]) / "faces.pkl"))
        click.echo("Database cleared")
    else:
        click.echo("Failed to clear database")


@cli.command("recognize-image")
@click.argument("image_path")
@click.option("--output", help="Output image path")
@click.option("--tolerance", type=float, help="Recognition tolerance")
@click.pass_context
def recognize_image(
    ctx, image_path: str, output: Optional[str], tolerance: Optional[float]
):
    """Recognize faces in an image file."""
    config = ctx.obj["config"]
    if tolerance is not None:
        config["tolerance"] = tolerance

    if not os.path.exists(image_path):
        click.echo(f"Error: Image file not found: {image_path}")
        return

    db = FaceDatabase(config["data_dir"])
    recognizer = FaceRecognizer(
        tolerance=config["tolerance"],
        model=config["model"],
    )

    faces = db.get_all_faces()
    for person_id, face_info in faces.items():
        encoding = db.get_encoding(person_id)
        if encoding is not None:
            recognizer.known_face_encodings.append(np.array(encoding))
            recognizer.known_face_names.append(face_info["name"])

    click.echo(f"Loaded {recognizer.get_known_faces_count()} known faces")

    image = recognizer.load_image(image_path)
    results = recognizer.recognize_faces(image)

    click.echo(f"\nDetected {len(results)} face(s):")
    for index, (_location, name, confidence) in enumerate(results, start=1):
        click.echo(f"  {index}. {name} (confidence: {confidence:.2f})")

    if output:
        bgr_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        result_image = draw_face_boxes(bgr_image, results)
        cv2.imwrite(output, result_image)
        click.echo(f"\nOutput saved to: {output}")


if __name__ == "__main__":
    cli()
