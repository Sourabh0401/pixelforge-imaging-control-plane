from __future__ import annotations

import math
from typing import Sequence

from .pixel_tolerance import Pixel, PixelMatrix


def _luma(pixel: Pixel) -> float:
    if isinstance(pixel, (int, float)):
        return float(pixel)
    channels = [float(channel) for channel in pixel]
    if len(channels) == 1:
        return channels[0]
    red = channels[0]
    green = channels[1] if len(channels) > 1 else channels[0]
    blue = channels[2] if len(channels) > 2 else channels[0]
    return (0.299 * red) + (0.587 * green) + (0.114 * blue)


def _sample(matrix: PixelMatrix, hash_size: int) -> list[float]:
    height = len(matrix)
    width = len(matrix[0]) if height else 0
    if height == 0 or width == 0:
        raise ValueError("pixel matrix cannot be empty")
    samples: list[float] = []
    for y in range(hash_size):
        source_y = min((y * height) // hash_size, height - 1)
        for x in range(hash_size):
            source_x = min((x * width) // hash_size, width - 1)
            samples.append(_luma(matrix[source_y][source_x]))
    return samples


def average_hash(matrix: PixelMatrix, hash_size: int = 8) -> str:
    if hash_size <= 0:
        raise ValueError("hash_size must be positive")
    samples = _sample(matrix, hash_size)
    mean_luma = sum(samples) / len(samples)
    return "".join("1" if value >= mean_luma else "0" for value in samples)


def hamming_distance(left: str, right: str) -> int:
    if len(left) != len(right):
        raise ValueError("hash lengths do not match")
    return sum(1 for a, b in zip(left, right, strict=True) if a != b)


def hash_summary(matrix: PixelMatrix, reference_hash: str, max_distance: int = 0) -> dict[str, int | str | bool]:
    inferred_size = int(math.sqrt(len(reference_hash)))
    if inferred_size * inferred_size != len(reference_hash):
        raise ValueError("reference_hash must have a square bit length")
    actual_hash = average_hash(matrix, inferred_size)
    distance = hamming_distance(actual_hash, reference_hash)
    return {
        "passed": distance <= max_distance,
        "hash": actual_hash,
        "reference_hash": reference_hash,
        "distance": distance,
        "max_distance": max_distance,
    }


def matches_hash(matrix: PixelMatrix, expected_hash: str, max_distance: int = 0) -> bool:
    return bool(hash_summary(matrix, expected_hash, max_distance=max_distance)["passed"])
