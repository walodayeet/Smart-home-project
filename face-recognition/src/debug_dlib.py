"""Debug script to test dlib directly."""
import numpy as np

print("Testing dlib installation...\n")

# Test 1: Import dlib
print("1. Importing dlib...")
try:
    import dlib
    print(f"   SUCCESS: dlib version = {dlib.__version__}")
except Exception as e:
    print(f"   FAILED: {e}")
    exit(1)

# Test 2: Check dlib face detector
print("\n2. Loading dlib face detector...")
try:
    detector = dlib.get_frontal_face_detector()
    print("   SUCCESS: Face detector loaded")
except Exception as e:
    print(f"   FAILED: {e}")
    exit(1)

# Test 3: Test with a simple synthetic image
print("\n3. Testing detector with synthetic gray image...")
try:
    gray_img = np.zeros((100, 100), dtype=np.uint8)
    gray_img[30:70, 30:70] = 128  # gray square
    faces = detector(gray_img, 1)
    print(f"   SUCCESS: Detector ran (found {len(faces)} faces, expected 0)")
except Exception as e:
    print(f"   FAILED: {e}")

# Test 4: Test with RGB image
print("\n4. Testing detector with synthetic RGB image...")
try:
    rgb_img = np.zeros((100, 100, 3), dtype=np.uint8)
    rgb_img[30:70, 30:70, :] = 128
    faces = detector(rgb_img, 1)
    print(f"   SUCCESS: Detector ran (found {len(faces)} faces, expected 0)")
except Exception as e:
    print(f"   FAILED: {e}")

# Test 5: Test with actual webcam frame
print("\n5. Testing detector with webcam frame...")
try:
    import cv2
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cap.release()
    
    if ret and frame is not None:
        # Convert BGR to RGB
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        print(f"   Frame: dtype={rgb.dtype}, shape={rgb.shape}")
        
        # Try dlib directly
        faces = detector(rgb, 1)
        print(f"   SUCCESS: Detector ran (found {len(faces)} faces)")
    else:
        print("   SKIPPED: Could not read webcam frame")
except Exception as e:
    print(f"   FAILED: {e}")

# Test 6: Check face_recognition_models
print("\n6. Checking face_recognition_models...")
try:
    import face_recognition_models
    predictor_path = face_recognition_models.pose_predictor_model_location()
    face_rec_path = face_recognition_models.face_recognition_model_location()
    print(f"   Predictor model: {predictor_path}")
    print(f"   Face rec model: {face_rec_path}")
    
    import os
    print(f"   Predictor exists: {os.path.exists(predictor_path)}")
    print(f"   Face rec exists: {os.path.exists(face_rec_path)}")
except Exception as e:
    print(f"   FAILED: {e}")

print("\nDone.")
input("Press Enter to exit...")
