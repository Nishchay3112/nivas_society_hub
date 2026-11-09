import os, sys, pathlib, tempfile
from datetime import date, timedelta
os.environ["DATABASE_URL"] = f"sqlite:///{tempfile.mkdtemp()}/test.db"
os.environ["JWT_SECRET"] = "test-secret"
os.environ["DEMO_MODE"] = "1"
ROOT = pathlib.Path(__file__).parents[1]; sys.path.insert(0, str(ROOT))
import pytest
from fastapi.testclient import TestClient
from app.main import app

HEADS = {}

@pytest.fixture(scope="module")
def c():
    with TestClient(app) as client: yield client

def h(c, phone):
    if phone not in HEADS:
        otp = c.post("/auth/otp", json={"phone": phone}).json()["demo_otp"]
        r = c.post("/auth/verify", json={"phone": phone, "otp": otp}); assert r.status_code == 200
        HEADS[phone] = {"Authorization": "Bearer " + r.json()["token"]}
    return HEADS[phone]

def test_no_token_is_401(c): assert c.get("/home").status_code == 401
def test_wrong_otp_rejected(c):
    c.post("/auth/otp", json={"phone": "9000000020"})
    assert c.post("/auth/verify", json={"phone": "9000000020", "otp": "000000"}).status_code == 400
def test_resident_blocked_from_staff_routes(c):
    assert c.get("/bank/queue", headers=h(c, "9000000003")).status_code == 403
    assert c.get("/committee/summary", headers=h(c, "9000000003")).status_code == 403
def test_pay_clears_dues_and_gives_receipt(c):
    H = h(c, "9000000002"); assert c.post("/bills/pay", json={}, headers=H).status_code == 200
    home = c.get("/home", headers=H).json(); assert home["bill"]["total_due"] == 0
    pid = home["ledger"][0]["id"]; assert c.get(f"/receipts/{pid}", headers=H).json()["flat_no"] == "T12-0408"
    assert c.get(f"/receipts/{pid}", headers=h(c, "9000000001")).status_code == 404
def test_safety_complaint_goes_to_duty_manager(c):
    r = c.post("/complaints", json={"text": "Smell of gas near the lift"}, headers=h(c, "9000000001")).json()
    assert r["assignee"] == "Duty manager" and r["urgency"] == "critical"
def test_reopen_flow(c):
    R, S = h(c, "9000000001"), h(c, "9000000010")
    cid = c.post("/complaints", json={"text": "Water leak in bathroom ceiling"}, headers=R).json()["id"]
    assert c.post(f"/complaints/{cid}/reopen", headers=R).status_code == 409      # not closed yet
    assert c.patch(f"/complaints/{cid}", json={"status": "closed"}, headers=S).status_code == 200
    assert c.post(f"/complaints/{cid}/reopen", headers=R).json()["status"] == "assigned"
def test_bank_upload_never_autoposts_partials(c):
    S = h(c, "9000000010"); csv = (ROOT / "sample_bank.csv").read_bytes()
    r = c.post("/bank/upload", files={"file": ("s.csv", csv, "text/csv")}, headers=S).json()
    assert r["rows"] == 5 and r["auto_posted"] + r["queued"] == 5
    assert any(x["amount"] == 3000 for x in c.get("/bank/queue", headers=S).json())
def test_booking_conflict(c):
    day = (date.today() + timedelta(days=1)).isoformat(); body = {"amenity": "Tennis court", "day": day, "slot": "06-07"}
    assert c.post("/bookings", json=body, headers=h(c, "9000000001")).status_code == 200
    assert c.post("/bookings", json=body, headers=h(c, "9000000003")).status_code == 409
def test_visitor_approval_flow(c):
    G, R = h(c, "9000000030"), h(c, "9000000002")
    vid = c.post("/visitors", json={"flat_no": "T12-0408", "name": "Plumber"}, headers=G).json()["id"]
    assert c.post(f"/visitors/{vid}/move", json={"to": "inside"}, headers=G).status_code == 409   # not approved yet
    assert c.post(f"/visitors/{vid}/decision", json={"approve": True}, headers=R).status_code == 200
    assert c.post(f"/visitors/{vid}/move", json={"to": "inside"}, headers=G).json()["status"] == "inside"
def test_household_member_gets_own_login(c):
    R = h(c, "9000000001")
    assert c.post("/members", json={"name": "Meera Kulkarni", "phone": "9111111111", "relation": "family"}, headers=R).status_code == 200
    assert h(c, "9111111111") and c.get("/home", headers=h(c, "9111111111")).json()["flat_no"] == "T07-1203"
