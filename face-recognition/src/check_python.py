import sys
import struct

print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")
print(f"Architecture: {struct.calcsize('P') * 8}-bit")
print(f"Version info: {sys.version_info.major}.{sys.version_info.minor}")
