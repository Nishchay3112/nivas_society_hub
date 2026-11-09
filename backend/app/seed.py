"""Synthetic data only. 3 given sample flats + ~2,380 generated flats (28 towers). Rate ₹6.50/sq ft."""
import random
from datetime import date, datetime, timedelta
from .main import User, Flat, Bill, Payment, Complaint, TEAM, SLA_H
from .logic import classify

RATE = 6.5
TEXTS = ["Lift not working in our tower", "Water leak in bathroom ceiling", "Corridor light is not working", "Garbage not collected today",
         "Stranger loitering near gate", "Car parked in my slot", "Tap leaking in kitchen", "Smell of gas near stairwell", "Please call me"]


def seed(db):
    if db.query(Flat).count(): return
    rnd = random.Random(7); today = date.today(); month = today.strftime("%b %Y")
    given = {"T07-1203": (1150, 7475, 0, "neeraj.k@okicici", "Neeraj Kulkarni", "9000000001"), "T12-0408": (980, 0, 47, "swati.j@oksbi", "Swati Joshi (tenant)", "9000000002"),
             "T21-1601": (1640, 5000, 18, "aamir@okaxis", "Aamir Shaikh", "9000000003")}
    flats = {}
    for t in range(1, 29):
        for fl in range(1, 18):
            for k in range(1, 6): flats[f"T{t:02d}-{fl:02d}{k:02d}"] = rnd.choice([650, 980, 1150, 1320, 1640])
    for no, g in given.items(): flats[no] = g[0]
    for no, area in flats.items():
        amt = round(area * RATE)
        g = given.get(no)
        if g: paid, over = g[1], g[2]
        else:
            r = rnd.random(); paid = amt if r < .78 else (amt // 2 if r < .83 else 0); over = 0 if paid == amt else rnd.choice([3, 12, 25, 40, 55, 75])
        if no in given and no == "T07-1203": paid = amt
        db.add(Flat(no=no, tower=no[:3], area=area, upi=g[3] if g else f"{no.lower().replace('-', '')}@okbank"))
        db.add(Bill(flat_no=no, month=month, amount=amt, paid=paid, due_date=today - timedelta(days=over) if paid < amt else today + timedelta(days=5)))
        if paid: db.add(Payment(flat_no=no, amount=paid, source="bank_auto", ref="SEED"))
    for no, g in given.items(): db.add(User(phone=g[5], name=g[4], role="resident", flat_no=no))
    db.add(User(phone="9000000010", name="Help desk (Priya)", role="helpdesk")); db.add(User(phone="9000000020", name="Committee (Mr. Deshpande)", role="committee"))
    db.flush()
    c = Complaint(flat_no="T12-0408", text="Water leak in bathroom ceiling", **classify("Water leak in bathroom ceiling"), status="assigned", assignee=TEAM["plumbing"],
                  created=datetime.utcnow() - timedelta(hours=30), due_by=datetime.utcnow() - timedelta(hours=6)); db.add(c)
    keys = list(flats)
    for i in range(40):
        txt, no = rnd.choice(TEXTS), rnd.choice(keys); r = classify(txt); made = datetime.utcnow() - timedelta(hours=rnd.randint(2, 200))
        done = rnd.random() < .6
        db.add(Complaint(flat_no=no, text=txt, **r, reopens=int(done and rnd.random() < .1), status="closed" if done else "assigned", assignee="Duty manager" if r["safety"] else TEAM[r["category"]],
                         created=made, due_by=made + timedelta(hours=SLA_H[r["urgency"]]), closed_at=made + timedelta(hours=rnd.randint(1, 40)) if done else None))
    seed_extra(db)
    db.commit()


def seed_extra(db):
    from .extra import Notice, Visitor, Booking
    db.add(User(phone="9000000030", name="Gate guard (Ramesh)", role="guard"))
    db.add(Notice(title="Water supply off on Tuesday", body="Tanks will be cleaned between 10 am and 1 pm. Please store water in advance."))
    db.add(Notice(title="Clubhouse timings during Diwali", body="The clubhouse stays open until 11 pm from 10 to 14 November."))
    db.add(Visitor(flat_no="T12-0408", name="Courier (Amazon)", purpose="Delivery", status="pending"))
    db.add(Booking(flat_no="T21-1601", amenity="Clubhouse", day=date.today() + timedelta(days=2), slot="19-22", fee=500))
