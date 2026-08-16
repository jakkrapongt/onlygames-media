#!/usr/bin/env python3
"""
Encode meta.json → meta.dat (base64) for publishing.
Only encodes item-level meta.json files.
manifest.json and _category.json stay as plain JSON.

Usage: python encode.py
"""

import base64
import glob
import os

ROOT = os.path.dirname(os.path.abspath(__file__))

def encode():
    count = 0
    for filepath in glob.glob(os.path.join(ROOT, "content/*/*/meta.json")):
        dat_path = filepath.replace(".json", ".dat")
        with open(filepath, "rb") as f:
            data = f.read()
        with open(dat_path, "wb") as f:
            f.write(base64.b64encode(data))
        os.remove(filepath)
        rel = os.path.relpath(dat_path, ROOT)
        print(f"  {rel}")
        count += 1
    print(f"\nEncoded {count} files (meta.json -> meta.dat)")

if __name__ == "__main__":
    print("Encoding meta files...\n")
    encode()
