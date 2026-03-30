import sys
import os
from pathlib import Path

build_lib = Path(r"D:\\TempProj\\nptsne\\build\\lib.win-amd64-cpython-313")

# Check complete tree
for p in build_lib.rglob("*"):
    print(p)

# Set up environment exactly as stubgen will see it
sys.path.insert(0, str(build_lib))

# Try the import chain step by step
try:
    import nptsne
    print("nptsne OK")
except Exception as e:
    print(f"nptsne FAILED: {e}")

try:
    import nptsne.libs
    print("nptsne.libs OK")
except Exception as e:
    print(f"nptsne.libs FAILED: {e}")

try:
    import nptsne.libs._nptsne
    print("nptsne.libs._nptsne OK")
except Exception as e:
    print(f"nptsne.libs._nptsne FAILED: {e}")