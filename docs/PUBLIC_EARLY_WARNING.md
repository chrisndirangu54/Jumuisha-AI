# Public early warning module (prototype)

## Current implementation
- `GET /v1/early-warning/alerts`: returns **only active verified actual alerts** by default. Currently always empty because no authorized live data source is connected.
- `GET /v1/early-warning/alerts?include_exercises=true`: displays an explicitly labeled demonstration exercise.
- Optional `county` and `hazard` filters; national alerts are included alongside a county filter.
- `GET /v1/early-warning/alerts/{id}` and `GET /v1/early-warning/readiness`.
- Flutter read-only Public Early Warnings screen, county filter, exercise toggle, bilingual text, and accessible semantics.
- Exercise content **must never be represented as real-time disaster warnings**.

## Essential work before production
1. Signed/authorized feed ingestion from responsible authorities, with verifiable provenance, timestamps, geographical polygons, incident IDs and revocation/cancellation handling. Prefer Common Alerting Protocol (CAP) where supplied.
2. Persistent datastore, ingestion audit trails, idempotency, publisher roles, human approval, and fraud protection. Do not accept public unauthenticated alert publishing.
3. Validation of alert life cycle (alert/update/cancel), expiration, jurisdiction, multilingual messaging, clock skew, data confidence and freshness; test delivery under outages.
4. Human reviewed English/Kiswahili and qualified Kenyan Sign Language warnings, accessible map alternatives, high contrast, offline caching with prominent stale-content notices.
5. User-opt-in geographic targeting, minimized retention, secure notification subscriptions and opt-out, SMS/USSD/IVR/push providers, abuse prevention, provider delivery receipts, rate limiting and alert fatigue management.
6. Device field tests with disability communities; emergency operations drills, fallback communication channels, threat models and a formally agreed incident-response owner.
7. AI hazard predictions remain internal advisory signals, never automatically branded as official warnings.

## Testing
Run `cd api && pytest -q`; run `cd mobile && flutter analyze && flutter test` with installed dependencies. No live alert-feed acceptance tests or provider delivery tests have been completed.
