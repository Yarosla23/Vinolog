# TASK.md — Grooming Interview Answers

## Original Description

сделай план реализации улучшения понимания фото на основе твоих замечаний и исследования dino3, а так же устойчивость к шумам

## Interview Answers

### Q1 (Goal): What matters more for the competition — accuracy (correct slug in top-1) or speed (latency_ms)?

**Answer:** Both matter — 95% accuracy target is needed, speed is also important but no explicit SLA from organizers.

### Q2 (Hardware): Will the container run on CPU only or is GPU possible?

**Answer:** CPU only now, GPU theoretically possible in the future.

### Q3 (Scope): What is in scope for the plan?

**Answer:** All four areas:
- DINOv3 as first-pass candidate selection (replace FLANN voting stage)
- OCR with decisive role for text/year matching (not just a +0.2 bonus)
- Augmentations at indexing time for noise robustness
- Catalog↔photo mapping cleanup (offline script)

### Q4 (Eval): How to measure improvement?

**Answer:** Both: first build the eval script (Phase 0), then run it as a gate for each subsequent phase. Synthetic recall@1 from reference images + augmentations.

## Key Requirements Extracted

- Build a synthetic eval harness (Recall@1 from augmented reference images) before other changes
- Replace FLANN descriptor-voting shortlist with DINOv3 CLS cosine similarity (CPU, ONNX, ViT-S/16)
- Keep SIFT+RANSAC reranking as-is; DINOv3 only changes how the shortlist is built
- OCR text score must override visual score when year or name tokens match strongly (hard filter, not soft bonus)
- Index-time augmentations: blur, JPEG compression, perspective warp applied to reference images to make SIFT descriptors noise-robust
- Offline catalog→image mapping audit: detect suspicious fuzzy-mapped references using DINOv3 cosine similarity within same winery
- Deploy constraint: CPU-only Docker container, no torch; use onnxruntime + ONNX export of DINOv3 ViT-S/16
- License: DINOv3 license permits commercial use; "Built with DINOv3" attribution required in product or docs
- No pgvector needed: brute-force cosine over ~6000 vectors is faster and exact
- eval/predict endpoint must always return a slug (never 422 on empty shortlist — return best guess)

## Open Questions

- None
