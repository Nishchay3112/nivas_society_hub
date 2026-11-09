import os, csv, io, json, hmac, hashlib, base64, time, secrets, random
from datetime import date, datetime, timedelta
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, DateTime, Boolean, Text
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from .logic import classify, match_rows, similar
from .ai_triage import triage_complaint
from dotenv import load_dotenv

load_dotenv()

DB = os.getenv("DATABASE_URL", "sqlite:///./society.db")
engine = create_engine(DB, connect_args={"check_same_thread": False} if DB.startswith("sqlite") else {})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()
SECRET = (os.getenv("JWT_SECRET") or secrets.token_hex(32)).encode()
DEMO = os.getenv("DEMO_MODE", "1") == "1"
LATE_RATE = 0.21  # ASSUMPTION: 21% p.a. simple interest after due date (bye-law rate not given)
TEAM = {"plumbing": "Plumbing team", "electrical": "Electrical team", "lift": "Lift vendor", "housekeeping": "Housekeeping",
        "security": "Security desk", "parking": "Security desk", "needs_triage": "Help desk triage"}
SLA_H = {"critical": 1, "high": 4, "normal": 24}


class User(Base):
    __tablename__ = "users"; id = Column(Integer, primary_key=True); phone = Column(String, unique=True, index=True)
    name = Column(String); role = Column(String); flat_no = Column(String)
class Flat(Base):
    __tablename__ = "flats"; no = Column(String, primary_key=True); tower = Column(String); area = Column(Integer); upi = Column(String)
class Bill(Base):
    __tablename__ = "bills"; id = Column(Integer, primary_key=True); flat_no = Column(String, index=True)
    month = Column(String); amount = Column(Integer); paid = Column(Integer, default=0); due_date = Column(Date)
class Payment(Base):
    __tablename__ = "payments"; id = Column(Integer, primary_key=True); flat_no = Column(String, index=True)
    amount = Column(Integer); source = Column(String); ref = Column(String); at = Column(DateTime, default=datetime.utcnow)
class Complaint(Base):
    __tablename__ = "complaints"; id = Column(Integer, primary_key=True); flat_no = Column(String, index=True); text = Column(String)
    category = Column(String); urgency = Column(String); confidence = Column(Float); safety = Column(Boolean, default=False)
    rating = Column(Integer); photo = Column(Text); reopens = Column(Integer, default=0); status = Column(String, default="open"); assignee = Column(String); duplicate_of = Column(Integer)
    created = Column(DateTime, default=datetime.utcnow); due_by = Column(DateTime); closed_at = Column(DateTime)
class BankRow(Base):
    __tablename__ = "bank_rows"; id = Column(Integer, primary_key=True); date = Column(String); ref = Column(String)
    upi = Column(String); amount = Column(Integer); status = Column(String); flat_no = Column(String); note = Column(String)


def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()


# ---- minimal HS256 JWT (stdlib) ----
def _b(x): return base64.urlsafe_b64encode(x).rstrip(b"=").decode()
def _ub(s): return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))
def make_token(u):
    h, p = _b(b'{"alg":"HS256","typ":"JWT"}'), _b(json.dumps({"sub": u.id, "role": u.role, "exp": int(time.time()) + 8 * 3600}).encode())
    return f"{h}.{p}." + _b(hmac.new(SECRET, f"{h}.{p}".encode(), hashlib.sha256).digest())
from fastapi import Header
def auth(*roles):
    def dep(authorization: str = Header(default=""), db: Session = Depends(get_db)):
        try:
            h, p, s = authorization.removeprefix("Bearer ").split(".")
            ok = hmac.compare_digest(s, _b(hmac.new(SECRET, f"{h}.{p}".encode(), hashlib.sha256).digest()))
            data = json.loads(_ub(p)); assert ok and data["exp"] > time.time()
        except Exception:
            raise HTTPException(401, "Please sign in again")
        u = db.get(User, data["sub"])
        if not u or (roles and u.role not in roles): raise HTTPException(403, "You don't have access to this")
        return u
    return dep


app = FastAPI(title="Society Hub API")
app.add_middleware(CORSMiddleware, allow_origins=os.getenv("ALLOWED_ORIGIN", "http://localhost:5173").split(","), allow_methods=["*"], allow_headers=["*"])
OTPS: dict = {}


def fee(b):
    d = (date.today() - b.due_date).days
    return round(max(0, b.amount - b.paid) * LATE_RATE * d / 365) if d > 0 else 0
def days_over(b): return max(0, (date.today() - b.due_date).days) if b.amount > b.paid else 0


class PhoneIn(BaseModel): phone: str = Field(pattern=r"^\d{10}$")
class VerifyIn(PhoneIn): otp: str = Field(pattern=r"^\d{6}$")
class PayIn(BaseModel): amount: int | None = Field(default=None, gt=0)
class ComplaintIn(BaseModel):
    text: str = Field(min_length=5, max_length=500)
    photo: str | None = Field(default=None, max_length=400000, pattern=r"^data:image/(jpeg|png);base64,[A-Za-z0-9+/=]+$")
