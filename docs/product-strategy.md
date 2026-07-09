# Woofer Product Strategy

Updated: 2026-07-08

## Executive Decision

The strongest next move is to position Woofer as a responsible pet-care and trust-readiness platform, not as a live-animal sales marketplace. The first defensible wedge is the Woofer Trust Passport: AI breed/care analysis plus a country-aware adoption or transfer readiness checklist for shelters, vets, foster groups, and responsible owners.

This keeps the product close to the existing MVP while directly answering the biggest concern from startup reviewers: country-by-country animal welfare, ownership, breeder, and payment regulations.

## Current Product Reality

Woofer currently works as a Streamlit MVP with:

- AI dog breed analysis using MobileNetV2.
- Breed-specific care guidance from a local JSON knowledge base.
- PDF care guide generation.
- Health tracking and vet reminder basics.
- Azerbaijan-focused supply links.
- Adoption-first positioning and no live animal sales.
- Optional isolated MongoDB persistence path for private beta storage.
- Focused unit tests and GitHub Actions checks for the product trust layer.

Main gaps before serious launch:

- No user accounts, auth, or durable multi-user database.
- No privacy policy flow, consent handling, deletion/export, or analytics.
- No monitoring or error reporting.
- Limited breed knowledge base.
- No verified partner workflow for shelters, clinics, or transfers.
- No legal-reviewed compliance workflow beyond the current country-aware product narrative.

## Dosty Analysis

Dosty is a direct adjacent competitor in broad pet-care software, not in Woofer's best wedge. Public positioning on dosty.co emphasizes all-in-one pet care, health records, behavior, routines, AI guidance, and community. Their B2B page targets vet clinics with bookings, patient/client CRM, structured SOAP notes, treatments, inventory, and business insights.

Implication: do not compete head-on as "another AI pet-care app." Dosty is already deeper on mobile, community, AI assistant, and B2B clinic operations.

Better differentiation:

- Woofer: responsible adoption and transfer readiness, localized first for Azerbaijan/Turkey-region trust gaps.
- Dosty: ongoing pet-parent care OS and clinic management.
- Partnership angle: Woofer can send verified, better-prepared adopters/pet owners into Dosty-style long-term care or clinic workflows.

## Response To The Turkish Feedback

The Turkish feedback is directionally correct: animal sales, breeding, ownership transfer, and welfare rules differ by country. A startup that touches live-animal sales must explain regulation, operations, and compliance in detail.

Recommended answer:

- Woofer will not start with animal sales or escrow.
- Woofer starts with education, pet identity, care readiness, welfare documentation, and partner verification.
- Marketplace listing, breeder verification, and payment/escrow are restricted future lanes.
- Each country gets a compliance profile before launch.
- Payments for live-animal transfer require legal review and a licensed payment partner.

## Capability Contract: Trust Passport

### Actors

- Pet owner or adopter.
- Shelter, rescue, or foster coordinator.
- Vet clinic or care partner.
- Woofer operator/admin.

### User Promise

Woofer helps generate a clear, shareable readiness record before adoption, fostering, vet referral, or responsible transfer.

### Non-Goals

- No live-animal marketplace in this phase.
- No escrow or payment custody in this phase.
- No legal certification.
- No veterinary diagnosis.
- No breeder promotion.

### Required Fields

- Pet profile: name, breed estimate, age, weight, AI confidence, health notes.
- Market/country profile: Azerbaijan, Turkey, EU, United States.
- Readiness checks: identity, vet records, microchip/registration, owner consent, care fit, welfare terms, follow-up.
- Operator notes.
- Downloadable Trust Passport output.

### Invariants

- Every Trust Passport must include medical and legal disclaimers.
- Any transfer/payment language must be framed as restricted until legal review.
- The user must see missing readiness evidence before a pet is considered partner-ready.
- The product should reward welfare readiness, not transaction volume.

## 30-Day Execution Plan

### Week 1

- Ship the Trust Passport MVP inside Streamlit.
- Update README and website messaging to explain the new wedge.
- Create a 1-page partner deck for shelters/vets.
- Interview 5 local vets/shelters/rescuers about transfer-readiness pain.

### Week 2

- Replace JSON storage with Supabase/Postgres or SQLite-backed persistence for private beta.
- Add basic auth and consent notice.
- Add PostHog or simple event logging for activation and repeat use.
- Expand the knowledge base to the top 20 local breeds/mixed-breed scenarios.

### Week 3

- Run a small partner pilot: 10 Trust Passports with one shelter/foster group or vet clinic.
- Collect objections and missing fields.
- Add admin review status: draft, needs evidence, partner-ready, archived.
- Add exportable PDF version of the passport.

### Week 4

- Package the pilot results: number of profiles, readiness score improvement, partner feedback, screenshots.
- Decide whether to pursue B2B shelter/vet workflow, pet-parent subscription, or supply affiliate path first.
- Prepare an updated pitch that says clearly: "We are not a marketplace; we are the trust and care-readiness layer."

## Monetization Path

Best near-term model:

- Free pet-parent analysis for adoption/care education.
- B2B light plan for shelters/rescues/vets that need organized readiness records.
- Affiliate revenue from supplies only.
- Vet referral partnerships only where permitted and transparent.

Avoid charging for:

- Live animal listings.
- Breeder placement.
- Escrow.
- "Verified sale" badges before legal review.

Suggested packages:

- Free: breed scan, basic care guide, one Trust Passport draft.
- Partner: shelter/vet dashboard, multiple profiles, export, follow-up reminders, 29-79 AZN/month after pilot.
- Pro Network: partner directory, reviewed readiness workflows, analytics, API/export, custom pricing.

## Success Metrics

- Activation: pet profile created, care guide downloaded, Trust Passport generated.
- Quality: percentage of profiles with 80%+ readiness score.
- Partner value: partner accepts passport as useful, requests changes, or reuses it.
- Retention: profiles updated after 7 and 30 days.
- Revenue readiness: number of partner conversations that ask for dashboard/export/admin features.

## What To Delay

- Mobile app rebuild.
- Escrow.
- Marketplace listings.
- Full clinic management.
- Large AI model training.
- Multi-country launch.

## Frontend Decision

Streamlit is acceptable for the current open demo because the product still depends heavily on Python AI, PDF, and readiness logic. The near-term fix is to make Streamlit feel lighter and more user-friendly, not to rewrite the whole product before partner validation.

Vercel/Next.js becomes the right move after the Trust Passport flow has real partner feedback and the backend API contract is stable. See `docs/vercel-migration-plan.md`.

## Next Product Build

The next build after the Streamlit Trust Passport should be a partner pilot dashboard:

- Authenticated partner accounts.
- Pet profile list.
- Passport status.
- Evidence attachments.
- Follow-up reminders.
- Export to PDF.
- Analytics events.

## Implementation Update - 2026-07-09

The repo now has the first persistence hardening needed for a credible pilot:

- Local JSON remains the default demo mode.
- MongoDB is supported only through Woofer-specific variables: `WOOFER_STORAGE_BACKEND`, `WOOFER_MONGODB_URI`, `WOOFER_MONGO_DB_NAME`, and `WOOFER_MONGO_COLLECTION`.
- Generic `MONGODB_URI` is intentionally ignored so Woofer does not accidentally connect to unrelated trading, automation, or analytics databases.
- Generated runtime JSON and local secrets are ignored by git.
- GitHub Actions runs unit tests and syntax checks on pushes and pull requests.
- Trust Passport now includes missing-evidence guidance and both Markdown and PDF export for partner sharing.

This does not replace the need for auth, consent, privacy controls, and partner access rules before collecting real multi-user data.

