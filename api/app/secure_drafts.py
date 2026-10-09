"""Authenticated encrypted draft storage. Requires deployment secret and user identity token.
Not an agency submission. SQLite is for single-instance pilots, use PostgreSQL for production.
"""
import os,sqlite3,secrets,time
from contextlib import closing
from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel, Field
from cryptography.fernet import Fernet, InvalidToken
from .main import INDEX
router=APIRouter(prefix="/v1/private",tags=["encrypted private drafts"])
DB=os.getenv("JUMUISHA_DB_PATH","/tmp/jumuisha_drafts.sqlite3")
KEY=os.getenv("JUMUISHA_FERNET_KEY")
AUTH=os.getenv("JUMUISHA_PILOT_BEARER_TOKEN")
def require_user(authorization: str | None=Header(default=None)):
    # Pilot-only single-operator auth, explicitly NOT citizen account authentication.
    if not AUTH or not KEY:
        raise HTTPException(503,"Secure private workflow is not configured")
    if not authorization or not secrets.compare_digest(authorization,f"Bearer {AUTH}"):
        raise HTTPException(401,"Authentication required")
    return "pilot-operator"
def cipher():
    try: return Fernet(KEY.encode())
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
