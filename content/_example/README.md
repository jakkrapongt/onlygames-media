# Item folder example

Every item folder must contain:

## Required files

| File | Description |
|------|-------------|
| `meta.json` | Item metadata (see meta.json in this folder) |
| `thumbnail.jpg` | 256x256 JPEG, used for card display |
| `og-image.jpg` | 1200x630 JPEG, used for social sharing |

Plus any media files required by the category (see `_category.json` → `requiredFiles`).

## Optional files

You may include additional files beyond the required ones.
List any extra downloadable files in `meta.json` → `files` array.

## meta.json rules

- `id` must match the folder name
- `status` must be `"ready"`
- See the category's `_category.json` → `metaSchema` for category-specific fields
