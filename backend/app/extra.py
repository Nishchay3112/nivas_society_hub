"""Notices, visitor management (gate), amenity booking, complaint rating."""
from datetime import datetime, timedelta, date, time as dtime
import secrets
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import Column, Integer, String, DateTime, Date, UniqueConstraint, Text
from sqlalchemy.orm import Session
from .main import Base, User, Flat, Complaint, Payment, SLA_H, get_db, auth, cj

r = APIRouter()
AMEN = {"Clubhouse": {"fee": 500, "slots": ["06-09", "09-12", "16-19", "19-22"]},
        "Tennis court": {"fee": 0, "slots": ["06-07", "07-08", "17-18", "18-19"]},
        "Party lawn": {"fee": 1500, "slots": ["10-14", "18-23"]}}  # ASSUMPTION: slots and fees


class Notice(Base):
    __tablename__ = "notices"; id = Column(Integer, primary_key=True); title = Column(String); body = Column(String); created = Column(DateTime, default=datetime.utcnow)
class Visitor(Base):
    __tablename__ = "visitors"; id = Column(Integer, primary_key=True); flat_no = Column(String, index=True); name = Column(String)
    purpose = Column(String); status = Column(String); code = Column(String); photo = Column(Text); created = Column(DateTime, default=datetime.utcnow)
class Booking(Base):
    __tablename__ = "bookings"; id = Column(Integer, primary_key=True); flat_no = Column(String, index=True); amenity = Column(String)
    day = Column(Date); slot = Column(String); fee = Column(Integer)
    __table_args__ = (UniqueConstraint("amenity", "day", "slot"),)


class NoticeIn(BaseModel): title: str = Field(min_length=3, max_length=80); body: str = Field(min_length=3, max_length=500)
class VisIn(BaseModel):
    flat_no: str = Field(min_length=3, max_length=12); name: str = Field(min_length=2, max_length=60)
    purpose: str = Field(default="Guest", max_length=30); code: str | None = Field(default=None, pattern=r"^\d{6}$")
    photo: str | None = Field(default=None, max_length=400000, pattern=r"^data:image/(jpeg|png);base64,[A-Za-z0-9+/=]+$")
class PreIn(BaseModel): name: str = Field(min_length=2, max_length=60)
class Decision(BaseModel): approve: bool
class Move(BaseModel): to: str = Field(pattern="^(inside|left)$")
class BookIn(BaseModel): amenity: str; day: date; slot: str
class RateIn(BaseModel): rating: int = Field(ge=1, le=5)


def vj(v): return {"id": v.id, "flat_no": v.flat_no, "name": v.name, "purpose": v.purpose, "status": v.status, "code": v.code, "at": v.created.isoformat(), "has_photo": bool(v.photo)}
def today0(): return datetime.combine(date.today(), dtime.min)  # ASSUMPTION: server time treated as local


@r.get("/notices")
def notices(u=Depends(auth()), db: Session = Depends(get_db)):
    return [{"id": n.id, "title": n.title, "body": n.body, "at": n.created.isoformat()} for n in db.query(Notice).order_by(Notice.id.desc()).limit(20)]

@r.post("/notices")
def post_notice(b: NoticeIn, u=Depends(auth("helpdesk", "committee")), db: Session = Depends(get_db)):
    db.add(Notice(title=b.title.strip(), body=b.body.strip())); db.commit(); return {"ok": True}


@r.post("/visitors")
def log_visitor(b: VisIn, u=Depends(auth("guard")), db: Session = Depends(get_db)):
    if not db.get(Flat, b.flat_no.upper()): raise HTTPException(422, "No such flat. Check the number, e.g. T12-0408")
    flat = b.flat_no.upper()
    if b.code:
        v = db.query(Visitor).filter_by(flat_no=flat, code=b.code, status="preapproved").first()
        if not v: raise HTTPException(400, "Guest code is not valid for this flat")
        v.status = "inside"; v.created = datetime.utcnow(); v.photo = b.photo or v.photo
    else:
        v = Visitor(flat_no=flat, name=b.name.strip(), purpose=b.purpose, status="pending", photo=b.photo); db.add(v)
    db.commit(); return vj(v)

