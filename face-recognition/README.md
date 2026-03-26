# Face Recognition System

A Python-based face recognition system using OpenCV and the face-recognition library.

## Features

- Real-time face detection and recognition
- Face encoding and storage
- Support for multiple known faces
- Easy-to-use CLI interface
- Configurable recognition tolerance

## Project Structure

```
face-recognition/
├── src/              # Source code
├── data/             # Face data storage
├── models/           # Pre-trained models
├── tests/            # Unit tests
├── config/           # Configuration files
├── requirements.txt  # Python dependencies
└── README.md         # This file
```

## Installation

1. Install Python 3.8+
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

```bash
python src/main.py
```

## Common Commands

```bash
# Add a face from webcam
python src/main.py add "Your Name"

# Add a face from an image
python src/main.py add "Your Name" --image path/to/photo.jpg

# List registered faces
python src/main.py list-faces

# Start webcam recognition
python src/main.py recognize

# Recognize from image and save result
python src/main.py recognize-image input.jpg --output result.jpg
```

## Requirements

- Python 3.8+
- OpenCV
- face-recognition
- NumPy
- Pillow

## License

MIT License
