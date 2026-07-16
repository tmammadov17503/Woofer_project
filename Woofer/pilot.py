from collections import Counter
from datetime import datetime
from typing import Any, Dict, Iterable, List, Mapping, Optional

try:
    from Woofer.trust_passport import (
        COMPLIANCE_MARKETS,
        TRUST_PASSPORT_CHECKS,
        calculate_readiness_score,
        get_missing_readiness_checks,
    )
except ImportError:
    from trust_passport import (
        COMPLIANCE_MARKETS,
        TRUST_PASSPORT_CHECKS,
        calculate_readiness_score,
        get_missing_readiness_checks,
    )


PILOT_PARTNER_TYPES = [
    "Shelter or rescue",
    "Vet clinic",
    "Foster coordinator",
    "Adopter family",
    "Startup/conference reviewer",
]

PILOT_STAGES = [
    "Intake",
    "Evidence collection",
    "Partner review",
    "Ready for handoff",
    "Needs follow-up",
]

PILOT_FEEDBACK_SIGNALS = [
    "Not reviewed yet",
    "Useful for pilot",
    "Needs more evidence",
    "Not a fit yet",
]

DEFAULT_REVIEWER = "Pilot reviewer"


def _safe_text(value: Any, fallback: str = "") -> str:
    if value is None:
        return fallback

    text = str(value).strip()
    return text if text else fallback


def _normalize_option(value: Any, allowed_values: List[str], fallback: str) -> str:
    text = _safe_text(value)
    return text if text in allowed_values else fallback


def default_readiness_checks_for_pet(pet: Mapping[str, Any]) -> Dict[str, bool]:
    checks = {item["id"]: False for item in TRUST_PASSPORT_CHECKS}
    checks["identity"] = all(
        pet.get(field) not in (None, "", "N/A")
        for field in ["nickname", "breed_detected", "age", "weight"]
    )
    checks["welfare_terms"] = True
    return checks


def normalize_readiness_checks(
    readiness_checks: Optional[Mapping[str, Any]],
    pet: Optional[Mapping[str, Any]] = None,
) -> Dict[str, bool]:
    defaults = default_readiness_checks_for_pet(pet or {})
    provided = readiness_checks or {}

    return {
        item["id"]: bool(provided[item["id"]]) if item["id"] in provided else defaults[item["id"]]
        for item in TRUST_PASSPORT_CHECKS
    }


def build_pilot_case(
    pet: Mapping[str, Any],
    market: str,
    readiness_checks: Mapping[str, Any],
    partner_type: str,
    stage: str,
    reviewer_name: str = "",
    reviewer_notes: str = "",
    feedback_signal: str = "Not reviewed yet",
    generated_at: Optional[datetime] = None,
) -> Dict[str, Any]:
    generated_at = generated_at or datetime.now()
    normalized_checks = normalize_readiness_checks(readiness_checks, pet)
    score = calculate_readiness_score(normalized_checks)
    missing_evidence = get_missing_readiness_checks(normalized_checks)
    normalized_market = market if market in COMPLIANCE_MARKETS else "Azerbaijan"
    normalized_stage = _normalize_option(stage, PILOT_STAGES, "Intake")
    status, status_bucket = _classify_status(score, normalized_stage)

    return {
        "profile_id": _safe_text(pet.get("profile_id"), "N/A"),
        "nickname": _safe_text(pet.get("nickname"), "Unknown"),
        "breed_detected": _safe_text(pet.get("breed_detected"), "Unknown"),
        "ai_confidence": _safe_text(pet.get("ai_confidence"), "N/A"),
        "market": normalized_market,
        "partner_type": _normalize_option(partner_type, PILOT_PARTNER_TYPES, "Shelter or rescue"),
        "stage": normalized_stage,
        "status": status,
        "status_bucket": status_bucket,
        "readiness_score": score,
        "readiness_checks": normalized_checks,
        "missing_evidence": missing_evidence,
        "next_actions": _build_next_actions(missing_evidence, status_bucket),
        "reviewer_name": _safe_text(reviewer_name, DEFAULT_REVIEWER),
        "reviewer_notes": _safe_text(reviewer_notes, "No reviewer notes yet."),
        "feedback_signal": _normalize_option(
            feedback_signal,
            PILOT_FEEDBACK_SIGNALS,
            "Not reviewed yet",
        ),
        "generated_at": generated_at.isoformat(),
    }


def build_pilot_case_from_pet(
    pet: Mapping[str, Any],
    generated_at: Optional[datetime] = None,
) -> Dict[str, Any]:
    review = pet.get("pilot_review") if isinstance(pet.get("pilot_review"), dict) else {}

    return build_pilot_case(
        pet=pet,
        market=review.get("market", "Azerbaijan"),
        readiness_checks=review.get("readiness_checks", {}),
        partner_type=review.get("partner_type", "Shelter or rescue"),
        stage=review.get("stage", "Intake"),
        reviewer_name=review.get("reviewer_name", ""),
        reviewer_notes=review.get("reviewer_notes", ""),
        feedback_signal=review.get("feedback_signal", "Not reviewed yet"),
        generated_at=generated_at,
    )


