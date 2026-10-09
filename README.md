# Jumuisha AI

An accessibility-first, Kenya-focused public-service navigator for people with disabilities and underserved communities.

## What runs today
- FastAPI government-service catalogue, accessibility preferences, consent-scoped draft workflow, accessibility guidance and connector capability registry.
- Flutter starter with selectable text/voice-friendly/large-text/reduced-motion modes, semantics, scalable text and service browsing.
- Kenyan Sign Language (KSL) content manifest supporting **cached human-validated 2D video and sprite sequences**, with text fallback and interpreter handoff.
- Offline-friendly catalog/manifest design; sample content is explicitly marked as demonstration content.
- Automated API tests and GitHub Actions checks.

## Boundaries
**This repository does not claim integration with live eCitizen, NTSA, SHA, NCPWD, IPRS, BRS or other restricted systems.** All agency submissions are disabled unless separately implemented, contractually authorized, tested and explicitly enabled. KRA GavaConnect and eTIMS adapters likewise require official credentials, specifications and certification; no browser scraping or PIN/password collection shortcuts.

KSL assets are not machine-generated translations. Human-reviewed KSL clips should be recorded with Deaf language experts, associated with exact phrases, versioned, licensed and cached. Sprite sequences can serve short fixed phrases but need usability testing; prioritize compressed 2D video for fluid signing. Real-time 3D avatars, AI video and gesture translation stay experimental until independently validated.

## Start API
```bash
cd api
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
pytest -q
```
Visit http://localhost:8000/docs

## Flutter client
```bash
cd mobile
flutter pub get
flutter run --dart-define=API_BASE_URL=http://10.0.2.2:8000
```
Use http://localhost:8000 for desktop/web development as applicable.

## Architecture
```
mobile/    Flutter accessible starter UI
api/       FastAPI catalogue, drafts, consent and integration guards
content/   KSL content manifest and accessibility editorial guides
docs/      service onboarding, privacy, safety and field validation plan
```

## Production roadmap
1. Co-design and validate with Deaf, blind, deafblind, motor and cognitive-disability communities. WCAG 2.2 AA audit, accessibility device matrix.
2. Add authenticated accounts, PostgreSQL migrations, encryption, object-storage controls, background queue, rate limits, fine-grained access, retention/deletion, legal review and secure audit logging.
3. Build truly offline encrypted local drafts and robust synchronization; SMS/USSD/IVR and human interpretation through licensed providers.
4. Integrate documented KRA APIs within approved scopes and certifications; agency-specific connectors only after agreements.
5. Evaluate Kenyan language ASR/TTS and supervised KSL research against community-defined quality and safety thresholds. Never automatically sign legal or health instructions with unvalidated generators.

## Principles
Consent, dignity, autonomy, low-bandwidth access, local language inclusion, safety, verifiable source provenance, and no invented government fees or eligibility determinations.

MIT license for project code; separately obtained recordings/data keep their own consent and licenses.

## October 9, 2026 implementation update
- The Flutter catalogue now opens a dedicated service journey with agency URL, non-authoritative guide, consent-gated local notes and delete control.
- Read-only API endpoints under `/v1` provide deterministic bilingual navigation, service instructions, human assistance guidance and capability reporting.
- Device TTS and a local public-catalogue cache were added. No private citizen information should be stored in that public cache.
- Additional API and widget regression tests were added. GitHub Actions workflows are committed, but successful execution has not been verified in this session.
- **Not implemented or validated**: live agency submission, production account/auth, encrypted personal draft synchronization, actual SMS/USSD/IVR provider flows, live interpreter dispatch, qualified KSL recordings, automatic KSL recognition, actual refreshable Braille device tests, comprehensive WCAG audit, and deployment. Do not deploy for citizen personal data yet.

## 2026-10-09 voice / KSL delivery
- VoiceSearch provides device-provided speech recognition with manual text correction and a keyboard alternative. It searches local catalogue entries, not citizen records.
- KslPlayer supports HTTPS-hosted video only when the caller marks it reviewed; the app currently supplies **no approved assets**, so users see an explicit fallback message.
- Tests validate the input alternative and the no-asset KSL fallback.
- Device deployment still requires Android RECORD_AUDIO permission and iOS microphone/speech usage descriptions; these must be committed in generated platform projects and reviewed with users.
- Speech recognition availability and privacy depend on native OS vendors. Do not describe it as offline or Kenyan-language validated until independently tested.
- A valid KSL asset must pass an ingestion gate that checks actual recording provenance, consent/license, hash, community sign-off and domain allowlist; the UI's reviewed flag alone is not secure approval.
- Still blocked for national production: government API agreements, community-evaluated signing assets, real assistive-device tests, citizen-grade encrypted offline sync, persistent multi-tenant DB, observability, security review and verified passing builds.
