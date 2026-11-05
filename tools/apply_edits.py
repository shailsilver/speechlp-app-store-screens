#!/usr/bin/env python3
"""Apply edits saved by the manifest editor to a manifest file.

The editor stores one document per changed word in its `edits` collection:
  {"data": <word object>, "deleted": bool, "isNew": bool, "updatedAt": str}
Export them as JSON files (one per word, file name = word id) into a folder, then:

  python3 tools/apply_edits.py manifest/manifest-v1793049610.json path/to/edits [--bump]
"""
import json, pathlib, sys, time

src, edits_dir = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
bump = "--bump" in sys.argv
m = json.loads(src.read_text(encoding="utf-8"))
edits = {}
for f in sorted(edits_dir.rglob("*.json")):
    doc = json.loads(f.read_text(encoding="utf-8"))
    doc = doc.get("data", doc) if "deleted" not in doc and isinstance(doc.get("data"), dict) and "data" in doc["data"] else doc
    edits[f.stem] = doc

words, seen, changed, removed, added = [], set(), 0, 0, 0
for w in m["words"]:
    e = edits.get(w["id"])
    seen.add(w["id"])
    if e is None:
        words.append(w)
    elif e.get("deleted"):
        removed += 1
    else:
        words.append(e["data"]); changed += 1
for wid, e in edits.items():
    if wid not in seen and not e.get("deleted") and e.get("data"):
        words.append(e["data"]); added += 1

m["words"] = words
if bump:
    m["version"] = int(time.time())
out = src.with_name(f"manifest-v{m['version']}.json")
out.write_text(json.dumps(m, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"{changed} edited, {added} added, {removed} removed -> {out}")
