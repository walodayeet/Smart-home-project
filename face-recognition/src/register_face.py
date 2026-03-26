#!/usr/bin/env python3
"""
Helper script to register a face using webcam.
Usage: python register_face.py "Your Name"
"""

import sys
import cv2
import requests
import time
from pathlib import Path

API_URL = "http://localhost:5000/register"

def capture_and_register(name: str):
    """Capture face from webcam and register it"""
    
    print(f"\n{'='*50}")
    print(f"Registering Face: {name}")
    print(f"{'='*50}\n")
    
    # Open webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[ERROR] Could not open webcam")
        return False
    
    print("[OK] Webcam opened successfully")
    print("\nInstructions:")
    print("  - Look directly at the camera")
    print("  - Ensure good lighting on your face")
    print("  - Press SPACE to capture")
    print("  - Press ESC to cancel\n")
    
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    captured = False
    image_data = None
    
    while not captured:
        ret, frame = cap.read()
        if not ret:
            print("[ERROR] Failed to read frame")
            break
        
        # Detect faces for visual feedback
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        
        # Draw rectangles around faces
        display_frame = frame.copy()
        for (x, y, w, h) in faces:
            cv2.rectangle(display_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(display_frame, "Face Detected", (x, y-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # Add instructions overlay
        cv2.putText(display_frame, "SPACE = Capture | ESC = Cancel", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        if len(faces) > 0:
            cv2.putText(display_frame, f"Ready to capture for: {name}", (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        else:
            cv2.putText(display_frame, "No face detected", (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        
        cv2.imshow('Register Face - Press SPACE to capture', display_frame)
        
        key = cv2.waitKey(1) & 0xFF
        
        if key == 32:  # SPACE
            if len(faces) == 0:
                print("[WARN] No face detected. Please adjust position and try again.")
                continue
            
            print("[INFO] Capturing image...")
            image_data = frame
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
    
    # Save temporary image
    temp_path = Path("temp_register.jpg")
    cv2.imwrite(str(temp_path), image_data)
    
    print("[UPLOAD] Uploading to API...")
    
    try:
        # Send to API
        with open(temp_path, 'rb') as f:
            files = {'image': ('face.jpg', f, 'image/jpeg')}
            data = {'name': name}
            response = requests.post(API_URL, files=files, data=data, timeout=10)
        
        # Clean up temp file
        temp_path.unlink()
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n[SUCCESS] Registration successful!")
            print(f"   ID: {result.get('id', 'N/A')}")
            print(f"   Name: {result.get('name', name)}")
            print(f"   Message: {result.get('message', 'Face registered')}")
            return True
        else:
            print(f"\n[ERROR] Registration failed: {response.status_code}")
            print(f"   {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("\n[ERROR] Could not connect to API server")
        print("   Make sure the server is running: python api_deepface.py")
        return False
    except Exception as e:
        print(f"\n[ERROR] {e}")
        return False


def main():
    if len(sys.argv) < 2:
        print("Usage: python register_face.py \"Your Name\"")
        print("\nExample:")
        print("  python register_face.py \"Minh\"")
        sys.exit(1)
    
    name = sys.argv[1]
    
    if not name.strip():
        print("[ERROR] Name cannot be empty")
        sys.exit(1)
    
    success = capture_and_register(name)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
