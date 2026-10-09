# Secure pilot constraints

The /v1/private endpoints support encrypted single-operator draft storage with an environment-provided Fernet key. An authentication token and encryption key are both REQUIRED; without them requests fail closed. The token is shared pilot authorization, not multi-user identity. This feature is suitable for local engineering evaluation only, not for use with citizen personal data. SQLite supports a single-instance pilot; production should use PostgreSQL, independent accounts, scoped roles, migration, retention policy, backups, secret rotation and full security assessment.

Never place the bearer token in a Flutter build or other public client. Future public-client workflows must use short-lived validated user tokens issued by a real OIDC provider, with per-user ownership enforcement. Secrets should be supplied by a secret manager. Avoid recording request payloads in logs. Fernet encryption does not guarantee safe storage when keys and database coexist without proper host controls.

The existing local Flutter notes are **not encrypted**. Never enter identity numbers, medical details, passwords or payment information. Do not connect those notes to the secure API without replacing them with a fully authenticated encrypted local store.

The data-directory permissions, consent records, threat model, privacy impact assessment, breach process, and agency authorization must all be verified before production.
