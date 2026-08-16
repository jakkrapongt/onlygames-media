#!/usr/bin/env python3
"""
Validate media repo structure.

Usage:
  python validate.py           # validate production (content/)
  python validate.py --draft   # validate draft/ items
"""

import base64
import json
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
CONTENT_DIR = os.path.join(ROOT, "content")
DRAFT_DIR = os.path.join(ROOT, "draft")

ALWAYS_REQUIRED_FILES = ["meta.json", "thumbnail.jpg", "og-image.jpg"]
DEFAULT_REQUIRED_META_FIELDS = ["id", "title", "status"]

def load_meta_dat(path):
    with open(path, "rb") as f:
        return json.loads(base64.b64decode(f.read()))

def load_meta_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def validate_production():
    """Validate content/ against manifest.json."""
    errors = []
    warnings = []

    manifest_path = os.path.join(ROOT, "manifest.json")
    if not os.path.exists(manifest_path):
        print("FAIL: manifest.json not found")
        return False

    manifest = json.load(open(manifest_path, encoding="utf-8"))

    if "baseUrl" not in manifest:
        errors.append("manifest.json missing 'baseUrl'")
    if "categories" not in manifest:
        print("FAIL: manifest.json missing 'categories'")
        return False

    for cat in manifest["categories"]:
        cat_id = cat["id"]
        cat_dir = os.path.join(CONTENT_DIR, cat_id)

        cat_meta_path = os.path.join(cat_dir, "_category.json")
        if not os.path.exists(cat_meta_path):
            errors.append(f"{cat_id}/_category.json not found")
            continue

        cat_meta = json.load(open(cat_meta_path, encoding="utf-8"))
        cat_files = cat_meta.get("requiredFiles", [])
        merged = list(dict.fromkeys(ALWAYS_REQUIRED_FILES + cat_files))
        required = [("meta.dat" if f == "meta.json" else f) for f in merged]
        required_fields = list(cat_meta.get("metaSchema", {}).keys()) or DEFAULT_REQUIRED_META_FIELDS

        for item_id in cat.get("items", []):
            item_dir = os.path.join(cat_dir, item_id)
            prefix = f"{cat_id}/{item_id}"

            if not os.path.isdir(item_dir):
                errors.append(f"{prefix}/ directory not found")
                continue

            for fname in required:
                if not os.path.exists(os.path.join(item_dir, fname)):
                    errors.append(f"{prefix}/{fname} missing")

            dat_path = os.path.join(item_dir, "meta.dat")
            if os.path.exists(dat_path):
                try:
                    meta = load_meta_dat(dat_path)
                    for field in required_fields:
                        if field not in meta:
                            errors.append(f"{prefix}/meta.dat missing field '{field}'")
                    if meta.get("id") != item_id:
                        errors.append(f"{prefix}/meta.dat 'id' is '{meta.get('id')}', expected '{item_id}'")
                except Exception as e:
                    errors.append(f"{prefix}/meta.dat decode error: {e}")

        if os.path.isdir(cat_dir):
            for d in os.listdir(cat_dir):
                if os.path.isdir(os.path.join(cat_dir, d)) and d not in cat.get("items", []):
                    warnings.append(f"{cat_id}/{d}/ exists but not listed in manifest.json")

    total = sum(len(c.get("items", [])) for c in manifest["categories"])
    return report("production", total, errors, warnings)

def validate_draft():
    """Validate draft/ items against their _category.json."""
    errors = []
    warnings = []
    total = 0

    if not os.path.isdir(DRAFT_DIR):
        print("No draft/ folder found.")
        return True

    for cat_id in sorted(os.listdir(DRAFT_DIR)):
        cat_dir = os.path.join(DRAFT_DIR, cat_id)
        if not os.path.isdir(cat_dir):
            continue

        # Load _category.json from draft/ or content/
        cat_meta = None
        for base in [DRAFT_DIR, CONTENT_DIR]:
            cat_meta_path = os.path.join(base, cat_id, "_category.json")
            if os.path.exists(cat_meta_path):
                cat_meta = json.load(open(cat_meta_path, encoding="utf-8"))
                break

        if cat_meta is None:
            errors.append(f"{cat_id}/_category.json not found (not in draft/ or content/)")
            continue

        cat_files = cat_meta.get("requiredFiles", [])
        required = list(dict.fromkeys(ALWAYS_REQUIRED_FILES + cat_files))
        required_fields = list(cat_meta.get("metaSchema", {}).keys()) or DEFAULT_REQUIRED_META_FIELDS

        for item_id in sorted(os.listdir(cat_dir)):
            item_dir = os.path.join(cat_dir, item_id)
            if not os.path.isdir(item_dir) or item_id.startswith("_"):
                continue

            total += 1
            prefix = f"{cat_id}/{item_id}"

            for fname in required:
                if not os.path.exists(os.path.join(item_dir, fname)):
                    errors.append(f"{prefix}/{fname} missing")

            meta_path = os.path.join(item_dir, "meta.json")
            if os.path.exists(meta_path):
                try:
                    meta = load_meta_json(meta_path)
                    for field in required_fields:
                        if field not in meta:
                            errors.append(f"{prefix}/meta.json missing field '{field}'")
                    if meta.get("id") != item_id:
                        errors.append(f"{prefix}/meta.json 'id' is '{meta.get('id')}', expected '{item_id}'")
                    if meta.get("status") != "ready":
                        warnings.append(f"{prefix}/meta.json status is '{meta.get('status')}', not 'ready'")
                except json.JSONDecodeError as e:
                    errors.append(f"{prefix}/meta.json parse error: {e}")

    return report("draft", total, errors, warnings)

def report(mode, total, errors, warnings):
    print(f"Validated {total} {mode} items\n")

    if warnings:
        print(f"Warnings ({len(warnings)}):")
        for w in warnings:
            print(f"  WARN: {w}")
        print()

    if errors:
        print(f"Errors ({len(errors)}):")
        for e in errors:
            print(f"  FAIL: {e}")
        print("\nFAIL")
        return False
    else:
        print("ALL OK")
        return True

if __name__ == "__main__":
    if "--draft" in sys.argv:
        ok = validate_draft()
    else:
        ok = validate_production()
    sys.exit(0 if ok else 1)
