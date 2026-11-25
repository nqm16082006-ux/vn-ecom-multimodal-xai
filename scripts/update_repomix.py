"""Generate or refresh repomix-output.xml for LLM context handoff.

Uses local `repomix` CLI if installed on PATH, otherwise builds a clean
Repomix-compatible XML snapshot directly from `repomix.config.json` and
`.repomixignore` with zero external dependencies.
"""

from __future__ import annotations

import datetime as dt
import fnmatch
import json
import shutil
import subprocess
import sys
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "repomix.config.json"
IGNORE_PATH = ROOT / ".repomixignore"
DEFAULT_OUTPUT = ROOT / "repomix-output.xml"

MAX_FILE_BYTES = 256_000
BINARY_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".webp", ".gif", ".ico", ".bmp",
    ".pt", ".pth", ".bin", ".safetensors", ".onnx", ".pkl",
    ".zip", ".tar", ".gz", ".7z", ".pdf", ".exe", ".dll", ".pyd",
}


def load_ignore_patterns() -> list[str]:
    patterns: list[str] = [".git", ".git/**", "repomix-output.xml"]
    if IGNORE_PATH.exists():
        for raw in IGNORE_PATH.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if line and not line.startswith("#"):
                patterns.append(line.rstrip("/"))
    if CONFIG_PATH.exists():
        cfg = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        for pat in cfg.get("ignore", {}).get("customPatterns", []):
            patterns.append(pat.rstrip("/"))
    return patterns


def is_ignored(rel_posix: str, patterns: list[str]) -> bool:
    parts = rel_posix.split("/")
    for pat in patterns:
        clean = pat.lstrip("/")
        if fnmatch.fnmatch(rel_posix, clean) or fnmatch.fnmatch(parts[-1], clean):
            return True
        if any(fnmatch.fnmatch(part, clean.removesuffix("/**")) for part in parts[:-1]):
            return True
        if clean.endswith("/**") and rel_posix.startswith(clean[:-3] + "/"):
            return True
    return False


def build_tree(paths: list[str]) -> str:
    tree: dict = {}
    for p in paths:
        node = tree
        for part in p.split("/"):
            node = node.setdefault(part, {})

    lines: list[str] = []

    def walk(node: dict, prefix: str = "") -> None:
        items = sorted(node.items(), key=lambda kv: (len(kv[1]) == 0, kv[0]))
        for idx, (name, children) in enumerate(items):
            connector = "└── " if idx == len(items) - 1 else "├── "
            suffix = "/" if children else ""
            lines.append(f"{prefix}{connector}{name}{suffix}")
            if children:
                ext = "    " if idx == len(items) - 1 else "│   "
                walk(children, prefix + ext)

    walk(tree)
    return "\n".join(lines)


def generate_fallback_xml(output_path: Path) -> None:
    cfg = json.loads(CONFIG_PATH.read_text(encoding="utf-8")) if CONFIG_PATH.exists() else {}
    header_text = cfg.get("output", {}).get("headerText", "")
    show_lines = cfg.get("output", {}).get("showLineNumbers", True)
    patterns = load_ignore_patterns()

    included_files: list[Path] = []
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT).as_posix()
        if is_ignored(rel, patterns):
            continue
        if path.suffix.lower() in BINARY_EXTENSIONS:
            continue
        if path.stat().st_size > MAX_FILE_BYTES:
            continue
        included_files.append(path)

    rel_paths = [p.relative_to(ROOT).as_posix() for p in included_files]
    tree_str = build_tree(rel_paths)
    now_iso = dt.datetime.now().astimezone().isoformat(timespec="seconds")

    chunks: list[str] = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        "<repomix>",
        "<file_summary>",
        "This file is a merged representation of the repository context.",
        f"<generated_at>{escape(now_iso)}</generated_at>",
        f"<file_count>{len(included_files)}</file_count>",
        f"<header_text>{escape(header_text)}</header_text>",
        "</file_summary>",
        "<directory_structure>",
        escape(tree_str),
        "</directory_structure>",
        "<files>",
    ]

    for path, rel in zip(included_files, rel_paths):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if show_lines:
            numbered = "\n".join(
                f"{idx:4d} | {line}" for idx, line in enumerate(text.splitlines(), start=1)
            )
        else:
            numbered = text
        chunks.append(f'<file path="{escape(rel)}">')
        chunks.append(escape(numbered))
        chunks.append("</file>")

    chunks.extend(["</files>", "</repomix>"])
    output_path.write_text("\n".join(chunks) + "\n", encoding="utf-8")


def main() -> int:
    repomix_bin = shutil.which("repomix")
    if repomix_bin:
        print(f"Running local repomix CLI: {repomix_bin}")
        res = subprocess.run([repomix_bin], cwd=ROOT)
        return res.returncode

    cfg = json.loads(CONFIG_PATH.read_text(encoding="utf-8")) if CONFIG_PATH.exists() else {}
    out_rel = cfg.get("output", {}).get("filePath", "repomix-output.xml")
    out_path = ROOT / out_rel
    generate_fallback_xml(out_path)
    size_kb = out_path.stat().st_size / 1024
    print(f"Generated {out_path.name} ({size_kb:.1f} KB) using offline fallback.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
