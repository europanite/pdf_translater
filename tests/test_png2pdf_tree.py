import os
import runpy
import sys
from pathlib import Path
import pytest

THIS_DIR = Path(__file__).resolve().parent
REPO_ROOT = os.path.join(THIS_DIR.parent,"src")
CANDIDATES = [
    THIS_DIR / "png2pdf_tree.py",
    REPO_ROOT / "png2pdf_tree.py",
]


def load_main():
    for path in CANDIDATES:
        if path.exists():
            ns = runpy.run_path(str(path))
            main = ns.get("main")
            assert callable(main), "main() not found in png2pdf_tree.py"
            return main
    raise FileNotFoundError(
        "png2pdf_tree.py not found in tests/ or repo root. " "Adjust CANDIDATES in test file."
    )


def run_script(argv: list[str]):
    main = load_main()
    old = sys.argv[:]
    try:
        sys.argv = ["prog"] + argv
        main()
    finally:
        sys.argv = old


def make_img(p: Path, size=(64, 48), color=(200, 100, 50)):
    from PIL import Image

    p.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", size, color).save(p)


def test_basic_single_file_conversion(tmp_path: Path):
    inp = tmp_path / "img.png"
    out_root = tmp_path / "out"
    make_img(inp)

    run_script([str(inp), str(out_root)])
    out_pdf = out_root / (inp.stem + "_converted.pdf")
    assert out_pdf.exists()
    assert out_pdf.stat().st_size > 0


def test_recursive_dir_mirror_structure(tmp_path: Path):
    inp_dir = tmp_path / "in"
    a = inp_dir / "a" / "x.png"
    b = inp_dir / "b" / "y.jpg"
    make_img(a)
    make_img(b)
    out_root = tmp_path / "out"

    run_script([str(inp_dir), str(out_root)])
    assert (out_root / "a" / "x_converted.pdf").exists()
    assert (out_root / "b" / "y_converted.pdf").exists()


def test_merge_option_creates_one_pdf_per_folder(tmp_path: Path):
    inp_dir = tmp_path / "in2"
    img1 = inp_dir / "k" / "1.png"
    img2 = inp_dir / "k" / "2.jpg"
    make_img(img1)
    make_img(img2)
    out_root = tmp_path / "out2"

    run_script([str(inp_dir), str(out_root), "--merge"])
    merged = out_root / "k" / ("k_converted.pdf")
    assert merged.exists()
    assert not (out_root / "k" / "1_converted.pdf").exists()
    assert not (out_root / "k" / "2_converted.pdf").exists()


def test_only_ext_and_overwrite_behavior(tmp_path: Path):
    inp_dir = tmp_path / "in3"
    ok_png = inp_dir / "ok.png"
    skip_bmp = inp_dir / "skip.bmp"
    make_img(ok_png)
    make_img(skip_bmp)
    out_root = tmp_path / "out3"

    run_script([str(inp_dir), str(out_root)])
    out_pdf = out_root / "ok_converted.pdf"
    assert out_pdf.exists()
    first_mtime = out_pdf.stat().st_mtime

    run_script([str(inp_dir), str(out_root)])
    assert out_pdf.stat().st_mtime == pytest.approx(first_mtime)

    run_script([str(inp_dir), str(out_root), "--overwrite"])
    assert out_pdf.stat().st_mtime >= first_mtime

    assert not (out_root / "skip_converted.pdf").exists()

    run_script([str(inp_dir), str(out_root), "--exts", "png,jpg,jpeg,bmp"])
    assert (out_root / "skip_converted.pdf").exists()


def test_missing_input_exits_with_code_1(tmp_path: Path):
    missing = tmp_path / "no_such_dir"
    out_root = tmp_path / "out4"

    with pytest.raises(SystemExit) as ei:
        run_script([str(missing), str(out_root)])
    assert ei.value.code == 1
