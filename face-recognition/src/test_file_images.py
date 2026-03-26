"""Test face_recognition with a file image instead of webcam."""
import face_recognition
import numpy as np
from PIL import Image

print("Test 1: Create synthetic RGB image with PIL...")
try:
    # Create a simple test image using PIL
    pil_img = Image.new('RGB', (100, 100), color=(128, 128, 128))
    np_img = np.array(pil_img)
    print(f"  PIL image: dtype={np_img.dtype}, shape={np_img.shape}")
    
    locations = face_recognition.face_locations(np_img, model="hog")
    print(f"  SUCCESS! Found {len(locations)} faces")
except Exception as e:
    print(f"  FAILED: {e}")

print("\nTest 2: Create synthetic RGB image with numpy...")
try:
    # Create with numpy directly
    np_img = np.full((100, 100, 3), 128, dtype=np.uint8)
    print(f"  Numpy image: dtype={np_img.dtype}, shape={np_img.shape}")
    
    locations = face_recognition.face_locations(np_img, model="hog")
    print(f"  SUCCESS! Found {len(locations)} faces")
except Exception as e:
    print(f"  FAILED: {e}")

print("\nTest 3: Load an image file with face_recognition.load_image_file...")
try:
    # Save a test image first
    test_img = Image.new('RGB', (200, 200), color=(100, 150, 200))
    test_img.save('test_image.jpg')
    
    # Load with face_recognition's loader
    img = face_recognition.load_image_file('test_image.jpg')
    print(f"  Loaded image: dtype={img.dtype}, shape={img.shape}")
    
    locations = face_recognition.face_locations(img, model="hog")
    print(f"  SUCCESS! Found {len(locations)} faces")
except Exception as e:
    print(f"  FAILED: {e}")

print("\nTest 4: OpenCV image from file (not webcam)...")
try:
    import cv2
    # Use the test image we saved
    bgr = cv2.imread('test_image.jpg')
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    print(f"  OpenCV file image: dtype={rgb.dtype}, shape={rgb.shape}")
    
    locations = face_recognition.face_locations(rgb, model="hog")
    print(f"  SUCCESS! Found {len(locations)} faces")
except Exception as e:
    print(f"  FAILED: {e}")

print("\nDone.")
input("Press Enter to exit...")
