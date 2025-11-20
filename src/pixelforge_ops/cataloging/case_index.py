from __future__ import annotations

from collections import defaultdict

from pixelforge_ops.models import ExerciseBundle


def by_section(bundle: ExerciseBundle) -> dict[str, list[str]]:
    output: dict[str, list[str]] = defaultdict(list)
    for case in bundle.cases:
        output[case.section].append(case.case_id)
    return {section: sorted(case_ids) for section, case_ids in sorted(output.items())}


def by_difficulty(bundle: ExerciseBundle) -> dict[str, list[str]]:
    output: dict[str, list[str]] = defaultdict(list)
    for case in bundle.cases:
        output[case.difficulty].append(case.case_id)
    return {difficulty: sorted(case_ids) for difficulty, case_ids in sorted(output.items())}


def hidden_case_ids(bundle: ExerciseBundle) -> tuple[str, ...]:
    return tuple(sorted(case.case_id for case in bundle.cases if case.hidden))


def searchable_rows(bundle: ExerciseBundle) -> list[dict[str, object]]:
    return [
        {
            "case_id": case.case_id,
            "section": case.section,
            "difficulty": case.difficulty,
            "hidden": case.hidden,
            "tags": list(case.tags),
        }
        for case in bundle.cases
    ]


def tag_counts(bundle: ExerciseBundle) -> dict[str, int]:
    counts: dict[str, int] = {}
    for case in bundle.cases:
        for tag in case.tags:
            counts[tag] = counts.get(tag, 0) + 1
    return dict(sorted(counts.items()))


def filter_cases(bundle: ExerciseBundle, *, section: str | None = None, hidden: bool | None = None) -> list[str]:
    output = []
    for case in bundle.cases:
        if section is not None and case.section != section:
            continue
        if hidden is not None and case.hidden != hidden:
            continue
        output.append(case.case_id)
    return output


