#!/usr/bin/env python3
"""
Decode meta.dat → meta.json for local editing.

Usage: python decode.py
"""

import base64
import glob
import os

ROOT = os.path.dirname(os.path.abspath(__file__))

def decode():
    count = 0
    for filepath in glob.glob(os.path.join(ROOT, "content/*/*/meta.dat")):
        json_path = filepath.replace(".dat", ".json")
        with open(filepath, "rb") as f:
            data = base64.b64decode(f.read())
        with open(json_path, "wb") as f:
            f.write(data)
        os.remove(filepath)
        rel = os.path.relpath(json_path, ROOT)
        print(f"  {rel}")
        count += 1
    print(f"\nDecoded {count} files (meta.dat -> meta.json)")

if __name__ == "__main__":
    print("Decoding meta files...\n")
    decode()