def summarize_pilot_cases(cases: Iterable[Mapping[str, Any]]) -> Dict[str, Any]:
    case_list = [dict(case) for case in cases]
    total_cases = len(case_list)
    scores = [int(case.get("readiness_score", 0) or 0) for case in case_list]
    buckets = Counter(case.get("status_bucket", "blocked") for case in case_list)
    gap_counts = _count_missing_evidence(case_list)

    return {
        "total_cases": total_cases,
        "ready_cases": buckets.get("ready", 0),
        "in_progress_cases": buckets.get("in_progress", 0),
        "blocked_cases": buckets.get("blocked", 0),
        "average_readiness_score": round(sum(scores) / total_cases) if total_cases else 0,
        "top_missing_evidence": gap_counts,
    }


def build_pilot_report(
    cases: Iterable[Mapping[str, Any]],
    generated_at: Optional[datetime] = None,
) -> str:
    case_list = [dict(case) for case in cases]
    summary = summarize_pilot_cases(case_list)
    generated_at = generated_at or datetime.now()

    lines = [
        "# Woofer Partner Pilot Report",
        "",
        f"Generated: {generated_at.strftime('%Y-%m-%d %H:%M')}",
        "",
        "## Pipeline Summary",
        f"- Total cases: {summary['total_cases']}",
        f"- Ready cases: {summary['ready_cases']}",
        f"- In progress cases: {summary['in_progress_cases']}",
        f"- Blocked cases: {summary['blocked_cases']}",
        f"- Average readiness score: {summary['average_readiness_score']}%",
        "",
        "## Top Evidence Gaps",
    ]

    if summary["top_missing_evidence"]:
        for gap in summary["top_missing_evidence"][:5]:
            lines.append(f"- {gap['label']}: {gap['count']} case(s)")
    else:
        lines.append("- No missing evidence across this pilot batch.")

    lines.extend(["", "## Case Details"])
    for case in case_list:
        lines.extend(_format_case_report(case))

    lines.extend([
        "",
        "## Operating Guardrail",
        "Woofer is a care, adoption, and readiness tool. It should not be used as an escrow, breeder payment, or live-animal marketplace system without country-specific legal review.",
    ])
    return "\n".join(lines)


def _classify_status(score: int, stage: str) -> tuple[str, str]:
    if stage == "Needs follow-up":
        return "Needs follow-up", "in_progress"
    if score >= 80:
        return "Ready for partner review", "ready"
    if score >= 50:
        return "Evidence collection", "in_progress"
    return "Needs intake work", "blocked"


def _build_next_actions(missing_evidence: List[Mapping[str, Any]], status_bucket: str) -> List[str]:
    if missing_evidence:
        return [
            f"{item['label']}: {item['help']}"
            for item in missing_evidence[:4]
        ]

    if status_bucket == "ready":
        return [
            "Share the Trust Passport with the selected partner reviewer.",
            "Schedule a post-adoption or post-transfer follow-up date.",
        ]

    return [
        "Confirm the partner reviewer and next review date.",
        "Export the Trust Passport after the partner review is complete.",
    ]


def _count_missing_evidence(cases: List[Mapping[str, Any]]) -> List[Dict[str, Any]]:
    counts: Counter[str] = Counter()
    labels_by_id = {item["id"]: item["label"] for item in TRUST_PASSPORT_CHECKS}
    order_by_id = {item["id"]: index for index, item in enumerate(TRUST_PASSPORT_CHECKS)}

    for case in cases:
        for item in case.get("missing_evidence", []):
            if isinstance(item, Mapping) and item.get("id"):
                counts[str(item["id"])] += 1

    return [
        {
            "id": check_id,
            "label": labels_by_id.get(check_id, check_id),
            "count": count,
        }
        for check_id, count in sorted(
            counts.items(),
            key=lambda entry: (-entry[1], order_by_id.get(entry[0], 999)),
        )
    ]


def _format_case_report(case: Mapping[str, Any]) -> List[str]:
    lines = [
        "",
        f"## {case.get('nickname', 'Unknown')} - {case.get('breed_detected', 'Unknown')}",
        f"- Profile ID: {case.get('profile_id', 'N/A')}",
        f"- Partner type: {case.get('partner_type', 'N/A')}",
        f"- Target market: {case.get('market', 'N/A')}",
        f"- Stage: {case.get('stage', 'N/A')}",
        f"- Status: {case.get('status', 'N/A')}",
        f"- Readiness score: {case.get('readiness_score', 0)}%",
        f"- Feedback signal: {case.get('feedback_signal', 'Not reviewed yet')}",
        "",
        "### Next Actions",
    ]

    for action in case.get("next_actions", []):
        lines.append(f"- {action}")

    lines.extend([
        "",
        "### Reviewer Notes",
        str(case.get("reviewer_notes") or "No reviewer notes yet."),
    ])
    return lines
