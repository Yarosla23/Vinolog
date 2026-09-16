#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path

import cv2
import numpy as np
import onnxruntime as ort

_HERE = Path(__file__).resolve().parent
for _root in (_HERE.parent / "services" / "retrieval", _HERE.parent):
    if (_root / "app" / "index.py").exists():
        sys.path.insert(0, str(_root))
        break

from app.catalog import is_original_media, load_catalog
from app.config import load_settings
from app.index import SiftIndex

IMAGENET_MEAN = np.float32([0.485, 0.456, 0.406]).reshape(3, 1, 1)
IMAGENET_STD = np.float32([0.229, 0.224, 0.225]).reshape(3, 1, 1)


def load_session(model_path: str) -> ort.InferenceSession:
    options = ort.SessionOptions()
    options.intra_op_num_threads = os.cpu_count() or 4
    return ort.InferenceSession(model_path, options, providers=["CPUExecutionProvider"])


def preprocess(image: np.ndarray) -> np.ndarray:
    resized = cv2.resize(image, (224, 224), interpolation=cv2.INTER_LINEAR)
    rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
    return (rgb.transpose(2, 0, 1) - IMAGENET_MEAN) / IMAGENET_STD


def embed_paths(
    session: ort.InferenceSession,
    paths: list[Path],
    batch_size: int = 16,
    progress_label: str = "",
) -> tuple[np.ndarray, np.ndarray]:
    embeddings = np.zeros((len(paths), 384), dtype=np.float32)
    usable = np.zeros(len(paths), dtype=bool)
    pending: list[tuple[int, np.ndarray]] = []

    def flush() -> None:
        if not pending:
            return
        batch = np.stack([tensor for _, tensor in pending])
        output = session.run(["pooler_output"], {"pixel_values": batch})[0]
        for (position, _), vector in zip(pending, output):
            embeddings[position] = vector
            usable[position] = True
        pending.clear()

    for position, path in enumerate(paths):
        image = cv2.imread(str(path), cv2.IMREAD_COLOR)
        if image is not None:
            pending.append((position, preprocess(image)))
        if len(pending) >= batch_size:
            flush()
        if progress_label and position and position % 500 == 0:
            print(f"  {progress_label}: embedded {position}/{len(paths)}")
    flush()
    return embeddings, usable


