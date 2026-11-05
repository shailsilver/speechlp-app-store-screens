#!/usr/bin/env python3
"""Embed a word-card manifest into the editor template.

Usage: python3 tools/build_manifest_editor.py [manifest.json] [out.html]
"""
import json, pathlib, sys

root = pathlib.Path(__file__).resolve().parent.parent
src = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else sorted((root / "manifest").glob("manifest-v*.json"))[-1]
out = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else root / "manifest-editor.html"
data = json.dumps(json.loads(src.read_text(encoding="utf-8")), ensure_ascii=False, separators=(",", ":"))
data = data.replace("</", "<\\/")
tpl = (root / "tools" / "manifest-editor.template.html").read_text(encoding="utf-8")
out.write_text(tpl.replace("__MANIFEST__", data), encoding="utf-8")
print(f"Wrote {out} from {src.name} ({out.stat().st_size // 1024} KB)")
