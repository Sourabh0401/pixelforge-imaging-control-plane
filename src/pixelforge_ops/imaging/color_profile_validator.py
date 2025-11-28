from __future__ import annotations

from typing import Sequence


def _profile_name(payload: dict[str, object]) -> str:
    return str(payload.get("profile_name", payload.get("profile", ""))).strip()


def validate_profile(
    payload: dict[str, object],
    required_profile: str | None = None,
    allowed_transfer_functions: Sequence[str] | None = None,
    require_embedded_profile: bool = False,
    allowed_gamuts: Sequence[str] | None = None,
) -> list[str]:
    issues: list[str] = []
    profile_name = _profile_name(payload)
    if required_profile and profile_name != required_profile:
        issues.append(f"profile_name expected {required_profile} but got {profile_name or 'missing'}")
    if require_embedded_profile and not bool(payload.get("embedded_profile", payload.get("embedded", False))):
        issues.append("embedded_profile missing")
    transfer_function = str(payload.get("transfer_function", "")).strip()
    if allowed_transfer_functions and transfer_function not in set(allowed_transfer_functions):
        issues.append(f"transfer_function {transfer_function or 'missing'} is not allowed")
    gamut = str(payload.get("gamut", "")).strip()
    if allowed_gamuts and gamut not in set(allowed_gamuts):
        issues.append(f"gamut {gamut or 'missing'} is not allowed")
    return issues


def profile_summary(
    payload: dict[str, object],
    required_profile: str | None = None,
    allowed_transfer_functions: Sequence[str] | None = None,
    require_embedded_profile: bool = False,
    allowed_gamuts: Sequence[str] | None = None,
) -> dict[str, object]:
    issues = validate_profile(
        payload,
        required_profile=required_profile,
        allowed_transfer_functions=allowed_transfer_functions,
        require_embedded_profile=require_embedded_profile,
        allowed_gamuts=allowed_gamuts,
    )
    status = "block" if issues and any("expected" in issue or "missing" in issue for issue in issues) else "warn" if issues else "ok"
    return {
        "passed": status != "block",
        "status": status,
        "severity": status,
        "profile_name": _profile_name(payload),
        "embedded_profile": bool(payload.get("embedded_profile", payload.get("embedded", False))),
        "transfer_function": payload.get("transfer_function"),
        "gamut": payload.get("gamut"),
        "issues": issues,
    }
