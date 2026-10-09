# Production identity integration

The new OIDC validator checks HTTPS issuer, HTTPS JWKS, RS256 signature, audience, issued-at, expiration and stable subject. Configure JUMUISHA_OIDC_ISSUER, JUMUISHA_OIDC_AUDIENCE, and JUMUISHA_OIDC_JWKS_URI for a trusted identity provider (for example a properly configured OIDC tenant). Verify correct client and resource audience, session lifecycle and account recovery in integration tests.

**Do not enable shared pilot authentication in an internet deployment.** It exists only as the initial single-operator engineering harness. Move citizens to properly authenticated per-user database records. Configure key rotation, token-revocation policy, device key storage, scoped authorizations, delegated account permissions and redacted audit logs. Production API endpoints should reject unconfigured identity providers by default.

A government API gateway requires separate credentials and authorization per agency. User identity does not grant government API permissions.
