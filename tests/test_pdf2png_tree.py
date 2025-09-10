import runpy
import sys
import time
from pathlib import Path

import pymupdf  # noqa: E402  (after importorskip)
import pytest

THIS_DIR = Path(__file__).resolve().parent
REPO_ROOT = THIS_DIR.parent
CANDIDATES = [
    THIS_DIR / "pdf2png_tree.py",
    REPO_ROOT / "pdf2png_tree.py",
]


def load_main():
    for path in CANDIDATES:
        if path.exists():
            ns = runpy.run_path(str(path))
            main = ns.get("main")
            assert callable(main), "main() not found in pdf2png_tree.py"
            return main
    raise FileNotFoundError(
        "pdf2png_tree.py not found in tests/ or repo root. " "Adjust CANDIDATES in test file."
    )


def run_script(argv: list[str]):
    main = load_main()
    backup = sys.argv[:]
    try:
        sys.argv = ["prog"] + argv
        main()
    finally:
        sys.argv = backup


def make_pdf(path: Path, pages: int = 2, text_prefix: str = "pg"):
    path.parent.mkdir(parents=True, exist_ok=True)
    doc = pymupdf.open()
    for i in range(pages):
        page = doc.new_page()
        page.insert_text((72, 72), f"{text_prefix}-{i+1}", fontsize=24)
    doc.save(path.as_posix())
    doc.close()


def test_single_file_default(tmp_path: Path):
    pdf = tmp_path / "a.pdf"
    out_root = tmp_path / "out"
    make_pdf(pdf, pages=2)

    run_script([str(pdf), str(out_root)])
    p1 = out_root / "a_p001.png"
    p2 = out_root / "a_p002.png"
    assert p1.exists() and p1.stat().st_size > 0
    assert p2.exists() and p2.stat().st_size > 0


def test_recursive_dir_mirror(tmp_path: Path):
    root = tmp_path / "in"
    pdf1 = root / "x" / "a.pdf"
    pdf2 = root / "y" / "b.pdf"
    make_pdf(pdf1, pages=1)
    make_pdf(pdf2, pages=1)
    out_root = tmp_path / "out"

    run_script([str(root), str(out_root)])
    assert (out_root / "x" / "a_p001.png").exists()
    assert (out_root / "y" / "b_p001.png").exists()


def test_per_pdf_subdir_and_suffix(tmp_path: Path):
    root = tmp_path / "in2"
    pdf = root / "k" / "c.pdf"
    make_pdf(pdf, pages=1)
    out_root = tmp_path / "out2"

    run_script([str(root), str(out_root), "--per-pdf-subdir", "--suffix", "_imgs"])
    subdir = out_root / "k" / "c_imgs"
    out_img = subdir / "c_p001.png"
    assert out_img.exists()


def test_ext_jpg(tmp_path: Path):
    pdf = tmp_path / "d.pdf"
    out_root = tmp_path / "out3"
    make_pdf(pdf, pages=1)

    run_script([str(pdf), str(out_root), "--ext", "jpg"])
    out_img = out_root / "d_p001.jpg"
    assert out_img.exists() and out_img.stat().st_size > 0


def test_overwrite_behavior(tmp_path: Path):
    pdf = tmp_path / "e.pdf"
    out_root = tmp_path / "out4"
    make_pdf(pdf, pages=1)

    run_script([str(pdf), str(out_root)])
    out_img = out_root / "e_p001.png"
    assert out_img.exists()
    first_mtime = out_img.stat().st_mtime

    run_script([str(pdf), str(out_root)])
    assert out_img.stat().st_mtime == pytest.approx(first_mtime)

    time.sleep(1.1)

    run_script([str(pdf), str(out_root), "--overwrite"])
    assert out_img.stat().st_mtime >= first_mtime


def test_missing_input_exits_1(tmp_path: Path):
    missing = tmp_path / "no_such_dir"
    out_root = tmp_path / "out5"

    with pytest.raises(SystemExit) as ei:
        run_script([str(missing), str(out_root)])
    assert ei.value.code == 1
