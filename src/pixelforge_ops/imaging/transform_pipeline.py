from __future__ import annotations

from typing import Mapping, Sequence


def _aspect_ratio(width: int, height: int) -> float:
    return round(width / max(height, 1), 6)


def validate_transform_chain(stages: Sequence[Mapping[str, object]], max_scale_up: float = 4.0) -> list[str]:
    issues: list[str] = []
    previous_width: int | None = None
    previous_height: int | None = None
    encode_seen = False
    seen_operations: list[str] = []
    for index, stage in enumerate(stages):
        operation = str(stage.get("operation", "transform"))
        width = int(stage.get("width", 0))
        height = int(stage.get("height", 0))
        if width <= 0 or height <= 0:
            issues.append(f"stage {index} has non-positive dimensions")
            continue
        if operation == "decode" and index != 0:
            issues.append(f"stage {index} decode appears after pipeline start")
        if encode_seen:
            issues.append(f"stage {index} appears after encode")
        if operation == "encode":
            encode_seen = True
        if operation in {"crop", "resize"} and seen_operations and seen_operations[-1] == operation:
            issues.append(f"stage {index} repeats {operation} without an intervening normalize step")
        if operation == "alpha-premultiply" and "flatten" in seen_operations:
            issues.append(f"stage {index} premultiplies alpha after flatten")
        if previous_width is not None and previous_height is not None:
            scale_x = width / previous_width
            scale_y = height / previous_height
            if scale_x > max_scale_up or scale_y > max_scale_up:
                issues.append(f"stage {index} scales beyond {max_scale_up}x")
            if operation == "crop" and (width > previous_width or height > previous_height):
                issues.append(f"stage {index} crop enlarged the image")
            if operation == "flatten" and (width != previous_width or height != previous_height):
                issues.append(f"stage {index} flatten changed dimensions")
        previous_width = width
        previous_height = height
        seen_operations.append(operation)
    return issues


def pipeline_summary(stages: Sequence[Mapping[str, object]]) -> dict[str, object]:
    if not stages:
        return {"step_count": 0, "operations": [], "issues": ["pipeline is empty"]}
    first = stages[0]
    last = stages[-1]
    issues = validate_transform_chain(stages)
    return {
        "step_count": len(stages),
        "operations": [str(stage.get("operation", "transform")) for stage in stages],
        "input_size": [int(first.get("width", 0)), int(first.get("height", 0))],
        "output_size": [int(last.get("width", 0)), int(last.get("height", 0))],
        "aspect_ratio_delta": round(
            abs(
                _aspect_ratio(int(first.get("width", 0)), int(first.get("height", 0)))
                - _aspect_ratio(int(last.get("width", 0)), int(last.get("height", 0)))
            ),
            6,
        ),
        "issues": issues,
        "passed": not issues,
    }