@r.get("/visitors/gate")
def gate_list(u=Depends(auth("guard")), db: Session = Depends(get_db)):
    return [vj(v) for v in db.query(Visitor).filter(Visitor.created >= today0(), Visitor.status != "preapproved").order_by(Visitor.id.desc()).limit(60)]

@r.post("/visitors/{vid}/move")
def move(vid: int, b: Move, u=Depends(auth("guard")), db: Session = Depends(get_db)):
    v = db.get(Visitor, vid); ok = {"inside": "approved", "left": "inside"}[b.to]
    if not v or v.status != ok: raise HTTPException(409, "Not allowed for this visitor right now")
    v.status = b.to; db.commit(); return vj(v)

@r.get("/visitors")
def my_visitors(u=Depends(auth("resident")), db: Session = Depends(get_db)):
    q = db.query(Visitor).filter(Visitor.flat_no == u.flat_no, (Visitor.created >= today0()) | (Visitor.status == "preapproved"))
    return [vj(v) for v in q.order_by(Visitor.id.desc()).limit(50)]

@r.post("/visitors/preapprove")
def preapprove(b: PreIn, u=Depends(auth("resident")), db: Session = Depends(get_db)):
    v = Visitor(flat_no=u.flat_no, name=b.name.strip(), purpose="Pre-approved", status="preapproved", code=f"{secrets.randbelow(10**6):06d}")
    db.add(v); db.commit(); return vj(v)

@r.post("/visitors/{vid}/decision")
def decide(vid: int, b: Decision, u=Depends(auth("resident")), db: Session = Depends(get_db)):
    v = db.get(Visitor, vid)
    if not v or v.flat_no != u.flat_no or v.status != "pending": raise HTTPException(404, "Request not found or already answered")
    v.status = "approved" if b.approve else "denied"; db.commit(); return vj(v)


@r.get("/amenities")
def amenities(u=Depends(auth())): return AMEN

@r.get("/bookings")
def my_bookings(u=Depends(auth("resident")), db: Session = Depends(get_db)):
    q = db.query(Booking).filter(Booking.flat_no == u.flat_no, Booking.day >= date.today()).order_by(Booking.day)
    return [{"id": x.id, "amenity": x.amenity, "day": str(x.day), "slot": x.slot, "fee": x.fee} for x in q]

@r.get("/bookings/taken")
def taken(amenity: str, day: date, u=Depends(auth("resident")), db: Session = Depends(get_db)):
    return [x.slot for x in db.query(Booking).filter_by(amenity=amenity, day=day)]

@r.post("/bookings")
def book(b: BookIn, u=Depends(auth("resident")), db: Session = Depends(get_db)):
    a = AMEN.get(b.amenity)
    if not a or b.slot not in a["slots"]: raise HTTPException(422, "Choose an amenity and one of its slots")
    if not (date.today() <= b.day <= date.today() + timedelta(days=30)): raise HTTPException(422, "Bookings open for the next 30 days")
    if db.query(Booking).filter_by(amenity=b.amenity, day=b.day, slot=b.slot).first(): raise HTTPException(409, "That slot is taken. Pick another")
    if db.query(Booking).filter_by(flat_no=u.flat_no, day=b.day).count() >= 2: raise HTTPException(409, "Rule: at most 2 bookings per flat per day")
    db.add(Booking(flat_no=u.flat_no, amenity=b.amenity, day=b.day, slot=b.slot, fee=a["fee"])); db.commit(); return {"ok": True, "fee": a["fee"]}

@r.delete("/bookings/{bid}")
def cancel(bid: int, u=Depends(auth("resident")), db: Session = Depends(get_db)):
    x = db.get(Booking, bid)
    if not x or x.flat_no != u.flat_no: raise HTTPException(404, "Booking not found")
    db.delete(x); db.commit(); return {"ok": True}


@r.post("/complaints/{cid}/rate")
def rate(cid: int, b: RateIn, u=Depends(auth("resident")), db: Session = Depends(get_db)):
    c = db.get(Complaint, cid)
    if not c or c.flat_no != u.flat_no or c.status != "closed": raise HTTPException(409, "You can rate a complaint once it is closed")
    c.rating = b.rating; db.commit(); return cj(c)


