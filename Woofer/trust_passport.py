from datetime import datetime


COMPLIANCE_MARKETS = {
    "Azerbaijan": {
        "position": "Adoption-first care passport for pet owners, shelters, vets, and responsible transfers.",
        "notes": [
            "Keep Woofer out of live-animal sale facilitation until local counsel validates the model.",
            "Use vet/shelter verification, owner consent, vaccination records, and care readiness as the trust layer.",
            "Azerbaijan is a natural first market because the product already localizes supplies and care resources.",
        ],
        "blocked_until": "No escrow, marketplace listing, or breeder payment flow before legal and payment-provider review.",
    },
    "Turkey": {
        "position": "Country-aware welfare and transfer-readiness layer, not a pet-sale marketplace.",
        "notes": [
            "Turkey requires extra caution around breeder, pet shop, microchip, ownership, and animal welfare rules.",
            "Any sales/payment flow should be treated as a restricted future lane, not the MVP wedge.",
            "A partner pilot with shelters or clinics is safer than launching consumer-to-consumer sales.",
        ],
        "blocked_until": "Get written legal review for animal transfer, breeder verification, platform liability, and payments.",
    },
    "European Union": {
        "position": "GDPR-aware pet identity, care, and traceability preparation for shelters and clinics.",
        "notes": [
            "EU expansion needs privacy-by-design, user consent, data deletion/export, and country-specific animal rules.",
            "Traceability, microchip, breeder/seller identity, and online listing controls are trending up.",
            "A B2B shelter/clinic workflow is a better first EU wedge than consumer pet transactions.",
        ],
        "blocked_until": "No EU transaction launch before GDPR, animal welfare, and seller-traceability review.",
    },
    "United States": {
        "position": "Care readiness, adoption support, and vet/shelter partner tooling before payments.",
        "notes": [
            "US rules vary heavily by state, city, shelter, rescue, and breeder category.",
            "Avoid claiming medical diagnosis; keep AI health guidance clearly educational.",
            "Treat payments and live-animal transfer as state-by-state legal work.",
        ],
        "blocked_until": "No state-scale marketplace rollout before state licensing, shelter, and payment review.",
    },
}


TRUST_PASSPORT_CHECKS = [
    {
        "id": "identity",
        "label": "Pet identity confirmed",
        "help": "Name, species, breed estimate, age, weight, and photo are present.",
    },
    {
        "id": "vet_records",
        "label": "Vet or vaccination records available",
        "help": "Vaccination, deworming, or recent vet visit records can be shown before transfer/adoption.",
    },
    {
        "id": "microchip",
        "label": "Microchip or local registration checked",
        "help": "Where applicable, confirm chip/registration status and owner transfer requirements.",
    },
    {
        "id": "owner_consent",
        "label": "Current owner / shelter consent documented",
        "help": "The person transferring the animal is authorized to do so.",
    },
    {
        "id": "care_fit",
        "label": "New owner care fit reviewed",
        "help": "Lifestyle, housing, exercise capacity, and expected monthly care costs are understood.",
    },
    {
        "id": "welfare_terms",
        "label": "No unsafe sale or breeding incentive",
        "help": "The flow does not promote puppy mills, impulse buying, or unverified breeders.",
    },
    {
        "id": "follow_up",
        "label": "Post-transfer follow-up planned",
        "help": "A vet visit, reminder, or shelter check-in is scheduled after adoption/transfer.",
    },
]


def calculate_readiness_score(checks):
    if not checks:
        return 0
    completed = sum(1 for value in checks.values() if value)
    return round((completed / len(checks)) * 100)


def build_trust_passport(pet, market, checks, operator_notes, generated_at=None):
    score = calculate_readiness_score(checks)
    market_profile = COMPLIANCE_MARKETS.get(market, COMPLIANCE_MARKETS["Azerbaijan"])
    target_market = market if market in COMPLIANCE_MARKETS else "Azerbaijan"
    status = "Ready for partner review" if score >= 80 else "Needs more evidence before transfer"
    generated_at = generated_at or datetime.now()

    lines = [
        "# Woofer Trust Passport",
        "",
        f"Generated: {generated_at.strftime('%Y-%m-%d %H:%M')}",
        f"Target market: {target_market}",
        f"Status: {status}",
        f"Readiness score: {score}%",
        "",
        "## Pet Profile",
        f"- Name: {pet.get('nickname', 'Unknown')}",
        f"- Breed estimate: {pet.get('breed_detected', 'Unknown')}",
        f"- AI confidence: {pet.get('ai_confidence', 'N/A')}",
        f"- Age: {pet.get('age', 'N/A')} years",
        f"- Weight: {pet.get('weight', 'N/A')} kg",
        f"- Profile ID: {pet.get('profile_id', 'N/A')}",
        "",
        "## Compliance Position",
        market_profile["position"],
        "",
        "## Readiness Checklist",
    ]

    labels_by_id = {item["id"]: item["label"] for item in TRUST_PASSPORT_CHECKS}
    for check_id, value in checks.items():
        mark = "x" if value else " "
        lines.append(f"- [{mark}] {labels_by_id.get(check_id, check_id)}")

    lines.extend(["", "## Market Notes"])
    for note in market_profile["notes"]:
        lines.append(f"- {note}")

    lines.extend([
        "",
        "## Restricted Until",
        market_profile["blocked_until"],
        "",
        "## Operator Notes",
        operator_notes.strip() if operator_notes.strip() else "No additional notes.",
        "",
        "## Medical and Legal Disclaimer",
        "Woofer provides educational care guidance and readiness documentation only. It does not replace a licensed veterinarian or legal counsel.",
    ])
    return "\n".join(lines)
