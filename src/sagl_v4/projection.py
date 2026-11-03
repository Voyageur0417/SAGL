"""Exact ID projection functions copied from frozen SAGL v3 47119f63.
Source SHA256: 51ec657d823c503685466ea9a3b1b3db03c5d61ca79d17330a697b9d0ede19e0
Only these two functions are vendored; no runtime dependency on v3 checkout.
"""
from pathlib import Path
from typing import Iterable
from collections import defaultdict

def links_to_id_map(links: Iterable[dict]) -> dict[str, dict[int, int]]:
    by_seq: dict[str, list[dict]] = defaultdict(list)
    for link in links:
        by_seq[str(link["sequence"])].append(link)
    out: dict[str, dict[int, int]] = {}
    for seq, seq_links in by_seq.items():
        ids = sorted({int(l["src"]) for l in seq_links} | {int(l["dst"]) for l in seq_links})
        parent = {i: i for i in ids}

        def find(x: int) -> int:
            parent.setdefault(x, x)
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        for link in seq_links:
            rs, rd = find(int(link["src"])), find(int(link["dst"]))
            if rs != rd:
                parent[rd] = rs
        out[seq] = {i: find(i) for i in parent}
    return out

def write_id_projection_file(src: Path, dst: Path, mapping: dict[int, int]) -> dict:
    out_lines = []
    changed = 0
    rows = 0
    for ln in src.read_text(encoding="utf-8").splitlines():
        if not ln.strip():
            continue
        rows += 1
        p = ln.split(",")
        old = int(float(p[1]))
        new = int(mapping.get(old, old))
        if new != old:
            changed += 1
            p[1] = str(new)
        out_lines.append(",".join(p))
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text("\n".join(out_lines) + ("\n" if out_lines else ""), encoding="utf-8")
    return {"rows": rows, "changed_id_rows": changed}
