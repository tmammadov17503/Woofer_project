from copy import deepcopy


DEMO_PROFILE_BREED_KEY = "golden_retriever"
DEMO_PROFILE_PAYLOAD = {
    "nickname": "Luna",
    "breed_detected": "Golden Retriever",
    "ai_confidence": "94.2%",
    "age": 4.0,
    "weight": 28.0,
    "health_notes": (
        "Demo profile for judges, shelters, vets, and partners. "
        "Includes sample vaccination evidence, weekly exercise needs, and follow-up planning."
    ),
    "is_demo_profile": True,
    "source": "Built-in conference demo",
}


def build_demo_pet_profile(knowledge_base):
    if DEMO_PROFILE_BREED_KEY in knowledge_base:
        breed_key = DEMO_PROFILE_BREED_KEY
    elif "general_dog" in knowledge_base:
        breed_key = "general_dog"
    else:
        breed_key = next(iter(knowledge_base), "general_dog")

    care_data = deepcopy(knowledge_base.get(breed_key, {}))
    return {
        **DEMO_PROFILE_PAYLOAD,
        "breed_key": breed_key,
        "care_data": care_data,
    }
