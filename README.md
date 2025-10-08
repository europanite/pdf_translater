# [PDF Translater](https://github.com/europanite/pdf_translater "PDF Translater")

[![CI](https://github.com/europanite/pdf_translater/actions/workflows/ci.yml/badge.svg)](https://github.com/europanite/pdf_translater/actions/workflows/ci.yml)
[![Python Lint](https://github.com/europanite/pdf_translater/actions/workflows/lint.yml/badge.svg)](https://github.com/europanite/pdf_translater/actions/workflows/lint.yml)
[![pages-build-deployment](https://github.com/europanite/pdf_translater/actions/workflows/pages/pages-build-deployment/badge.svg)](https://github.com/europanite/pdf_translater/actions/workflows/pages/pages-build-deployment)
[![CodeQL Advanced](https://github.com/europanite/pdf_translater/actions/workflows/codeql.yml/badge.svg)](https://github.com/europanite/pdf_translater/actions/workflows/codeql.yml)

PDF Translation Utilities.

This repository contains two Python command‑line utilities that convert between **PDF** and **PNG/JPG** while **preserving the original directory structure**.

- `pdf2png_tree.py` — Convert PDFs to PNG/JPG (page-per-image)
- `png2pdf_tree.py` — Convert PNG/JPG images to PDF

Both scripts are filesystem‑friendly (work with a single file or recursively over a directory).

---

## 1) pdf2png_tree.py — PDF → PNG/JPG

Convert PDF pages to images while mirroring the input directory tree under the output root.


```

### Usage
```bash
# Single file
python pdf2png_tree.py /path/to/file.pdf /path/to/outdir

# Directory (recursive)
python pdf2png_tree.py /path/to/input_dir /path/to/outdir
```

### Options
| Option | Default | Description |
|---|---|---|
| `-d`, `--dpi` | `144` | Output resolution (DPI). 200–300 recommended for print-quality |
| `--ext` | `png` | Output image format (`png` or `jpg`) |
| `--overwrite` | off | Overwrite existing files instead of skipping |
| `--per-pdf-subdir` | off | Create a subfolder per PDF (e.g., `<pdf_stem>_png/`) |
| `--suffix` | `_png` | Subfolder suffix when `--per-pdf-subdir` is used |

### Output layout

**Default (no subfolder):**
```
input/
 └─ reports/quarter1/file.pdf

output/
 └─ reports/quarter1/file_p001.png
                          file_p002.png
```

**With `--per-pdf-subdir`:**
```
output/
 └─ reports/quarter1/file_png/
      ├─ file_p001.png
      └─ file_p002.png
```

---

## 2) png2pdf_tree.py — PNG/JPG → PDF

Convert images to PDF while mirroring the input directory tree.  
**Default:** each image becomes one PDF.  
**Option `--merge`:** merge images **per folder** into one multi‑page PDF.

### Usage
```bash
# Per image (default)
python png2pdf_tree.py /path/to/images /path/to/outdir

# Merge images per folder into one PDF
python png2pdf_tree.py /path/to/images /path/to/outdir --merge
```

### Options
| Option | Default | Description |
|---|---|---|
| `--exts` | `png,jpg,jpeg` | Comma‑separated list of image extensions to include |
| `--suffix` | `_converted` | Suffix for output PDF filenames |
| `--overwrite` | off | Overwrite existing PDFs |
| `--merge` | off | Merge images per folder into a single PDF |

### Output layout

**Per image (default):**
```
input/
 ├─ A/img1.png
 └─ B/C/img2.jpg

output/
 ├─ A/img1_converted.pdf
 └─ B/C/img2_converted.pdf
```

**With `--merge`:**
```
input/
 ├─ A/img1.png
 ├─ A/img2.png
 └─ B/C/img3.jpg

output/
 ├─ A/A_converted.pdf      # img1 + img2
 └─ B/C/C_converted.pdf    # img3
```

---

## Tips

- For **large PDFs** or **high DPI**, consider `-d 300` (bigger files, sharper images).
- When converting JPG with `pdf2png_tree.py`, use `--ext jpg` to reduce file size.
- Sort order for `--merge` follows filename order; rename files if you need a specific sequence.

## License
- Apache License 2.0
