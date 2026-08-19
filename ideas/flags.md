# Idea: Flag Image Packs

## Keyword Opportunity

- `US flag png free download`
- `[country] flag svg free download`
- `french flag svg free download`
- `usa flag vector free download`
- `[country] flag printable pdf`
- `Thai flag png` / `ธงไทย png`
- `16 9 flags` / `4:3 flags` / `3:2 flags` / `flags of the world same size`

High volume, evergreen, every country × every language × every ratio.

## Pack Contents (per country)

| File | Size | Use case |
|------|------|----------|
| `flag.svg` | vector (4:3) | Scalable, any size |
| `flag-4x3.png` | 1280×960 | Presentations, standard |
| `flag-3x2.png` | 1280×853 | Photography, print |
| `flag-16x9.png` | 1280×720 | YouTube, wallpaper, widescreen |
| `flag-1x1.png` | 1024×1024 | Social media, icons |
| `flag.pdf` | A4 landscape | Printable |
| `thumbnail.jpg` | 256×256 | Card thumbnail |
| `og-image.jpg` | 1200×630 | OG / social share |
| `meta.json` | — | Metadata + i18n country names |

## SVG Sources (flag-crop repo)

Each PNG is rendered from a ratio-specific SVG to preserve flag proportions:

| Ratio | SVG Source | Method |
|-------|-----------|--------|
| 4:3 | flag-icons (lipis) | Human-reviewed source |
| 1:1 | flag-icons (lipis) | Human-reviewed source |
| 3:2 | flag-crop/passed/ | Smart extend/stretch from 4:3 |
| 16:9 | flag-crop/passed/ | Smart extend/stretch from 4:3 |

199 countries × 4 ratios = 796 SVGs, all passed validation.

## Media Repo Structure

```
content/
  flags/
    _category.json
    th/
      flag.svg
      flag-4x3.png
      flag-3x2.png
      flag-16x9.png
      flag-1x1.png
      flag.pdf
      thumbnail.jpg
      og-image.jpg
      meta.dat
    ...
```

## Download Page Design

- 6 separate download buttons (SVG / PNG 4:3 / PNG 3:2 / PNG 16:9 / PNG 1:1 / PDF)
- Each button = 1 click = ad impression
- Single countdown, then all buttons activate
- Show ratio labels clearly: "4:3 Standard" / "16:9 Widescreen" / "1:1 Square" etc.

## AdSense Flow

1. Category page → Flag page (1 pageview)
2. Flag page → Download page (2 pageview)
3. Click format button (ad impression per click, now 6 formats = more impressions)

## Generation

```bash
# Generate all drafts (flags-studio)
node scripts/generate-flags-drafts.js --force

# Validate (onlygames-media)
python validate.py --draft
```

## Notes

- All flags are public domain
- SVG sources: flag-icons (lipis/flag-icons) + flag-crop (ratio-specific)
- Aspect ratios from Wikipedia: https://en.wikipedia.org/wiki/List_of_aspect_ratios_of_national_flags
- 199 countries, all ratios validated and reviewed
