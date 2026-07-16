# Vercel Migration Plan

Updated: 2026-07-16

## Recommendation

Do not rewrite Woofer to Vercel immediately. First, make the current Streamlit app feel friendly enough for open demos and early partner conversations. Then migrate the public product experience to Vercel when the core flow is validated.

The reason: Woofer's current value is Python-heavy: image analysis, care-guide generation, PDF export, storage, and Trust Passport logic. Rebuilding all of that in a new frontend stack before a pilot would slow the project down.

## Best Architecture Later

- Vercel / Next.js: public app frontend, mobile-first interface, landing pages, partner-friendly workflows.
- Python API service: breed analysis, care logic, PDF generation, and future model work.
- MongoDB Atlas: isolated Woofer profile and partner-pilot data.
- Object storage: future photo/evidence uploads.
- No auth at first: keep the open demo flow until partner workflows need private data access.

## When To Move

Move to Vercel after these are true:

- The Trust Passport and Pilot Review flow is validated by at least one shelter, vet, foster group, or advisor.
- The app needs a more polished mobile-first user experience than Streamlit can comfortably provide.
- The backend API contract is stable enough to avoid rewriting the same product twice.

## No-Regret Work Done Now

- Explicit light Streamlit theme.
- Friendlier first-screen product hero.
- Mobile-safe layout styles for tabs, buttons, download controls, code previews, and cards.
- No-auth Partner Pilot Review workflow for early shelter, vet, foster, and advisor testing.
- Vercel-ready product direction documented without blocking the current demo.

## First Vercel Build

The first Vercel version should not be a giant rebuild. It should be a thin frontend over the existing product logic:

- Home/dashboard screen.
- Create pet profile flow.
- Trust Passport checklist.
- Pilot Review dashboard and report download.
- PDF download action served by Python API.
- Public demo mode with sample data.
- Later: partner accounts, private records, consent, and evidence uploads.
