# Safety, accessibility and deployment gates

## Acceptance criteria
- WCAG 2.2 AA audit of every flow (including errors), TalkBack, VoiceOver, NVDA, keyboard-only, zoom, switch access and reduced motion.
- Test with KSL-fluent reviewers, blind, deafblind, motor and cognitive disability groups. Supply consent forms in accessible modalities; pay participants.
- Never infer legal eligibility, tax liability or financial charges from an LLM. Use authoritative agency rules, provenance and update timestamps.
- Explicit review/confirmation for all consequential actions; receipts distinguish **draft** from **official submission**.
- KSL clip editorial pipeline: agreed source phrase -> Deaf community translation/review -> consent and license -> compression (WebP frames for short signs, H.264 MP4 for sentences) -> checksum -> offline cache -> accessibility QA. Do not claim generative signing accuracy.
- Human interpreter escalations for legal/health/identity-critical work.
- Offline caches contain public material by default; encrypted user drafts require device security and expiring retention policies.

## Production blockers
This starter has neither persistent user identity nor real transactions. Implement OIDC/Firebase Auth, server-enforced authorization, consent ledger, key management, secrets vault, logging without sensitive payloads, abuse prevention, secure database, restore procedures, deletion/export, incident response and penetration testing before citizen data collection.

Agency adapters require contracts and official API documentation; never automate captcha, scrape protected records, or ask users for government portal passwords.

## Measurement
Record consented, privacy-safe aggregated task completion, errors, language performance and assistive-device coverage; segment results without exposing individual disability profiles. No sensitive recordings used for training by default.
