"""Authenticated encrypted draft storage. Requires deployment secret and user identity token.
Not an agency submission. SQLite is for single-instance pilots, use PostgreSQL for production.
"""
import os,sqlite3,secrets,time
from contextlib import closing
from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel, Field
from cryptography.fernet import Fernet, InvalidToken
from .main import INDEX
from .oidc import verify_user_token
router=APIRouter(prefix="/v1/private",tags=["encrypted private drafts"])
DB=os.getenv("JUMUISHA_DB_PATH","/tmp/jumuisha_drafts.sqlite3")
def require_user(authorization: str | None=Header(default=None)):
    key=os.getenv("JUMUISHA_FERNET_KEY")
    if not key:
        raise HTTPException(503,"Encrypted storage is not configured")
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401,"Bearer authentication required")
    token=authorization[7:]
    if os.getenv("JUMUISHA_OIDC_ISSUER"):
        return verify_user_token(token)
    # Strictly opt-in local operator mode; NEVER use in a public deployment.
    auth=os.getenv("JUMUISHA_PILOT_BEARER_TOKEN")
    if os.getenv("JUMUISHA_ENABLE_PILOT_AUTH")!="true" or not auth:
        raise HTTPException(503,"OIDC authentication not configured")
    if not secrets.compare_digest(token,auth):
        raise HTTPException(401,"Invalid bearer token")
    return "pilot-operator"

def cipher():
    try: return Fernet(os.environ["JUMUISHA_FERNET_KEY"].encode())
    except (ValueError,TypeError): raise HTTPException(503,"Encryption key misconfigured")
def connect():
    connection=sqlite3.connect(DB,timeout=5)
    connection.execute("CREATE TABLE IF NOT EXISTS drafts (id TEXT PRIMARY KEY, owner TEXT NOT NULL,service_id TEXT NOT NULL, encrypted BLOB NOT NULL, updated INTEGER NOT NULL)")
    return connection
class Draft(BaseModel):
    service_id:str
    note:str=Field(max_length=2000)
    consent:bool
@router.post("/drafts")
def save(payload:Draft,owner:str=Depends(require_user)):
    if payload.service_id not in INDEX: raise HTTPException(404,"Unknown service")
    if not payload.consent: raise HTTPException(422,"Explicit storage consent required")
    draft_id=secrets.token_urlsafe(18)
    with closing(connect()) as db:
        db.execute("INSERT INTO drafts VALUES (?,?,?,?,?)",(draft_id,owner,payload.service_id,cipher().encrypt(payload.note.encode()),int(time.time())))
        db.commit()
    return {"draft_id":draft_id,"status":"encrypted_draft_not_submitted"}
@router.get("/drafts")
def list_drafts(owner:str=Depends(require_user)):
    with closing(connect()) as db:
        records=db.execute("SELECT id,service_id,updated FROM drafts WHERE owner=? ORDER BY updated DESC",(owner,)).fetchall()
    return [{"draft_id":r[0],"service_id":r[1],"updated":r[2]} for r in records]
@router.get("/drafts/{draft_id}")
def read(draft_id:str,owner:str=Depends(require_user)):
    with closing(connect()) as db:
        r=db.execute("SELECT service_id,encrypted FROM drafts WHERE id=? AND owner=?",(draft_id,owner)).fetchone()
    if not r: raise HTTPException(404,"Draft not found")
    try: plaintext=cipher().decrypt(r[1]).decode()
    except InvalidToken: raise HTTPException(503,"Unable to decrypt draft")
    return {"draft_id":draft_id,"service_id":r[0],"note":plaintext,"status":"not_submitted"}
@router.delete("/drafts/{draft_id}")
def delete(draft_id:str,owner:str=Depends(require_user)):
    with closing(connect()) as db:
        cur=db.execute("DELETE FROM drafts WHERE id=? AND owner=?",(draft_id,owner))
        db.commit()
    if not cur.rowcount: raise HTTPException(404,"Draft not found")
    return {"deleted":True}
