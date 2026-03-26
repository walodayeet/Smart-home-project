#!/usr/bin/env python3
"""
Test face recognition API endpoints without webcam.
Creates a test image, registers it, then tests recognition.
"""

import requests
import cv2
import numpy as np
from pathlib import Path

API_BASE = "http://localhost:5000"

def create_test_image():
    """Create a simple test image with a face-like pattern"""
    img = np.zeros((480, 640, 3), dtype=np.uint8)
    img[:] = (200, 180, 160)
    cv2.circle(img, (320, 240), 80, (220, 200, 180), -1)
    cv2.circle(img, (290, 220), 15, (50, 50, 50), -1)
    cv2.circle(img, (350, 220), 15, (50, 50, 50), -1)
    cv2.ellipse(img, (320, 280), (40, 20), 0, 0, 180, (100, 100, 100), 3)
    
    test_img_path = Path("test_face.jpg")
    cv2.imwrite(str(test_img_path), img)
    return test_img_path

def test_health():
    """Test /health endpoint"""
    print("\n[TEST] Health Check")
    print("-" * 40)
    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def test_register(image_path: Path, name: str):
    """Test /register endpoint"""
    print(f"\n[TEST] Register Face: {name}")
    print("-" * 40)
    try:
        with open(image_path, 'rb') as f:
            files = {'image': ('face.jpg', f, 'image/jpeg')}
            data = {'name': name}
            response = requests.post(f"{API_BASE}/register", files=files, data=data, timeout=10)
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def test_recognize(image_path: Path):
    """Test /recognize endpoint"""
    print(f"\n[TEST] Recognize Face")
    print("-" * 40)
    try:
        with open(image_path, 'rb') as f:
            files = {'image': ('face.jpg', f, 'image/jpeg')}
            response = requests.post(f"{API_BASE}/recognize", files=files, timeout=10)
        
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Response: {result}")
        
        if result.get('ownerRecognized'):
            print(f"[SUCCESS] Recognized as: {result.get('primaryMatch', {}).get('name')}")
        else:
            print(f"[INFO] Not recognized: {result.get('message')}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def test_list_faces():
    """Test /faces endpoint"""
    print(f"\n[TEST] List Registered Faces")
    print("-" * 40)
    try:
        response = requests.get(f"{API_BASE}/faces", timeout=5)
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Total Faces: {result.get('count', 0)}")
        for face in result.get('faces', []):
            print(f"  - {face.get('name')} (ID: {face.get('id')})")
        return response.status_code == 200
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def main():
    print("=" * 50)
    print("Face Recognition API Test Suite")
    print("=" * 50)
    
    test_img = create_test_image()
    print(f"\n[INFO] Created test image: {test_img}")
    
    results = []
    
    results.append(("Health Check", test_health()))
    results.append(("Register Face", test_register(test_img, "TestUser")))
    results.append(("List Faces", test_list_faces()))
    results.append(("Recognize Face", test_recognize(test_img)))
    
    test_img.unlink()
    print(f"\n[INFO] Cleaned up test image")
    
    print("\n" + "=" * 50)
    print("Test Results Summary")
    print("=" * 50)
    for name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status} {name}")
    
    all_passed = all(result for _, result in results)
    print("\n" + ("All tests passed!" if all_passed else "Some tests failed"))
    print("=" * 50)

if __name__ == "__main__":
    main()