class ComplaintPatch(BaseModel): status: str | None = Field(default=None, pattern="^(open|assigned|in_progress|closed)$"); category: str | None = None
class AssignIn(BaseModel): flat_no: str


@app.post("/auth/otp")
def send_otp(b: PhoneIn, db: Session = Depends(get_db)):
    rec = OTPS.get(b.phone)
    if rec and rec["sent"] > time.time() - 30: raise HTTPException(429, "Wait 30 seconds before requesting another OTP")
    otp = f"{secrets.randbelow(10**6):06d}"
    OTPS[b.phone] = {"h": hashlib.sha256(otp.encode()).hexdigest(), "exp": time.time() + 300, "tries": 0, "sent": time.time()}
    return {"sent": True, "demo_otp": otp if DEMO else None}  # SMS is mocked; OTP shown only in demo mode


@app.post("/auth/verify")
def verify(b: VerifyIn, db: Session = Depends(get_db)):
    rec, u = OTPS.get(b.phone), db.query(User).filter_by(phone=b.phone).first()
    if not rec or not u or rec["exp"] < time.time() or rec["tries"] >= 5: raise HTTPException(400, "OTP expired. Request a new one")
    rec["tries"] += 1
    if not hmac.compare_digest(rec["h"], hashlib.sha256(b.otp.encode()).hexdigest()): raise HTTPException(400, "Wrong OTP")
    OTPS.pop(b.phone)
    return {"token": make_token(u), "role": u.role, "name": u.name, "flat_no": u.flat_no}


@app.get("/home")
def home(u: User = Depends(auth("resident")), db: Session = Depends(get_db)):
    b = db.query(Bill).filter_by(flat_no=u.flat_no).first()
    cs = db.query(Complaint).filter_by(flat_no=u.flat_no).order_by(Complaint.id.desc()).all()
    return {"name": u.name, "flat_no": u.flat_no,
            "bill": {"id": b.id, "month": b.month, "amount": b.amount, "paid": b.paid, "late_fee": fee(b), "days_overdue": days_over(b),
                     "due_date": str(b.due_date), "total_due": b.amount - b.paid + fee(b)},
            "complaints": [cj(c) for c in cs],
            "ledger": [{"id": p.id, "ref": p.ref, "amount": p.amount, "source": p.source, "at": p.at.isoformat()} for p in db.query(Payment).filter_by(flat_no=u.flat_no).order_by(Payment.id.desc()).all()]}


def cj(c):
    d = {col.name: getattr(c, col.name) for col in c.__table__.columns if col.name != "photo"}
    d = {k: (v.isoformat() if isinstance(v, datetime) else v) for k, v in d.items()}
    d["has_photo"] = bool(c.photo); return d

@app.post("/bills/pay")
def pay(b: PayIn, u: User = Depends(auth("resident")), db: Session = Depends(get_db)):
    bill = db.query(Bill).filter_by(flat_no=u.flat_no).first()
    total = bill.amount - bill.paid + fee(bill)
    amt = b.amount or total
    if total <= 0: raise HTTPException(400, "Nothing is due")
    if amt > total: raise HTTPException(400, f"Amount is more than the ₹{total} due")
    bill.paid += min(amt, bill.amount - bill.paid)
    db.add(Payment(flat_no=u.flat_no, amount=amt, source="test_online", ref="TEST-" + secrets.token_hex(4)))  # gateway mocked
    db.commit(); return {"ok": True, "paid": amt}


@app.post("/complaints")
def create_complaint(b: ComplaintIn, u: User = Depends(auth("resident")), db: Session = Depends(get_db)):
    
    r = triage_complaint(b.text)

    c = Complaint(
        flat_no=u.flat_no,
        text=b.text.strip(),
        photo=b.photo,
        **r
    )

    c.assignee = (
        "Duty manager" if r["safety"]
        else TEAM[r["category"]]
    )

    c.status = "assigned"
    c.due_by = datetime.utcnow() + timedelta(
        hours=SLA_H[r["urgency"]]
    )

    for o in db.query(Complaint).filter(
        Complaint.status != "closed",
        Complaint.category == c.category,
        Complaint.duplicate_of.is_(None)
    ).limit(300):

        if o.flat_no[:3] == c.flat_no[:3] and similar(o.text, c.text):
            c.duplicate_of = o.id
            break

    db.add(c)
    db.commit()

    return cj(c)



@app.get("/complaints")
def list_complaints(u: User = Depends(auth("helpdesk", "committee")), db: Session = Depends(get_db)):
    order = {"critical": 0, "high": 1, "normal": 2}
    cs = db.query(Complaint).filter(Complaint.status != "closed").all()
    return sorted([cj(c) for c in cs], key=lambda c: (order[c["urgency"]], c["created"]))[:100]


