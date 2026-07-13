import unittest

from Woofer.demo_profile import build_demo_pet_profile


class DemoProfileTests(unittest.TestCase):
    def test_demo_profile_uses_golden_retriever_care_data(self):
        knowledge_base = {
            "golden_retriever": {
                "nutrition": {"diet_type": "Large breed adult formula"},
                "exercise": {"daily_requirement": "2 hours"},
            },
            "general_dog": {"nutrition": {"diet_type": "Balanced dog food"}},
        }

        profile = build_demo_pet_profile(knowledge_base)

        self.assertEqual(profile["nickname"], "Luna")
        self.assertEqual(profile["breed_key"], "golden_retriever")
        self.assertEqual(profile["breed_detected"], "Golden Retriever")
        self.assertTrue(profile["is_demo_profile"])
        self.assertEqual(profile["care_data"]["nutrition"]["diet_type"], "Large breed adult formula")

    def test_demo_profile_copies_care_data(self):
        knowledge_base = {
            "golden_retriever": {
                "nutrition": {"recommended_foods": ["Joint support food"]},
            },
        }

        profile = build_demo_pet_profile(knowledge_base)
        profile["care_data"]["nutrition"]["recommended_foods"].append("Changed")

        self.assertEqual(
            knowledge_base["golden_retriever"]["nutrition"]["recommended_foods"],
            ["Joint support food"],
        )

    def test_demo_profile_falls_back_when_golden_data_is_missing(self):
        knowledge_base = {
            "general_dog": {
                "nutrition": {"diet_type": "Balanced dog food"},
            },
        }

        profile = build_demo_pet_profile(knowledge_base)

        self.assertEqual(profile["breed_key"], "general_dog")
        self.assertEqual(profile["care_data"]["nutrition"]["diet_type"], "Balanced dog food")

    def test_demo_profile_keeps_fallback_key_and_data_consistent(self):
        knowledge_base = {
            "husky": {
                "nutrition": {"diet_type": "High-protein diet"},
            },
        }

        profile = build_demo_pet_profile(knowledge_base)

        self.assertEqual(profile["breed_key"], "husky")
        self.assertEqual(profile["care_data"]["nutrition"]["diet_type"], "High-protein diet")


if __name__ == "__main__":
    unittest.main()