def purge(db):
    """DPDP: delete visitor records (names, flats) after 90 days. Runs at startup; schedule daily in production."""
    db.query(Visitor).filter(Visitor.created < datetime.utcnow() - timedelta(days=90)).delete(); db.commit()



# ---- photos (stored as small JPEG data URLs; DPDP: visitor rows, photos included, purged after 90 days) ----
@r.get("/visitors/{vid}/photo")
def visitor_photo(vid: int, u=Depends(auth("guard", "resident")), db: Session = Depends(get_db)):
    v = db.get(Visitor, vid)
    if not v or not v.photo or (u.role == "resident" and v.flat_no != u.flat_no): raise HTTPException(404, "No photo")
    return {"photo": v.photo}

@r.get("/complaints/{cid}/photo")
def complaint_photo(cid: int, u=Depends(auth("resident", "helpdesk", "committee")), db: Session = Depends(get_db)):
    c = db.get(Complaint, cid)
    if not c or not c.photo or (u.role == "resident" and c.flat_no != u.flat_no): raise HTTPException(404, "No photo")
    return {"photo": c.photo}


# ---- reopen + receipts ----
@r.post("/complaints/{cid}/reopen")
def reopen(cid: int, u=Depends(auth("resident")), db: Session = Depends(get_db)):
    c = db.get(Complaint, cid)
    if not c or c.flat_no != u.flat_no or c.status != "closed": raise HTTPException(409, "Only your closed complaints can be reopened")
    c.status, c.closed_at, c.rating, c.reopens = "assigned", None, None, (c.reopens or 0) + 1
    c.due_by = datetime.utcnow() + timedelta(hours=SLA_H.get(c.urgency, 24)); db.commit(); return cj(c)

@r.get("/receipts/{pid}")
def receipt(pid: int, u=Depends(auth("resident", "helpdesk")), db: Session = Depends(get_db)):
    p = db.get(Payment, pid)
    if not p or (u.role == "resident" and p.flat_no != u.flat_no): raise HTTPException(404, "Receipt not found")
    return {"receipt_no": f"NIV-{p.id:06d}", "flat_no": p.flat_no, "amount": p.amount, "mode": p.source.replace("_", " "), "reference": p.ref, "date": p.at.isoformat()}


# ---- household: family and tenant members, each with their own login on the same flat ----
class Member(Base):
    __tablename__ = "members"; id = Column(Integer, primary_key=True); flat_no = Column(String, index=True); user_id = Column(Integer)
    name = Column(String); phone = Column(String); relation = Column(String)

class MemberIn(BaseModel):
    name: str = Field(min_length=2, max_length=60); phone: str = Field(pattern=r"^\d{10}$"); relation: str = Field(pattern="^(family|tenant)$")

@r.get("/members")
def members(u=Depends(auth("resident")), db: Session = Depends(get_db)):
    return [{"id": m.id, "name": m.name, "phone": m.phone, "relation": m.relation} for m in db.query(Member).filter_by(flat_no=u.flat_no)]

def _primary(u, db):
    if db.query(Member).filter_by(user_id=u.id).first(): raise HTTPException(403, "Only the primary resident can manage the household")

@r.post("/members")
def add_member(b: MemberIn, u=Depends(auth("resident")), db: Session = Depends(get_db)):
    _primary(u, db)
    if db.query(Member).filter_by(flat_no=u.flat_no).count() >= 6: raise HTTPException(409, "A flat can have up to 6 members")
    if db.query(User).filter_by(phone=b.phone).first(): raise HTTPException(409, "This number is already registered")
    nu = User(phone=b.phone, name=b.name.strip() + (" (tenant)" if b.relation == "tenant" else ""), role="resident", flat_no=u.flat_no); db.add(nu); db.flush()
    db.add(Member(flat_no=u.flat_no, user_id=nu.id, name=b.name.strip(), phone=b.phone, relation=b.relation)); db.commit(); return {"ok": True}

@r.delete("/members/{mid}")
def remove_member(mid: int, u=Depends(auth("resident")), db: Session = Depends(get_db)):
    _primary(u, db); m = db.get(Member, mid)
    if not m or m.flat_no != u.flat_no: raise HTTPException(404, "Member not found")
    db.query(User).filter_by(id=m.user_id).delete(); db.delete(m); db.commit(); return {"ok": True}
