#!/usr/bin/env python3
"""
Promote items from draft/ to content/ (production).

Validates each draft item, then:
  - Promotes _category.json if it's a new category
  - Encodes meta.json -> meta.dat
  - Moves item folder to content/
  - Updates manifest.json

Usage:
  python promote.py                  # promote all valid drafts
  python promote.py anthems/france   # promote a specific item
"""

import base64
import json
import os
import shutil
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
DRAFT_DIR = os.path.join(ROOT, "draft")
CONTENT_DIR = os.path.join(ROOT, "content")
MANIFEST_PATH = os.path.join(ROOT, "manifest.json")

ALWAYS_REQUIRED_FILES = ["meta.json", "thumbnail.jpg", "og-image.jpg"]
DEFAULT_REQUIRED_META_FIELDS = ["id", "title", "status"]

def load_manifest():
    with open(MANIFEST_PATH, encoding="utf-8") as f:
        return json.load(f)

def save_manifest(manifest):
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
        f.write("\n")

def load_category_meta(cat_id):
    """Load _category.json — check content/ first, then draft/."""
    for base in [CONTENT_DIR, DRAFT_DIR]:
        path = os.path.join(base, cat_id, "_category.json")
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                return json.load(f)
    return None

def promote_category_if_needed(cat_id):
    """Move _category.json from draft/ to content/ if not yet in production."""
    prod_path = os.path.join(CONTENT_DIR, cat_id, "_category.json")
    draft_path = os.path.join(DRAFT_DIR, cat_id, "_category.json")

    if not os.path.exists(prod_path) and os.path.exists(draft_path):
        os.makedirs(os.path.join(CONTENT_DIR, cat_id), exist_ok=True)
        shutil.move(draft_path, prod_path)
        print(f"  NEW CATEGORY: {cat_id}/_category.json promoted")

        # Add category to manifest if not present
        manifest = load_manifest()
        cat_ids = [c["id"] for c in manifest["categories"]]
        if cat_id not in cat_ids:
            manifest["categories"].append({"id": cat_id, "items": []})
            save_manifest(manifest)

def validate_draft(cat_id, item_id):
    """Validate a single draft item. Returns (ok, errors)."""
    errors = []
    item_dir = os.path.join(DRAFT_DIR, cat_id, item_id)

    if not os.path.isdir(item_dir):
        return False, [f"directory not found: draft/{cat_id}/{item_id}/"]

    cat_meta = load_category_meta(cat_id)
    if cat_meta is None:
        return False, [f"no _category.json found for '{cat_id}' (not in content/ or draft/)"]

    cat_files = cat_meta.get("requiredFiles", [])
    required = list(dict.fromkeys(ALWAYS_REQUIRED_FILES + cat_files))
    required_fields = list(cat_meta.get("metaSchema", {}).keys()) or DEFAULT_REQUIRED_META_FIELDS

    # Check required files
    for fname in required:
        if not os.path.exists(os.path.join(item_dir, fname)):
            errors.append(f"missing file: {fname}")

    # Check meta.json
    meta_path = os.path.join(item_dir, "meta.json")
    if os.path.exists(meta_path):
        try:
            with open(meta_path, encoding="utf-8") as f:
                meta = json.load(f)
            for field in required_fields:
                if field not in meta:
                    errors.append(f"meta.json missing field: {field}")
            if meta.get("id") != item_id:
                errors.append(f"meta.json 'id' is '{meta.get('id')}', expected '{item_id}'")
            if meta.get("status") != "ready":
                errors.append(f"meta.json 'status' is '{meta.get('status')}', expected 'ready'")
        except json.JSONDecodeError as e:
            errors.append(f"meta.json parse error: {e}")

    return len(errors) == 0, errors

def promote_item(cat_id, item_id):
    """Move a validated draft item to production."""
    src = os.path.join(DRAFT_DIR, cat_id, item_id)
    dst = os.path.join(CONTENT_DIR, cat_id, item_id)

    # Encode meta.json -> meta.dat
    meta_json_path = os.path.join(src, "meta.json")
    meta_dat_path = os.path.join(src, "meta.dat")
    with open(meta_json_path, "rb") as f:
        data = f.read()
    with open(meta_dat_path, "wb") as f:
        f.write(base64.b64encode(data))
    os.remove(meta_json_path)

    # Move to production
    if os.path.exists(dst):
        shutil.rmtree(dst)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.move(src, dst)

    # Update manifest.json
    manifest = load_manifest()
    for cat in manifest["categories"]:
        if cat["id"] == cat_id:
            if item_id not in cat["items"]:
                cat["items"].append(item_id)
                cat["items"].sort()
            break
    save_manifest(manifest)