@app.patch("/complaints/{cid}")
def patch_complaint(cid: int, b: ComplaintPatch, u: User = Depends(auth("helpdesk")), db: Session = Depends(get_db)):
    c = db.get(Complaint, cid)
    if not c: raise HTTPException(404, "Complaint not found")
    if b.category:
        if b.category not in TEAM: raise HTTPException(422, "Unknown category")
        c.category = b.category
        if not c.safety: c.assignee = TEAM[b.category]
    if b.status: c.status = b.status; c.closed_at = datetime.utcnow() if b.status == "closed" else None
    db.commit(); return cj(c)


def flat_dues(db):
    upi = {f.no: f.upi for f in db.query(Flat)}
    return {b.flat_no: {"due": b.amount - b.paid, "due_with_fee": b.amount - b.paid + fee(b), "upi": upi.get(b.flat_no)} for b in db.query(Bill)}


def post_payment(db, flat, amt, src, ref):
    b = db.query(Bill).filter_by(flat_no=flat).first(); b.paid += min(amt, b.amount - b.paid)
    db.add(Payment(flat_no=flat, amount=amt, source=src, ref=ref))


@app.post("/bank/upload")
async def upload(file: UploadFile = File(...), u: User = Depends(auth("helpdesk")), db: Session = Depends(get_db)):
    raw = await file.read()
    if len(raw) > 2_000_000: raise HTTPException(413, "File is larger than 2 MB")
    try:
        rows = [{"date": r["date"], "ref": r.get("reference", ""), "upi": r.get("upi", ""), "amount": int(float(r["amount"]))}
                for r in csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))]
    except Exception:
        raise HTTPException(422, "Could not read the CSV. Expected columns: date, reference, upi, amount")
    res = match_rows(rows, flat_dues(db)); auto = 0
    for r, m in zip(rows, res):
        db.add(BankRow(date=r["date"], ref=r["ref"], upi=r["upi"], amount=r["amount"], status=m["status"], flat_no=m["flat_no"], note=m["note"]))
        if m["status"] == "auto": post_payment(db, m["flat_no"], r["amount"], "bank_auto", r["ref"]); auto += 1
        db.flush()
    db.commit(); return {"rows": len(rows), "auto_posted": auto, "queued": len(rows) - auto}


@app.get("/bank/queue")
def queue(u: User = Depends(auth("helpdesk")), db: Session = Depends(get_db)):
    d = flat_dues(db)
    return [{"id": r.id, "date": r.date, "ref": r.ref, "upi": r.upi, "amount": r.amount, "note": r.note, "flat_no": r.flat_no,
             "suggestions": [f for f, x in d.items() if x["due"] == r.amount][:5] if not r.flat_no else []}
            for r in db.query(BankRow).filter_by(status="queue")]


@app.post("/bank/queue/{rid}/assign")
def assign(rid: int, b: AssignIn, u: User = Depends(auth("helpdesk")), db: Session = Depends(get_db)):
    r = db.get(BankRow, rid)
    if not r or r.status != "queue": raise HTTPException(404, "Row not in queue")
    if not db.query(Bill).filter_by(flat_no=b.flat_no).first(): raise HTTPException(422, "Unknown flat")
    post_payment(db, b.flat_no, r.amount, "bank_manual", r.ref); r.status, r.flat_no = "posted", b.flat_no
    db.commit(); return {"ok": True}


@app.post("/bank/queue/{rid}/reject")
def reject(rid: int, u: User = Depends(auth("helpdesk")), db: Session = Depends(get_db)):
    r = db.get(BankRow, rid)
    if r and r.status == "queue": r.status = "rejected"; db.commit()
    return {"ok": True}


@app.get("/committee/summary")
def summary(u: User = Depends(auth("helpdesk", "committee")), db: Session = Depends(get_db)):
    bills = db.query(Bill).all(); billed = sum(b.amount for b in bills); paid = sum(b.paid for b in bills)
    ageing = {"0-30": 0, "31-60": 0, "60+": 0}
    for b in bills:
        d = days_over(b)
        if d: ageing["0-30" if d <= 30 else "31-60" if d <= 60 else "60+"] += b.amount - b.paid
    closed = db.query(Complaint).filter(Complaint.closed_at.isnot(None)).all()
    hrs = [(c.closed_at - c.created).total_seconds() / 3600 for c in closed]
    cs = db.query(Complaint).all()
    return {"billed": billed, "collected": paid, "collection_pct": round(100 * paid / billed, 1) if billed else 0, "ageing": ageing,
            "avg_resolution_hours": round(sum(hrs) / len(hrs), 1) if hrs else None,
            "open_complaints": sum(c.status != "closed" for c in cs), "overdue_sla": sum(c.status != "closed" and c.due_by < datetime.utcnow() for c in cs),
            "accounts_queue": db.query(BankRow).filter_by(status="queue").count(),
            "reopen_pct": round(100 * sum((c.reopens or 0) > 0 for c in cs) / len(cs), 1) if cs else 0}


@app.get("/health")
def health(): return {"ok": True}


@app.on_event("startup")
def startup():
    Base.metadata.create_all(engine)
    from .seed import seed
    from .extra import purge
    with SessionLocal() as db: seed(db); purge(db)


from .extra import r as _extra  # noqa: E402  (registers notice/visitor/booking models and routes)
app.include_router(_extra)
