# Woofer Storage Setup

Updated: 2026-07-16

## Decision

Woofer keeps local JSON storage as the default for demos, and now has an optional MongoDB backend for private beta or partner pilot persistence.

The MongoDB database must be isolated for Woofer. Do not connect Woofer to existing trading bot, TikTok automation, makler, analytics, or shared `MONGODB_URI` databases.

## Why This Matters

Pet profiles, health notes, transfer-readiness checks, and future consent records are sensitive product data. Mixing them with unrelated bot infrastructure creates avoidable privacy, security, debugging, and investor diligence risk.

## Local Demo Mode

No setup is required.

```bash
streamlit run Woofer/woofer_care_ai.py
```

The app stores generated pet profiles in `woofer_care_registry.json`, which is ignored by git. Saved Partner Pilot Review notes are stored on the selected pet profile under `pilot_review`.

## MongoDB Private Beta Mode

Set Woofer-specific variables:

```bash
WOOFER_STORAGE_BACKEND=mongodb
WOOFER_MONGODB_URI=<your Woofer-only MongoDB connection string>
WOOFER_MONGO_DB_NAME=woofer_private_beta
WOOFER_MONGO_COLLECTION=pet_profiles
```

For Streamlit Cloud, add the same values as secrets or environment variables. The app intentionally ignores generic `MONGODB_URI` so another project's database is not selected accidentally.

## Recommended Private Beta Collections

- `pet_profiles`: saved pet profile, care data, readiness state, and update timestamps.
- `partner_notes`: future partner review notes and status history.
- `consent_events`: future privacy consent, export, and deletion requests.
- `audit_events`: future admin actions and partner workflow events.

Only `pet_profiles` is implemented today. It now includes optional `pilot_review` metadata for the no-auth pilot workflow: target market, partner type, stage, readiness checks, reviewer notes, feedback signal, and last-reviewed timestamp.

## Next Persistence Work

- Add authenticated partner accounts before multi-organization storage.
- Add consent notice and privacy policy acceptance before collecting real user data.
- Add delete/export functions for GDPR-style readiness.
- Add evidence attachments only after storage rules and access controls are defined.

