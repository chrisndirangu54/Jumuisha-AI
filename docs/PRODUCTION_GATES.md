# Jumuisha AI production release gates

The service navigator is **not** production certified. Do not promote it as government affiliated, submit to agencies, or collect sensitive data before all required gates pass.

## Engineering gates
- Identity: OIDC provider, scoped authorization, phishing-resistant administrator MFA, account recovery, delegation with explicit revocation.
- Data: encrypted database and backup, per-purpose consent ledger, access and deletion workflow, retention policy, secret storage, breach processes.
- Networks: rate limiting, HTTPS/HSTS, origin restrictions, strict CSP on hosted web client, supply-chain scanning, structured redacted logs, operational alerting.
- Transactions: verified official specifications and government approval, signed transaction confirmation, duplicate-safe idempotency, receipt reconciliation, agency outage handling.
- Offline: encryption at rest, authentication expiry, draft conflicts, background reconciliation and theft/loss handling.
- Compliance: Kenya Data Protection Act and disability-law review, accessibility statements, redress and support arrangements.

## Community-validated accessibility gates
- Audit against WCAG 2.2 AA plus assistive technology usability, keyboard, focus order, error suggestions, contrast, labels, zoom and dynamic text.
- Test Android TalkBack, iOS VoiceOver, web NVDA, switch control, refreshable Braille and screen magnification on representative devices.
- Real Kenyan Sign Language recordings require Deaf community review, clear license, release permission, transcripts/captions, asset checksum and replayable offline codec.
- KSL generation or sign recognition cannot be marketed as accurate before independent evaluation and community sign-off.
- Kiswahili speech needs device voice availability and linguist user testing; automated fallback must always provide text.
- Recruitment should include Deaf, blind, deafblind, cognitive and motor disability participants, including rural low-bandwidth users. Obtain accessible consent and fair compensation.

## Release decision
A human owner must sign off both independent security and accessibility evidence. CI passing is necessary but not sufficient. Current release flag: **NO**.
