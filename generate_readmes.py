#!/usr/bin/env python3
"""Generate README.md for content/national-anthems/ and each country folder."""

import base64
import json
import os

SITE_URL = "https://onlygames.me"
ROOT = os.path.dirname(os.path.abspath(__file__))
ANTHEMS_DIR = os.path.join(ROOT, "content", "national-anthems")


def decode_meta(path):
    with open(path, "rb") as f:
        return json.loads(base64.b64decode(f.read()))


def write(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def main():
    items = []
    for country_id in sorted(os.listdir(ANTHEMS_DIR)):
        meta_path = os.path.join(ANTHEMS_DIR, country_id, "meta.dat")
        if not os.path.isfile(meta_path):
            continue
        try:
            meta = decode_meta(meta_path)
        except Exception as e:
            print(f"  Skip {country_id}: {e}")
            continue
        if meta.get("status") != "ready":
            continue
        items.append(meta)

    # --- content/national-anthems/README.md ---
    lines = [
        "# National Anthems",
        "",
        f"Free MP3 downloads of national anthems from {len(items)} countries, with lyrics and translations in 8 languages.",
        f"All recordings are public domain. Listen and download at [{SITE_URL}/national-anthems/]({SITE_URL}/national-anthems/)",
        "",
        "| Country | Anthem | Page |",
        "|---------|--------|------|",
    ]
    for meta in items:
        country = meta.get("country", meta["id"].upper())
        title = meta.get("title", "")
        url = f"{SITE_URL}/national-anthems/{meta['id']}/"
        lines.append(f"| {country} | {title} | [Listen & Download]({url}) |")

    write(os.path.join(ANTHEMS_DIR, "README.md"), "\n".join(lines) + "\n")
    print(f"Written: content/national-anthems/README.md ({len(items)} entries)")

    # --- content/national-anthems/{id}/README.md ---
    count = 0
    for meta in items:
        country = meta.get("country", meta["id"].upper())
        title = meta.get("title", "")
        locale = meta.get("locale", "")
        duration_raw = meta.get("duration", "")
        if isinstance(duration_raw, int):
            duration = f"{duration_raw // 60}:{duration_raw % 60:02d}"
        else:
            duration = str(duration_raw)
        license_ = meta.get("license", "Public Domain")
        url = f"{SITE_URL}/national-anthems/{meta['id']}/"

        lines = [
            f"# {country} National Anthem",
            "",
            f"**{title}**" + (f" — {locale}" if locale else ""),
            "",
            f"| | |",
            f"|---|---|",
            f"| Duration | {duration} |",
            f"| License | {license_} |",
            f"| Languages | Original · Romanization · EN · TH · JA · ZH · RU · FR · ES · AR |",
            "",
            f"[🎵 Listen & Download Free MP3]({url})",
            "",
            f"> Public domain recording. Free for YouTube, school projects, video editing, and personal use.",
        ]

        path = os.path.join(ANTHEMS_DIR, meta["id"], "README.md")
        write(path, "\n".join(lines) + "\n")
        count += 1

    print(f"Written: {count} country README.md files")


if __name__ == "__main__":
    main()
