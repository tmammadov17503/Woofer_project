# Woofer Pilot Proposal

Updated: 2026-07-16

## Purpose

Woofer is testing a responsible pet-care and trust-readiness workflow for adoption, fostering, vet referral, and responsible ownership transfer. The pilot is intentionally not a marketplace, escrow product, breeder tool, or payment flow.

## Pilot Audience

- Animal shelters and rescue groups.
- Foster coordinators.
- Veterinary clinics.
- Responsible adopters or pet owners.
- Startup advisors evaluating welfare, compliance, and product readiness.

## What The Pilot Tests

1. Create or load a pet profile.
2. Review breed-aware care guidance.
3. Generate a Trust Passport with country-aware readiness checks.
4. Use Partner Pilot Review to capture partner type, pilot stage, readiness score, missing evidence, reviewer notes, and feedback signal.
5. Download a Markdown pilot report for follow-up.

## Success Criteria

- At least 10 pet profiles reviewed with the Trust Passport workflow.
- At least 3 external reviewers provide structured feedback.
- At least 1 shelter, foster group, or vet clinic confirms whether the readiness checklist matches their real workflow.
- The pilot identifies the top 3 missing evidence items that block adoption, foster, vet referral, or responsible transfer review.

## What Woofer Will Not Do In This Pilot

- No animal sales.
- No breeder payments.
- No escrow.
- No live marketplace listings.
- No legal or veterinary diagnosis claims.
- No multi-organization private data collection without auth, consent, and access controls.

## Data Handling

The open demo uses local JSON storage by default. Private beta persistence can use an isolated Woofer MongoDB database through Woofer-specific environment variables only. Do not connect Woofer to unrelated automation, trading, analytics, or bot databases.

## Next Build After Pilot

- Authenticated partner accounts.
- Evidence attachments for vaccination, microchip, consent, and vet records.
- Consent notice, data export, and delete controls.
- Partner dashboard history and follow-up reminders.
- Mobile-first Vercel/Next.js frontend after the workflow is validated.
