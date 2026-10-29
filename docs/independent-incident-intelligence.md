# Independent incident discovery and regulatory review

Jumuisha AI can collect **evidence leads** for diseases, fires, road crashes, industrial accidents and other accidents without a Regen Insights dependency.

## Intake channels
- Manual: qualified organizations enter location, event summary, source URL and observation time.
- Licensed API: adapters can submit normalized reports with provider credentials and terms.
- Permitted web: rights-respecting crawlers or RSS feed readers **may** submit source URLs and minimal summaries, subject to robots rules, publishers' terms, source licensing and rate limits.
- Official bulletin: agency advisories can be recorded and verified against the original issuing organization.

**No scraper, API supplier or background polling service is actually connected yet.** The ingestion route is a server-side entry point only, and is disabled unless operators configure an intake credential.

## Pilot workflow

1. Submit an evidence lead using `POST /v1/incident-intelligence/leads` with `X-Incident-Intake-Key`, configured by `JUMUISHA_INCIDENT_INTAKE_KEY`.
2. Authorized reviewers query `GET /v1/incident-intelligence/internal/leads` with `X-Incident-Review-Key`, configured by `JUMUISHA_INCIDENT_REVIEW_KEY`.
3. Reviewer checks original evidence, asks the appropriate regulator or issuing authority for official verification and records the decision with `POST /v1/incident-intelligence/internal/leads/{id}/review`.
4. Approval requires an independently verified authority reference and an explicit category-specific allowlist, e.g. `JUMUISHA_APPROVED_AUTHORITY_FIRE`. Review returns `public_warning_created: false`; the system **does not** automatically elevate leads to official public alerts.

The relevant public health authority could be the Ministry of Health / Kenya National Public Health Institute or delegated county offices. Fire response is often county-led; traffic collisions involve police and transport authorities; environmental incidents may require NEMA. Confirm **specific** jurisdiction and publication authority per event and region; this document does not grant authorization.

## Important limits and pre-release controls

- Pilot stores all data only in memory; restarts lose submitted leads, reviews and records. No durable workflow or audit-grade persistence.
- Shared header secrets are not named institutional authentication or proof of regulatory approval. In production replace with OIDC/mTLS, authenticated agency identity, contractual delegation, signed authorization artifacts, dual control, immutable audit records and incident revisions.
- No patient identifiers, victim names, witness phone numbers, precise residence details, medical records or casualty images should enter the intake. Add automated PII detection, privacy impact assessments and retention/redaction controls.
- Add reliable deduplication across repeated news syndication, geocoding with uncertainty, corroboration and source credibility labels. AI classifications should remain review suggestions.
- A source name or website domain alone is not regulator approval. API data may be observed without legal permission to issue alerts.
- Keep public warning publication restricted to the separately controlled early-warning service, after institutional approval and independent operations testing.
- API testing: `cd api && pytest -q tests/test_incident_intelligence.py`.

## Recommended source onboarding
- First-party official bulletins with signed or documented feeds and redistribution rights.
- Publisher-permitted RSS or paid news APIs for situational awareness, clearly labeled **unverified reports**.
- Secure official agency submissions, with multiple roles and an independent review trail.
- Optional Regen Insights analytical evidence, not required for public incident discovery.
