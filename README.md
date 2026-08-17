# OnlyGames Media

Open media repository for [OnlyGames](https://onlygames.me) — free games, national anthems, and digital downloads.

## Contents

### National Anthems (`content/national-anthems/`)

- 184 countries
- MP3 recordings (public domain)
- Lyrics in original script + romanization
- Translations in 8 languages: English, Thai, Japanese, Chinese, Russian, French, Spanish, Arabic
- Served at `https://media.onlygames.me`

## Structure

```
content/
  national-anthems/
    th/
      anthem.mp3
      thumbnail.jpg
      og-image.jpg
      meta.dat        ← base64-encoded JSON metadata
    ...
  _example/           ← example item for reference
manifest.json         ← list of all published items
```

## Protocol

See [PROTOCOL.md](PROTOCOL.md) for contribution guidelines.

- Agents write to `draft/` only
- Run `python validate.py --draft` to check
- Only maintainers run `promote.py` to publish

## License

All media files in this repository are public domain unless otherwise noted in the item's `meta.dat`.

---

Published at [onlygames.me](https://onlygames.me)
