import argparse
import sys
from pathlib import Path

import pymupdf


def is_pdf(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() == ".pdf"


def iter_pdfs(root: Path):
    """Iterate over PDFs: single file or recursively under directory"""
    if root.is_file():
        if is_pdf(root):
            yield root
    else:
        for p in root.rglob("*.pdf"):
            if p.is_file():
                yield p


def rel_parent(pdf_path: Path, input_root: Path) -> Path:
    """
    If input_root is a directory:
        return relative path of PDF's parent to input_root
    If input_root is a file:
        return empty relative path ("."), i.e. save directly under outdir
    """
    if input_root.is_file():
        return Path(".")
    return pdf_path.parent.relative_to(input_root)


def page_png_name(base_stem: str, page_num: int, total: int, ext: str) -> str:
    """Generate page filename with zero padding"""
    width = max(3, len(str(total)))
    return f"{base_stem}_p{page_num:0{width}d}.{ext}"


def convert_pdf(
    pdf_path: Path,
    input_root: Path,
    out_root: Path,
    dpi: int,
    per_pdf_subdir: bool,
    overwrite: bool,
    ext: str,
    suffix: str,
):
    try:
        doc = pymupdf.open(pdf_path)
    except Exception as e:
        print(f"[WARN] Cannot open: {pdf_path} ({e})", file=sys.stderr)
        return

    total = doc.page_count
    if total == 0:
        print(f"[INFO] No pages: {pdf_path}")
        doc.close()
        return

    # Compute output directory strictly from the input tree
    parent_rel = rel_parent(pdf_path, input_root)

    # Default: no extra subfolder -> pages directly under mirrored directory
    out_dir = out_root / parent_rel

    # Optional: per-PDF subfolder (e.g., <pdf_stem>_png)
    if per_pdf_subdir:
        out_dir = out_dir / (pdf_path.stem + suffix)

    out_dir = out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    # DPI -> zoom
    zoom = dpi / 72.0
    mat = pymupdf.Matrix(zoom, zoom)

    saved = 0
    for i in range(total):
        page = doc.load_page(i)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        name = page_png_name(pdf_path.stem, i + 1, total, ext)
        out_file = out_dir / name

        if out_file.exists() and not overwrite:
            # Skip if file already exists
            continue

        if ext.lower() == "png":
            pix.save(out_file.as_posix())
        elif ext.lower() in ("jpg", "jpeg"):
            pix.save(out_file.as_posix(), output="jpg", jpg_quality=95)
        else:
            raise ValueError("Unsupported extension (only png/jpg supported)")

        saved += 1

    doc.close()
    print(f"[OK] {pdf_path} -> {out_dir} ({saved}/{total} pages saved)")


def main():
    parser = argparse.ArgumentParser(
        description="Convert PDFs to PNG/JPG while preserving directory structure"
    )
    parser.add_argument("input_path", type=Path, help="Input PDF file or directory")
    parser.add_argument("output_root", type=Path, help="Output root directory")
    parser.add_argument(
        "-d", "--dpi", type=int, default=144, help="Output resolution (default: 144)"
    )
    parser.add_argument(
        "--ext",
        choices=["png", "jpg"],
        default="png",
        help="Output image format (default: png)",
    )
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing files")
    parser.add_argument("--per-pdf-subdir", action="store_true", help="Create a subfolder per PDF")
    parser.add_argument(
        "--suffix",
        default="_png",
        help="Subfolder suffix when --per-pdf-subdir is used",
    )
    args = parser.parse_args()

    in_path = args.input_path.resolve()
    out_root = args.output_root.resolve()

    if not in_path.exists():
        print(f"[ERROR] Input path not found: {in_path}", file=sys.stderr)
        sys.exit(1)
    out_root.mkdir(parents=True, exist_ok=True)

    pdfs = list(iter_pdfs(in_path))
    if not pdfs:
        print("[INFO] No PDF files found.")
        sys.exit(0)

    # Convert each PDF
    for pdf in pdfs:
        convert_pdf(
            pdf_path=pdf,
            input_root=in_path,
            out_root=out_root,
            dpi=args.dpi,
            per_pdf_subdir=args.per_pdf_subdir,
            overwrite=args.overwrite,
            ext=args.ext,
            suffix=args.suffix,
        )


if __name__ == "__main__":
    main()
