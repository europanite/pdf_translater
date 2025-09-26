import argparse
import sys
from pathlib import Path

from PIL import Image


def is_image(path: Path, exts) -> bool:
    return path.is_file() and path.suffix.lower().lstrip(".") in exts


def iter_images(root: Path, exts):
    """Iterate over images: single file or recursively under directory"""
    if root.is_file():
        if is_image(root, exts):
            yield root
    else:
        for p in root.rglob("*"):
            if is_image(p, exts):
                yield p


def rel_parent(img_path: Path, input_root: Path) -> Path:
    """
    If input_root is a directory:
        return relative path of image's parent to input_root
    If input_root is a file:
        return empty relative path ("."), i.e. save directly under outdir
    """
    if input_root.is_file():
        return Path(".")
    return img_path.parent.relative_to(input_root)


def save_images_as_pdf(images, out_file: Path, overwrite: bool):
    """Save a list of images into one PDF"""
    if not images:
        return False
    if out_file.exists() and not overwrite:
        print(f"[SKIP] {out_file} already exists")
        return False

    pil_images = []
    for img in images:
        try:
            im = Image.open(img).convert("RGB")
            pil_images.append(im)
        except Exception as e:
            print(f"[WARN] Cannot open {img}: {e}", file=sys.stderr)

    if not pil_images:
        return False

    first, rest = pil_images[0], pil_images[1:]
    out_file.parent.mkdir(parents=True, exist_ok=True)
    first.save(out_file, save_all=True, append_images=rest)
    print(f"[OK] Saved {out_file} ({len(pil_images)} pages)")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Convert PNG/JPG images to PDF while preserving directory structure"
    )
    parser.add_argument("input_path", type=Path, help="Input image file or directory")
    parser.add_argument("output_root", type=Path, help="Output root directory")
    parser.add_argument("--exts", default="png,jpg,jpeg", help="Image extensions (comma-separated)")
    parser.add_argument("--suffix", default="_converted", help="Suffix for output PDF filenames")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing PDFs")
    parser.add_argument("--merge", action="store_true", help="Merge images per folder into one PDF")
    args = parser.parse_args()

    in_path = args.input_path.resolve()
    out_root = args.output_root.resolve()
    exts = [e.lower() for e in args.exts.split(",")]

    if not in_path.exists():
        print(f"[ERROR] Input path not found: {in_path}", file=sys.stderr)
        sys.exit(1)

    out_root.mkdir(parents=True, exist_ok=True)

    if args.merge:
        # Folder-wise merge
        parents = {}
        for img in iter_images(in_path, exts):
            rel = rel_parent(img, in_path)
            parents.setdefault(rel, []).append(img)

        for rel, imgs in parents.items():
            imgs.sort()
            out_file = out_root / rel / (rel.name + args.suffix + ".pdf")
            save_images_as_pdf(imgs, out_file, args.overwrite)
    else:
        # Image-wise PDF (default)
        for img in iter_images(in_path, exts):
            rel = rel_parent(img, in_path)
            out_file = out_root / rel / (img.stem + args.suffix + ".pdf")
            save_images_as_pdf([img], out_file, args.overwrite)


if __name__ == "__main__":
    main()
