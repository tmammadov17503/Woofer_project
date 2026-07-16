from datetime import datetime
import unittest

from Woofer.pilot import (
    build_pilot_case,
    build_pilot_report,
    summarize_pilot_cases,
)
from Woofer.trust_passport import TRUST_PASSPORT_CHECKS


def _pet(**overrides):
    pet = {
        "nickname": "Luna",
        "breed_detected": "Golden Retriever",
        "ai_confidence": "94.1%",
        "age": 3,
        "weight": 28,
        "profile_id": "LUNA123",
    }
    return {**pet, **overrides}


class PilotWorkflowTests(unittest.TestCase):
    def test_build_pilot_case_marks_ready_without_mutating_checks(self):
        checks = {item["id"]: True for item in TRUST_PASSPORT_CHECKS}
        checks["follow_up"] = False
        original_checks = dict(checks)

        case = build_pilot_case(
            pet=_pet(),
            market="Turkey",
            readiness_checks=checks,
            partner_type="Shelter or rescue",
            stage="Partner review",
            reviewer_name="Leyla",
            reviewer_notes="  Vet records stored by the partner clinic.  ",
            feedback_signal="Useful for pilot",
            generated_at=datetime(2026, 7, 16, 10, 30),
        )

        self.assertEqual(checks, original_checks)
        self.assertEqual(case["status"], "Ready for partner review")
        self.assertEqual(case["status_bucket"], "ready")
        self.assertEqual(case["readiness_score"], 86)
        self.assertEqual(case["missing_evidence"][0]["id"], "follow_up")
        self.assertIn("Post-transfer follow-up planned", case["next_actions"][0])
        self.assertEqual(case["reviewer_notes"], "Vet records stored by the partner clinic.")

    def test_build_pilot_case_recommends_missing_evidence_in_order(self):
        checks = {
            "identity": True,
            "vet_records": False,
            "microchip": False,
            "owner_consent": False,
            "care_fit": False,
            "welfare_terms": True,
            "follow_up": False,
        }

        case = build_pilot_case(
            pet=_pet(nickname="Max"),
            market="Azerbaijan",
            readiness_checks=checks,
            partner_type="Vet clinic",
            stage="Evidence collection",
            reviewer_notes="",
            generated_at=datetime(2026, 7, 16, 11, 0),
        )

        self.assertEqual(case["status"], "Needs intake work")
        self.assertEqual(case["status_bucket"], "blocked")
        self.assertEqual([item["id"] for item in case["missing_evidence"][:3]], [
            "vet_records",
            "microchip",
            "owner_consent",
        ])
        self.assertIn("Vet or vaccination records available", case["next_actions"][0])

    def test_summarize_pilot_cases_counts_statuses_and_gaps(self):
        ready_checks = {item["id"]: True for item in TRUST_PASSPORT_CHECKS}
        progress_checks = {item["id"]: index < 4 for index, item in enumerate(TRUST_PASSPORT_CHECKS)}
        blocked_checks = {item["id"]: item["id"] == "identity" for item in TRUST_PASSPORT_CHECKS}

        cases = [
            build_pilot_case(_pet(nickname="Ready"), "Turkey", ready_checks, "Shelter or rescue", "Partner review"),
            build_pilot_case(_pet(nickname="Progress"), "Azerbaijan", progress_checks, "Vet clinic", "Evidence collection"),
            build_pilot_case(_pet(nickname="Blocked"), "United States", blocked_checks, "Foster coordinator", "Intake"),
        ]

        summary = summarize_pilot_cases(cases)

        self.assertEqual(summary["total_cases"], 3)
        self.assertEqual(summary["ready_cases"], 1)
        self.assertEqual(summary["in_progress_cases"], 1)
        self.assertEqual(summary["blocked_cases"], 1)
        self.assertEqual(summary["average_readiness_score"], 57)
        self.assertEqual(summary["top_missing_evidence"][0]["id"], "care_fit")

    def test_build_pilot_report_contains_metrics_cases_and_notes(self):
        ready_checks = {item["id"]: True for item in TRUST_PASSPORT_CHECKS}
        blocked_checks = {item["id"]: item["id"] == "identity" for item in TRUST_PASSPORT_CHECKS}
        cases = [
            build_pilot_case(
                _pet(nickname="Luna"),
                "Turkey",
                ready_checks,
                "Shelter or rescue",
                "Partner review",
                reviewer_notes="Advisor says the flow is clear.",
            ),
            build_pilot_case(
                _pet(nickname="Milo", profile_id="MILO321"),
                "Azerbaijan",
                blocked_checks,
                "Vet clinic",
                "Intake",
            ),
        ]

        report = build_pilot_report(cases, generated_at=datetime(2026, 7, 16, 12, 0))

        self.assertIn("# Woofer Partner Pilot Report", report)
        self.assertIn("Generated: 2026-07-16 12:00", report)
        self.assertIn("- Total cases: 2", report)
        self.assertIn("- Ready cases: 1", report)
        self.assertIn("## Luna - Golden Retriever", report)
        self.assertIn("- Partner type: Shelter or rescue", report)
        self.assertIn("Advisor says the flow is clear.", report)
        self.assertIn("## Milo - Golden Retriever", report)
        self.assertIn("- Status: Needs intake work", report)


if __name__ == "__main__":
    unittest.main()
