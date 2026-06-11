# ABOUTME: Convert Flow-2 Mermaid topology + card YAML into normalized flow JSON.
# Mirrors Flow-2/flow-loader.js parseMermaid + cards merge (leaves-only for chat).

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml

SRC_DIR = Path(__file__).resolve().parent.parent / "data" / "flows_src"
OUT_DIR = Path(__file__).resolve().parent.parent / "data" / "flows"

_TERMINALS = {"start", "end", "declined"}
_SKIP = re.compile(r"^(flowchart|graph|classDef|linkStyle|class |subgraph|end$|direction)")


def _parse_node(line: str) -> dict[str, Any] | None:
    cls = None
    cm = re.search(r":::(\w+)\s*$", line)
    if cm:
        cls = cm.group(1)
        line = line[: cm.start()].strip()
    m = re.match(r"^(\w+)\s*(\S.*)$", line)
    if not m:
        return None
    node_id, shape = m.group(1), m.group(2).strip()
    if (shape.startswith("([") and shape.endswith("])")) or (
        shape.startswith("[/") and shape.endswith("/]")
    ):
        text = shape[2:-2]
    elif (shape.startswith("{") and shape.endswith("}")) or (
        shape.startswith("[") and shape.endswith("]")
    ):
        text = shape[1:-1]
    else:
        return None
    text = re.sub(r'^"(.*)"$', r"\1", text).replace('\\"', '"')
    if cls in _TERMINALS:
        return {"id": node_id, "title": text, "type": "terminal", "term": cls}
    return {"id": node_id, "title": text, "type": cls or "system", "term": None}


def parse_mermaid(src: str) -> list[dict[str, Any]]:
    nodes: list[dict[str, Any]] = []
    for raw in src.splitlines():
        line = raw.strip()
        if not line or line.startswith("%%") or _SKIP.match(line):
            continue
        if "-->" in line or "--x" in line:  # edge — topology only, skip
            continue
        node = _parse_node(line)
        if node:
            nodes.append(node)
    return nodes


def _norm_docs(raw: Any) -> list[dict[str, Any]]:
    if not isinstance(raw, list):
        return []
    out = []
    for d in raw:
        if isinstance(d, str):
            out.append({"name": d, "format": None, "status": None})
        elif isinstance(d, dict) and (d.get("name") or d.get("title")):
            out.append(
                {
                    "name": d.get("name") or d.get("title"),
                    "format": d.get("format") or d.get("type"),
                    "status": d.get("status"),
                }
            )
    return out


def build_flow(fid: str, mmd: str, yml: dict[str, Any]) -> dict[str, Any]:
    cards = yml.get("cards") or {}
    meta = yml.get("flow") or {}
    nodes = []
    for n in parse_mermaid(mmd):
        c = cards.get(n["id"]) or {}
        nodes.append(
            {
                "id": n["id"],
                "title": n["title"],
                "type": n["type"],
                "term": n["term"],
                "owner": c.get("owner"),
                "team": c.get("team"),
                "sla": c.get("sla"),
                "desc": c.get("desc"),
                "inputs": c.get("inputs") or [],
                "outputs": c.get("outputs") or [],
                "steps": c.get("steps") or [],
                "documents": _norm_docs(c.get("documents")),
            }
        )
    return {"id": meta.get("id") or fid, "name": meta.get("name") or fid, "nodes": nodes}


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    count = 0
    for mmd_path in sorted(SRC_DIR.glob("*.flow.mmd")):
        fid = mmd_path.name[: -len(".flow.mmd")]
        cards_path = SRC_DIR / f"{fid}.cards.yaml"
        yml: dict[str, Any] = yaml.safe_load(cards_path.read_text()) if cards_path.exists() else {}
        flow = build_flow(fid, mmd_path.read_text(), yml or {})
        (OUT_DIR / f"{fid}.json").write_text(json.dumps(flow, indent=2))
        count += 1
        print(f"  {fid}: {len(flow['nodes'])} nodes")
    print(f"Wrote {count} flows to {OUT_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
