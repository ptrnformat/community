# Brand asset source

- `letters.py` draws the custom P, T, R and N letters (adapted from Arvo Bold) as outlines.
- `build.py` builds every logo, icon, favicon, avatar and social preview.

## Requirements

- Python 3 with `fonttools`, `skia-pathops` and `Pillow`
- `rsvg-convert` (librsvg) for PNG output
- `Arvo-Regular.ttf` from [Google Fonts](https://fonts.google.com/specimen/Arvo) (secondary text only; the main letters are drawn in code)

## Build

```sh
pip install fonttools skia-pathops Pillow
python3 build.py path/to/Arvo-Regular.ttf path/to/output   # writes path/to/output/brand/...
```

The output folder gets a `brand/` tree matching this one. Edit the social preview text in the `SOCIAL` table in `build.py`.
