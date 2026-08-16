# onlygames-media Protocol

This repo stores media assets for onlygames.me, served via GitHub Pages.

## Rules

1. **Agents write ONLY to `draft/`**
2. **Do NOT touch anything outside `draft/`** — no `content/`, no `manifest.json`, no root files
3. **Do NOT run `promote.py`** — only the maintainer or media agent runs it
4. **Run `python validate.py --draft`** to check your work before finishing

## How to add a new category

Create `draft/{category}/_category.json`:

```json
{
  "id": "category-id",
  "title": "Category Title",
  "emoji": "🎵",
  "color": "#3b82f6",
  "template": "category-id",
  "itemPath": "/category-id/",
  "description": "Short description",
  "requiredFiles": ["meta.json", "thumbnail.jpg", "og-image.jpg", "main-file.mp3"],
  "metaSchema": {
    "field": "description of what this field should contain"
  },
  "metaExample": {
    "field": "example value"
  }
}
```

## How to add items

### Step 1: Read the category schema

Read `draft/{category}/_category.json` (if you just created it) to find:
- `requiredFiles` — list of files you must provide
- `metaSchema` — field descriptions for meta.json
- `metaExample` — a complete example meta.json

### Step 2: Create item folder

```
draft/{category}/{item-id}/
  meta.json          # follow metaSchema
  thumbnail.jpg      # and other files listed in requiredFiles
  ...
```

- `item-id` must be lowercase, alphanumeric, hyphens only
- `meta.json` field `id` must match the folder name
- **Every item MUST have `thumbnail.jpg` (256x256) and `og-image.jpg` (1200x630)** regardless of what `requiredFiles` says
- You may include additional files beyond requiredFiles

### Step 3: Validate

```bash
python validate.py --draft
```

Fix any errors before finishing. Do NOT run promote.py.
