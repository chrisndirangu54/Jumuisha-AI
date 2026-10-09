"""Optional OIDC JWT verification for per-user authorization.
Validate issuer, audience, signature, expiry and issued-at. Requires trusted JWKS URI.
"""
import os
from functools import lru_cache
from fastapi import HTTPException
import jwt
from jwt import PyJWKClient, PyJWTError

@lru_cache(maxsize=2)
def jwks_client(uri: str):
    if not uri.startswith("https://"):
        raise ValueError("JWKS URI must be HTTPS")
    return PyJWKClient(uri,cache_jwk_set=True,lifespan=300)

def verify_user_token(token: str) -> str:
    issuer=os.getenv("JUMUISHA_OIDC_ISSUER","").rstrip("/")
    audience=os.getenv("JUMUISHA_OIDC_AUDIENCE","")
    jwks=os.getenv("JUMUISHA_OIDC_JWKS_URI","")
    if not issuer or not audience or not jwks:
        raise HTTPException(503,"Identity verification is not configured")
    if not issuer.startswith("https://") or not jwks.startswith("https://"):
        raise HTTPException(503,"Identity authority must use HTTPS")
    try:
        key=jwks_client(jwks).get_signing_key_from_jwt(token).key
        claims=jwt.decode(token,key,algorithms=["RS256"],audience=audience,issuer=issuer,options={"require":["sub","exp","iat","iss","aud"]},leeway=30)
    except (PyJWTError,ValueError) as ex:
        raise HTTPException(401,"Invalid identity token") from ex
    subject=claims.get("sub")
    if not isinstance(subject,str) or not subject or len(subject)>256:
        raise HTTPException(401,"Invalid identity subject")
    return issuer+"|"+subject
