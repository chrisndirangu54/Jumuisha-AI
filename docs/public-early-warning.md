# Public Early Warning System — pilot integration

## Implemented
- Public read-only `GET /v1/early-warning/alerts?county=Nairobi&hazard=flood`, with county/hazard filtering.
- Public `GET /v1/early-warning/status` explains that there is **no connected official live feed**.
- Restricted `POST /v1/early-warning/internal/alerts` and `DELETE /v1/early-warning/internal/alerts/{id}`, disabled without a configured key and approved source name.
- Enforced verified, actual, currently valid alert status; test/exercise, expired or unverified alerts do not appear publicly.
- Sequential alert revisions using a stable identifier; blocked stale/conflicting updates and publisher identity changes.
- Retractions yield public tombstones at `GET /v1/early-warning/retractions`, so clients can remove withdrawn warnings.
- Flutter accessible warning screen with county search, instructions, origin, expiry and conspicuous empty-feed safety warning.
- API tests for blocked ingestion, filtering and retraction.

## Development-only configuration
```bash
export JUMUISHA_WARNING_INGEST_KEY="<long-random-server-secret>"
export JUMUISHA_APPROVED_WARNING_SOURCES="Name of explicitly authorized issuing agency"
```
Never embed the secret in Flutter. Source names alone are **not** evidence of genuine official alerts: the operator must verify the publisher's identity, source feed and legal authorization before accepting an alert. The single shared secret is suitable only for controlled pilots; prefer mTLS or trusted provider-signed webhooks and named operator roles in production.

## Production blockers
1. Written coordination with the relevant Kenyan issuing authorities and authoritative data channels (e.g. Kenya Meteorological Department and disaster-management authorities, as applicable); evaluate CAP 1.2-compliant alerts, signed feeds and cancellation/update IDs.
2. Durable transactional PostgreSQL storage with publisher authentication, audit trails, replay defense, signature checking, idempotency, revocation, TTL, monitoring and high availability. The current in-memory alert and retraction stores are erased on restart and is **not a dependable warning system**.
3. Explicit geospatial coverage from approved county/subcounty/ward polygons, opt-in coarse-location subscription and a non-location alternative. Avoid collecting precise GPS by default.
4. Reliable opt-in SMS, USSD, voice/IVR and push notifications with delivery receipts, retry queues, language choices, consent, quiet-hour override policy for genuine emergencies and telecom/vendor agreements.
5. Human-reviewed English/Kiswahili and Kenyan Sign Language warnings, screen-reader order, large text, vibration/audio equivalents and disability-community usability validation.
6. Operational incident workflows: agency verification, publish/approve, severity assignment, update, cancel, drill/test isolation and published provenance. AI can summarize and translate reviewed information but must **never invent or independently authorize an emergency alert**.
7. Field tests, independent security assessment, incident simulation and continuous coverage/latency monitoring before any public claim of safety-critical reliability.

## Run checks
```bash
cd api
pip install -r requirements.txt
pytest -q tests/test_early_warning.py
```

Do not advertise the feature as real-time national emergency coverage until these blockers are resolved.