def normalize_rows(embeddings: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    return embeddings / np.maximum(norms, 1e-8)


def flag_suspicious(
    unit_embeddings: np.ndarray,
    usable: np.ndarray,
    wineries: list[str],
    mapping_kinds: list[str],
    threshold: float = 0.85,
) -> list[tuple[int, int, float]]:
    groups: dict[str, list[int]] = defaultdict(list)
    for position, winery in enumerate(wineries):
        if usable[position]:
            groups[winery].append(position)

    flagged: list[tuple[int, int, float]] = []
    for members in groups.values():
        if len(members) < 2:
            continue
        block = unit_embeddings[members]
        cosine = block @ block.T
        np.fill_diagonal(cosine, -1.0)
        for row, position in enumerate(members):
            if mapping_kinds[position] != "fuzzy_filename":
                continue
            best = int(np.argmax(cosine[row]))
            score = float(cosine[row, best])
            if score > threshold:
                flagged.append((position, members[best], score))
    return flagged


def run_audit(
    npz_path: str,
    dataset_root: str,
    model_path: str,
    output_dir: str,
    orphan_threshold: float = 0.90,
) -> Path:
    index = SiftIndex.load(npz_path)
    references = index.references
    uploads = Path(dataset_root) / "uploads"
    session = load_session(model_path)
    print(f"Loaded {len(references)} indexed references.")

    reference_embeddings, reference_usable = embed_paths(
        session,
        [uploads / reference.relative_path for reference in references],
        progress_label="references",
    )
    unit_references = normalize_rows(reference_embeddings)
    print(f"Embedded {int(reference_usable.sum())}/{len(references)} reference images.")

    flagged = flag_suspicious(
        unit_references,
        reference_usable,
        [reference.wine.winery for reference in references],
        [reference.mapping_kind for reference in references],
    )
    suspicious = [
        {
            "slug": references[position].wine.slug,
            "name": references[position].wine.name,
            "winery": references[position].wine.winery,
            "relative_path": references[position].relative_path,
            "mapping_kind": references[position].mapping_kind,
            "mapping_score": round(references[position].mapping_score, 4),
            "nearest_peer_slug": references[peer].wine.slug,
            "nearest_peer_path": references[peer].relative_path,
            "cosine": round(score, 4),
        }
        for position, peer, score in sorted(flagged, key=lambda item: item[2], reverse=True)
    ]

    settings = load_settings()
    _, media = load_catalog(settings.database_url)
    used_paths = {reference.relative_path for reference in references}
    orphan_media = [
        item for item in media
        if is_original_media(item.filename) and item.relative_path not in used_paths
    ]
    print(f"Found {len(orphan_media)} orphaned original media files.")

    orphan_embeddings, orphan_usable = embed_paths(
        session,
        [uploads / item.relative_path for item in orphan_media],
        progress_label="orphans",
    )
    unit_orphans = normalize_rows(orphan_embeddings)

    proposed_fixes = []
    if len(orphan_media) and reference_usable.any():
        valid_reference_positions = np.flatnonzero(reference_usable)
        cosine = unit_orphans @ unit_references[valid_reference_positions].T
        for position, item in enumerate(orphan_media):
            if not orphan_usable[position]:
                continue
            best = int(np.argmax(cosine[position]))
            if float(cosine[position, best]) < orphan_threshold:
                continue
            reference = references[int(valid_reference_positions[best])]
            proposed_fixes.append({
                "relative_path": item.relative_path,
                "filename": item.filename,
                "proposed_slug": reference.wine.slug,
                "proposed_name": reference.wine.name,
                "proposed_winery": reference.wine.winery,
                "cosine": round(float(cosine[position, best]), 4),
            })
        proposed_fixes.sort(key=lambda item: item["cosine"], reverse=True)

    report = {
        "generated_at": datetime.now(UTC).date().isoformat(),
        "index": npz_path,
        "reference_count": len(references),
        "embedded_reference_count": int(reference_usable.sum()),
        "suspicious": suspicious,
        "orphaned": [
            {
                "relative_path": item.relative_path,
                "filename": item.filename,
                "size_bytes": item.size_bytes,
            }
            for item in orphan_media
        ],
        "proposed_fixes": proposed_fixes,
    }

    destination = Path(output_dir) / f"mapping_audit_{report['generated_at']}.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\nSuspicious fuzzy mappings: {len(suspicious)}")
    print(f"Orphaned media: {len(report['orphaned'])}")
    print(f"Proposed fixes: {len(proposed_fixes)}")
    print(f"Report written to {destination}")
    return destination


def self_check() -> None:
    same = np.float32([1.0, 0.0, 0.0])
    near = np.float32([0.99, 0.14, 0.0])
    far = np.float32([0.0, 1.0, 0.0])
    embeddings = normalize_rows(np.stack([same, near, far]))
    usable = np.array([True, True, True])

    flagged = flag_suspicious(
        embeddings, usable,
        ["Табия", "Табия", "Табия"],
        ["fuzzy_filename", "image_filename", "fuzzy_filename"],
    )
    flagged_positions = {position for position, _, _ in flagged}
    assert flagged_positions == {0}, flagged

    other_winery = flag_suspicious(
        embeddings, usable,
        ["Табия", "Фанагория", "Табия"],
        ["fuzzy_filename", "image_filename", "fuzzy_filename"],
    )
    assert not other_winery, other_winery

    skipped = flag_suspicious(
        embeddings, usable,
        ["Табия", "Табия", "Табия"],
        ["image_filename", "image_filename", "image_filename"],
    )
    assert not skipped, skipped

    unusable = flag_suspicious(
        embeddings, np.array([True, False, True]),
        ["Табия", "Табия", "Табия"],
        ["fuzzy_filename", "image_filename", "fuzzy_filename"],
    )
    assert not unusable, unusable

    print("self-check passed")


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit catalog to image mapping with DINOv3 cosine")
    parser.add_argument("--npz", help="Path to .npz index file")
    parser.add_argument("--dataset", help="Path to dataset root (contains uploads/)")
    parser.add_argument("--model", default="/models/dinov3-vits16/model.onnx")
    parser.add_argument("--out", default="reports")
    parser.add_argument("--orphan-threshold", type=float, default=0.90,
                        help="Minimum cosine for an orphan reassignment to be proposed")
    parser.add_argument("--self-check", action="store_true", help="Run flagging assertions and exit")
    args = parser.parse_args()

    if args.self_check:
        self_check()
        return
    if not args.npz or not args.dataset:
        parser.error("--npz and --dataset are required unless --self-check is used")
    run_audit(args.npz, args.dataset, args.model, args.out, args.orphan_threshold)


if __name__ == "__main__":
    main()
