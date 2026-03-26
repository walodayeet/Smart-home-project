"""Debug script to test face_recognition with webcam frame."""
import cv2
import numpy as np
import face_recognition

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("ERROR: Could not open camera")
    exit(1)

print("Camera opened. Reading frame...")

ret, frame = cap.read()
cap.release()

if not ret or frame is None:
    print("Failed to read frame")
    exit(1)

print(f"Frame: dtype={frame.dtype}, shape={frame.shape}")

# Convert to RGB
rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
print(f"RGB frame: dtype={rgb_frame.dtype}, shape={rgb_frame.shape}")

# Make contiguous copy
rgb_copy = np.ascontiguousarray(rgb_frame, dtype=np.uint8)
print(f"RGB copy: dtype={rgb_copy.dtype}, shape={rgb_copy.shape}, contiguous={rgb_copy.flags['C_CONTIGUOUS']}")

# Test 1: Try with the copy
print("\nTest 1: face_locations with contiguous copy...")
try:
    locations = face_recognition.face_locations(rgb_copy, model="hog")
    print(f"  SUCCESS! Found {len(locations)} face(s)")
except Exception as e:
    print(f"  FAILED: {e}")

# Test 2: Try with explicit array creation
print("\nTest 2: face_locations with np.array()...")
try:
    rgb_new = np.array(rgb_frame, dtype=np.uint8)
    locations = face_recognition.face_locations(rgb_new, model="hog")
    print(f"  SUCCESS! Found {len(locations)} face(s)")
except Exception as e:
    print(f"  FAILED: {e}")

# Test 3: Try with copy()
print("\nTest 3: face_locations with .copy()...")
try:
    rgb_copied = rgb_frame.copy()
    locations = face_recognition.face_locations(rgb_copied, model="hog")
    print(f"  SUCCESS! Found {len(locations)} face(s)")
except Exception as e:
    print(f"  FAILED: {e}")

# Test 4: Check if it's a stride issue - create fresh array
print("\nTest 4: face_locations with zeros + data copy...")
try:
    h, w, c = rgb_frame.shape
    fresh = np.zeros((h, w, c), dtype=np.uint8)
    fresh[:] = rgb_frame
    locations = face_recognition.face_locations(fresh, model="hog")
    print(f"  SUCCESS! Found {len(locations)} face(s)")
except Exception as e:
    print(f"  FAILED: {e}")

print("\nDone.")
input("Press Enter to exit...")
