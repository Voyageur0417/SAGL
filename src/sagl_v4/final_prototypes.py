"""Frozen SAGL core; original source identity is recorded in manifests/source_snapshot.json."""
from __future__ import annotations
import numpy as np
import math

def l2n(v: np.ndarray) -> np.ndarray:
    arr = np.asarray(v, dtype=np.float32)
    norm = float(np.linalg.norm(arr))
    if norm < 1e-12:
        return np.zeros_like(arr, dtype=np.float32)
    return (arr / norm).astype(np.float32)

def prototype_bundle(features: np.ndarray, metas: list[dict]) -> dict[str, np.ndarray | float | int]:
    if len(features) == 0:
        z = np.zeros((1, 512), dtype=np.float32)
        return {"mean": z[0], "sparse": z, "robust": z, "dispersion": 1.0, "n": 0}
    feats = np.asarray(features, dtype=np.float32)
    idxs = sorted({0, len(feats) // 2, len(feats) - 1})
    sparse = feats[idxs]
    mean = l2n(np.mean(feats, axis=0))
    quality = []
    for i, meta in enumerate(metas):
        q = math.log1p(float(meta.get("area", 0.0))) + 0.2 * float(meta.get("score", 1.0))
        quality.append((q, i))
    top = [i for _, i in sorted(quality, reverse=True)[: min(5, len(quality))]]
    robust_raw = [mean, *list(sparse), *[feats[i] for i in top]]
    # Deduplicate near-identical selected rows by index-equivalent vector value.
    robust = []
    seen = set()
    for v in robust_raw:
        key = tuple(np.round(v[:8], 4))
        if key not in seen:
            robust.append(l2n(v))
            seen.add(key)
    if not robust:
        robust = [mean]
    sims = feats @ mean
    dispersion = float(1.0 - np.mean(sims)) if len(sims) else 1.0
    return {
        "mean": mean,
        "sparse": np.asarray([l2n(v) for v in sparse], dtype=np.float32),
        "robust": np.asarray(robust, dtype=np.float32),
        "dispersion": dispersion,
        "n": len(feats),
    }

def proto_similarity(src: dict, dst: dict, representation: str) -> dict:
    if representation == "mean":
        sim = float(np.dot(src["proto"]["mean"], dst["proto"]["mean"]))
        return {"score": sim, "sim_max": sim, "sim_topk_mean": sim, "sim_mean": sim}
    key = "sparse" if representation == "sparse3x3" else "robust"
    a = np.asarray(src["proto"][key], dtype=np.float32)
    b = np.asarray(dst["proto"][key], dtype=np.float32)
    mat = a @ b.T
    flat = np.sort(mat.reshape(-1))[::-1]
    topk = flat[: min(3, len(flat))]
    sim_max = float(flat[0]) if len(flat) else 0.0
    sim_top = float(np.mean(topk)) if len(topk) else 0.0
    sim_mean = float(np.mean(mat)) if mat.size else 0.0
    score = 0.65 * sim_top + 0.35 * sim_max
    if representation == "robust":
        score -= 0.03 * float(src["proto"]["dispersion"] + dst["proto"]["dispersion"])
    return {"score": float(score), "sim_max": sim_max, "sim_topk_mean": sim_top, "sim_mean": sim_mean}
