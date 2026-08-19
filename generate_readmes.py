#!/usr/bin/env python3
"""Generate README.md for each content category folder and each item folder.
Reads manifest.json + _category.json to support any category automatically."""

import base64
import json
import os

SITE_URL = "https://onlygames.me"
ROOT = os.path.dirname(os.path.abspath(__file__))
CONTENT_DIR = os.path.join(ROOT, "content")


def decode_meta(path):
    with open(path, "rb") as f:
        return json.loads(base64.b64decode(f.read()))


def write(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def format_duration(seconds):
    if isinstance(seconds, int):
        return f"{seconds // 60}:{seconds % 60:02d}"
    return str(seconds)


def main():
    manifest_path = os.path.join(ROOT, "manifest.json")
    manifest = json.load(open(manifest_path, encoding="utf-8"))

    for cat_entry in manifest["categories"]:
        cat_id = cat_entry["id"]
        cat_dir = os.path.join(CONTENT_DIR, cat_id)
        cat_meta_path = os.path.join(cat_dir, "_category.json")

        if not os.path.isfile(cat_meta_path):
            print(f"  Skip {cat_id}: no _category.json")
            continue

        cat_meta = json.load(open(cat_meta_path, encoding="utf-8"))
        item_path = cat_meta.get("itemPath", f"/{cat_id}/").strip("/")
        cat_title = cat_meta.get("title", cat_id)
        cat_desc = cat_meta.get("description", "")

        # Load all ready items
        items = []
        for item_id in cat_entry["items"]:
            meta_path = os.path.join(cat_dir, item_id, "meta.dat")
            if not os.path.isfile(meta_path):
                continue
            try:
                meta = decode_meta(meta_path)
            except Exception as e:
                print(f"  Skip {item_id}: {e}")
                continue
            if meta.get("status") == "ready":
                items.append(meta)

        # --- content/{cat_id}/README.md ---
        lines = [
            f"# {cat_title}",
            "",
            cat_desc,
            f"Browse all at [{SITE_URL}/{item_path}/]({SITE_URL}/{item_path}/)",
            "",
            "| Name | Title | Page |",
            "|------|-------|------|",
        ]
        for meta in items:
            name = meta.get("country", meta.get("title", meta["id"]))
            title = meta.get("title", "")
            url = f"{SITE_URL}/{item_path}/{meta['id']}/"
            lines.append(f"| {name} | {title} | [View]({url}) |")

        write(os.path.join(cat_dir, "README.md"), "\n".join(lines) + "\n")
        print(f"Written: content/{cat_id}/README.md ({len(items)} items)")

        # --- content/{cat_id}/{item_id}/README.md ---
        count = 0
        for meta in items:
            name = meta.get("country", meta.get("title", meta["id"]))
            title = meta.get("title", "")
            locale = meta.get("locale", "")
            duration = format_duration(meta.get("duration", ""))
            license_ = meta.get("license", "Public Domain")
            youtube = meta.get("youtube", "")
            url = f"{SITE_URL}/{item_path}/{meta['id']}/"

            # Thumbnail + YouTube preview (if available)
            hero = f"![{name}](thumbnail.jpg)"
            if youtube:
                hero += f"\n\n## Watch\n\n[![Watch on YouTube](https://img.youtube.com/vi/{youtube}/0.jpg)](https://www.youtube.com/watch?v={youtube})"

            # Subtitle line
            subtitle_parts = [f"**{title}**"]
            if locale:
                subtitle_parts.append(f"*{locale}*")
            subtitle = " — ".join(subtitle_parts)

            # Info table
            table_rows = []
            if duration:
                table_rows.append(f"| Duration | {duration} |")
            table_rows.append(f"| License | {license_} |")
            if youtube:
                table_rows.append(f"| YouTube | [Watch](https://www.youtube.com/watch?v={youtube}) |")
            if meta.get("translations"):
                langs = " · ".join(k.upper() for k in meta["translations"].keys())
                table_rows.append(f"| Translations | {langs} |")
            if meta.get("formats"):
                fmts = meta["formats"]
                fmt_labels = []
                for ratio, val in fmts.items():
                    if isinstance(val, dict):
                        fmt_labels.append(f'{ratio} ({val.get("width", "")}×{val.get("height", "")})')
                    else:
                        fmt_labels.append(ratio)
                table_rows.append(f"| Formats | {' · '.join(fmt_labels)} |")

            # CTA text based on category type
            has_audio = bool(meta.get("lyrics") or meta.get("duration"))
            cta = "🎵 Listen & Download" if has_audio else "🔗 View & Download"

            lines = [
                f"# {name}",
                "",
                hero,
                "",
                subtitle,
                "",
                "| | |",
                "|---|---|",
            ] + table_rows + [
                "",
                f"[{cta}]({url})",
                "",
                "> Free to use for YouTube, school projects, video editing, and personal use.",
            ]

            path = os.path.join(cat_dir, meta["id"], "README.md")
            write(path, "\n".join(lines) + "\n")
            count += 1

        print(f"Written: {count} item README.md files in content/{cat_id}/")


if __name__ == "__main__":
    main()
