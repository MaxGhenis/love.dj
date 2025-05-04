# dump_codebase.py
"""
Collect (small) codebases into one text file for easy sharing / review.

• Run from the repo root:   python dump_codebase.py
• It will create           ./codebase_snapshot.txt
• The script skips virtual-envs, __pycache__, git metadata, and anything
  over ~200 KB just in case a huge asset sneaked in.
"""

from pathlib import Path
import os

ROOT = Path(__file__).resolve().parent  # repo root
OUTPUT = ROOT / "codebase_snapshot.txt"
MAX_KB = 200  # skip giant blobs
KEEP_EXT = {".py", ".md", ".toml", ".txt"}  # tweak if needed
SKIP_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__"}


def wanted(path: Path) -> bool:
    if any(part in SKIP_DIRS for part in path.parts):
        return False
    if path.is_dir():
        return False
    if path.suffix.lower() not in KEEP_EXT:
        return False
    if path.stat().st_size > MAX_KB * 1024:
        return False
    return True


with OUTPUT.open("w", encoding="utf-8") as fout:
    for file in sorted(ROOT.rglob("*")):
        if not wanted(file):
            continue

        rel = file.relative_to(ROOT)
        fout.write(f"\n\n# ── {rel}\n\n")
        try:
            fout.write(file.read_text(encoding="utf-8", errors="replace"))
        except Exception as exc:
            fout.write(f"(Could not read file: {exc})")

print(
    f"\n✅  Wrote snapshot → {OUTPUT.relative_to(ROOT)}  "
    f"({OUTPUT.stat().st_size/1024:.1f} KB)"
)
