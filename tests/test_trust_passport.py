from datetime import datetime
import unittest

from Woofer.trust_passport import (
    COMPLIANCE_MARKETS,
    TRUST_PASSPORT_CHECKS,
    build_trust_passport,
    calculate_readiness_score,
)


class TrustPassportTests(unittest.TestCase):
    def test_readiness_score_handles_empty_checks(self):
        self.assertEqual(calculate_readiness_score({}), 0)

    def test_readiness_score_rounds_completed_checks(self):
        checks = {
            "identity": True,
            "vet_records": True,
            "microchip": False,
        }

        self.assertEqual(calculate_readiness_score(checks), 67)

    def test_passport_marks_ready_when_at_least_80_percent_complete(self):
        checks = {item["id"]: True for item in TRUST_PASSPORT_CHECKS}
        checks["follow_up"] = False
        pet = {
            "nickname": "Max",
            "breed_detected": "Golden Retriever",
            "ai_confidence": "94.2%",
            "age": 3,
            "weight": 28,
            "profile_id": "ABC123",
        }

        passport = build_trust_passport(
            pet=pet,
            market="Turkey",
            checks=checks,
            operator_notes="Vet records stored by partner clinic.",
            generated_at=datetime(2026, 7, 8, 12, 30),
        )

        self.assertIn("Status: Ready for partner review", passport)
        self.assertIn("Target market: Turkey", passport)
        self.assertIn("- [x] Pet identity confirmed", passport)
        self.assertIn("- [ ] Post-transfer follow-up planned", passport)
        self.assertIn("Vet records stored by partner clinic.", passport)
        self.assertIn(COMPLIANCE_MARKETS["Turkey"]["blocked_until"], passport)

    def test_unknown_market_falls_back_to_azerbaijan_profile(self):
        checks = {"identity": True}
        pet = {"nickname": "Bella"}

        passport = build_trust_passport(
            pet=pet,
            market="Unknown Market",
            checks=checks,
            operator_notes="",
            generated_at=datetime(2026, 7, 8, 12, 30),
        )

        self.assertIn("Target market: Azerbaijan", passport)
        self.assertIn(COMPLIANCE_MARKETS["Azerbaijan"]["position"], passport)
        self.assertIn("No additional notes.", passport)


if __name__ == "__main__":
    unittest.main()