def find_drafts():
    """Find all draft items (folders that are not _category.json)."""
    drafts = []
    if not os.path.isdir(DRAFT_DIR):
        return drafts
    for cat_id in sorted(os.listdir(DRAFT_DIR)):
        cat_dir = os.path.join(DRAFT_DIR, cat_id)
        if not os.path.isdir(cat_dir):
            continue
        for item_id in sorted(os.listdir(cat_dir)):
            item_path = os.path.join(cat_dir, item_id)
            if os.path.isdir(item_path) and not item_id.startswith("_"):
                drafts.append((cat_id, item_id))
    return drafts

def find_draft_categories():
    """Find categories in draft/ that have _category.json."""
    cats = []
    if not os.path.isdir(DRAFT_DIR):
        return cats
    for cat_id in sorted(os.listdir(DRAFT_DIR)):
        cat_dir = os.path.join(DRAFT_DIR, cat_id)
        if os.path.isdir(cat_dir) and os.path.exists(os.path.join(cat_dir, "_category.json")):
            cats.append(cat_id)
    return cats

def cleanup_empty_dirs():
    if os.path.isdir(DRAFT_DIR):
        for d in os.listdir(DRAFT_DIR):
            dd = os.path.join(DRAFT_DIR, d)
            if os.path.isdir(dd) and not os.listdir(dd):
                os.rmdir(dd)
        if os.path.isdir(DRAFT_DIR) and not os.listdir(DRAFT_DIR):
            os.rmdir(DRAFT_DIR)

def build_index_dat():
    """Build index.dat per category — base64-encoded JSON with all items' metadata."""
    manifest = load_manifest()
    for cat in manifest["categories"]:
        cat_id = cat["id"]
        cat_dir = os.path.join(CONTENT_DIR, cat_id)
        index = {}
        for item_id in cat["items"]:
            dat_path = os.path.join(cat_dir, item_id, "meta.dat")
            if not os.path.isfile(dat_path):
                continue
            try:
                with open(dat_path, "rb") as f:
                    meta = json.loads(base64.b64decode(f.read()))
                index[item_id] = meta
            except Exception:
                pass
        # Write as base64-encoded JSON
        raw = json.dumps(index, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        dat_path = os.path.join(cat_dir, "index.dat")
        with open(dat_path, "wb") as f:
            f.write(base64.b64encode(raw))
        print(f"  Built index.dat for {cat_id} ({len(index)} items)")


def main():
    # Specific item or all drafts?
    if len(sys.argv) > 1:
        parts = sys.argv[1].replace("\\", "/").strip("/").split("/")
        if len(parts) != 2:
            print("Usage: python promote.py [category/item-id]")
            sys.exit(1)
        target_cats = [parts[0]]
        drafts = [(parts[0], parts[1])]
    else:
        target_cats = find_draft_categories()
        drafts = find_drafts()

    if not drafts and not target_cats:
        print("No drafts found.")
        return

    # Promote new categories first
    for cat_id in target_cats:
        promote_category_if_needed(cat_id)

    if not drafts:
        print("No item drafts found.")
        cleanup_empty_dirs()
        return

    print(f"Found {len(drafts)} draft(s)\n")

    promoted = 0
    failed = 0

    for cat_id, item_id in drafts:
        label = f"{cat_id}/{item_id}"
        ok, errors = validate_draft(cat_id, item_id)

        if ok:
            promote_item(cat_id, item_id)
            print(f"  OK: {label}")
            promoted += 1
        else:
            print(f"  FAIL: {label}")
            for e in errors:
                print(f"    - {e}")
            failed += 1

    cleanup_empty_dirs()

    print(f"\nPromoted: {promoted}, Failed: {failed}")

    if promoted > 0:
        print()
        build_index_dat()

    sys.exit(1 if failed > 0 else 0)

if __name__ == "__main__":
    main()
