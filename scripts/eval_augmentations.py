from __future__ import annotations

import cv2
import numpy as np


def blur(img: np.ndarray) -> np.ndarray:
    return cv2.GaussianBlur(img, (15, 15), 0)


def jpeg(img: np.ndarray, quality: int = 40) -> np.ndarray:
    _, encoded = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, quality])
    return cv2.imdecode(encoded, cv2.IMREAD_COLOR)


def perspective(img: np.ndarray, shift: float = 0.08, seed: int = 42) -> np.ndarray:
    h, w = img.shape[:2]
    rng = np.random.default_rng(seed)
    offsets = rng.uniform(-shift, shift, (4, 2)) * np.array([w, h])
    src = np.float32([[0, 0], [w, 0], [w, h], [0, h]])
    dst = np.clip(src + offsets, 0, [w, h]).astype(np.float32)
    M = cv2.getPerspectiveTransform(src, dst)
    return cv2.warpPerspective(img, M, (w, h))


def brightness(img: np.ndarray) -> np.ndarray:
    return cv2.convertScaleAbs(img, alpha=1.4, beta=30)


def combined(img: np.ndarray) -> np.ndarray:
    return perspective(blur(img))


AUGMENTATIONS: dict[str, object] = {
    "blur": blur,
    "jpeg": jpeg,
    "perspective": perspective,
    "brightness": brightness,
    "combined": combined,
}


def hard_perspective(img: np.ndarray) -> np.ndarray:
    return perspective(img, shift=0.22, seed=7)


def crop_zoom(img: np.ndarray, keep: float = 0.65, seed: int = 19) -> np.ndarray:
    h, w = img.shape[:2]
    rng = np.random.default_rng(seed)
    ch, cw = int(h * keep), int(w * keep)
    top = int(rng.integers(0, h - ch + 1))
    left = int(rng.integers(0, w - cw + 1))
    return cv2.resize(img[top:top + ch, left:left + cw], (w, h), interpolation=cv2.INTER_LINEAR)


def motion_blur(img: np.ndarray, size: int = 21) -> np.ndarray:
    kernel = np.zeros((size, size), dtype=np.float32)
    np.fill_diagonal(kernel, 1.0)
    return cv2.filter2D(img, -1, kernel / size)


def low_light(img: np.ndarray, seed: int = 17) -> np.ndarray:
    rng = np.random.default_rng(seed)
    dark = cv2.convertScaleAbs(img, alpha=0.45, beta=-15)
    noise = rng.normal(0.0, 9.0, dark.shape)
    return np.clip(dark.astype(np.float32) + noise, 0, 255).astype(np.uint8)


def glare(img: np.ndarray) -> np.ndarray:
    h, w = img.shape[:2]
    overlay = np.zeros((h, w), dtype=np.uint8)
    cv2.ellipse(overlay, (int(w * 0.42), int(h * 0.3)), (max(8, w // 7), max(8, h // 4)), 25, 0, 360, 255, -1)
    overlay = cv2.GaussianBlur(overlay, (0, 0), sigmaX=w / 18 + 1)
    mask = (overlay.astype(np.float32) / 255.0)[..., None] * 0.75
    return np.clip(img.astype(np.float32) * (1 - mask) + 255.0 * mask, 0, 255).astype(np.uint8)


def shelf(img: np.ndarray, scale: float = 0.55, seed: int = 11) -> np.ndarray:
    h, w = img.shape[:2]
    rng = np.random.default_rng(seed)
    background = cv2.GaussianBlur(rng.integers(60, 190, (h, w, 3), dtype=np.uint8), (31, 31), 0)
    small = cv2.resize(img, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)
    sh, sw = small.shape[:2]
    top, left = (h - sh) // 2, (w - sw) // 2
    background[top:top + sh, left:left + sw] = small
    return background


def hard_combined(img: np.ndarray) -> np.ndarray:
    return low_light(motion_blur(hard_perspective(crop_zoom(img))))


HARD_AUGMENTATIONS: dict[str, object] = {
    "hard_perspective": hard_perspective,
    "crop_zoom": crop_zoom,
    "motion_blur": motion_blur,
    "low_light": low_light,
    "glare": glare,
    "shelf": shelf,
    "hard_combined": hard_combined,
}

PROFILES: dict[str, dict[str, object]] = {
    "easy": AUGMENTATIONS,
    "hard": HARD_AUGMENTATIONS,
    "both": {**AUGMENTATIONS, **HARD_AUGMENTATIONS},
}
