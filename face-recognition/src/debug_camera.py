"""Debug script to check webcam frame format."""
import cv2
import numpy as np

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("ERROR: Could not open camera")
    exit(1)

print("Camera opened successfully")
print("Reading frames...\n")

for i in range(5):
    ret, frame = cap.read()
    if not ret or frame is None:
        print(f"Frame {i}: Failed to read")
        continue
    
    print(f"Frame {i}:")
    print(f"  Type: {type(frame)}")
    print(f"  dtype: {frame.dtype}")
    print(f"  shape: {frame.shape}")
    print(f"  ndim: {frame.ndim}")
    print(f"  is contiguous: {frame.flags['C_CONTIGUOUS']}")
    print(f"  min/max values: {frame.min()} / {frame.max()}")
    
    # Test conversion
    try:
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb = np.ascontiguousarray(rgb, dtype=np.uint8)
        print(f"  RGB dtype: {rgb.dtype}, shape: {rgb.shape}, contiguous: {rgb.flags['C_CONTIGUOUS']}")
    except Exception as e:
        print(f"  RGB conversion error: {e}")
    print()

cap.release()
print("Done. Press Enter to exit...")
input()
