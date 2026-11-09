import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parents[1]))
from app.logic import classify, match_rows, similar

F = {"T12-0408": {"due": 6370, "due_with_fee": 6500, "upi": "swati@oksbi"},
     "T21-1601": {"due": 5660, "due_with_fee": 5700, "upi": "aamir@okaxis"},
     "T07-1203": {"due": 0, "due_with_fee": 0, "upi": "n@ok"}}

def m(ref="", upi="", amount=0): return match_rows([{"ref": ref, "upi": upi, "amount": amount}], F)[0]

def test_exact_reference_auto(): assert m("NEFT T12-0408 NOV", "", 6370)["status"] == "auto"
def test_upi_auto(): assert m("", "aamir@okaxis", 5660)["flat_no"] == "T21-1601"
def test_partial_never_auto(): assert m("T21-1601", "", 3000)["status"] == "queue"
def test_no_dues_queue(): assert m("T07-1203", "", 7475)["status"] == "queue"
def test_amount_only_queue(): r = m("MAINT", "", 6370); assert r["status"] == "queue" and r["suggestions"] == ["T12-0408"]
def test_conflict_queue(): assert m("T12-0408", "aamir@okaxis", 6370)["status"] == "queue"
def test_duplicate_row():
    r = match_rows([{"ref": "T12-0408", "upi": "", "amount": 6370}] * 2, F); assert [x["status"] for x in r] == ["auto", "queue"]
def test_safety_overrides(): c = classify("Smell of gas in corridor, water pipe also leaking"); assert c["urgency"] == "critical" and c["safety"]
def test_lift_stuck(): assert classify("Lift stuck with people inside")["urgency"] == "critical"
def test_unsure_goes_to_triage(): assert classify("Please call me")["category"] == "needs_triage"
def test_category(): assert classify("water leak in bathroom ceiling")["category"] == "plumbing"
def test_duplicates(): assert similar("Lift not working in tower 7", "tower 7 lift is not working again")

def test_second_payment_same_flat_queued():
    r = match_rows([{"ref": "T12-0408 A", "upi": "", "amount": 6370}, {"ref": "T12-0408 B", "upi": "", "amount": 6370}], F)
    assert [x["status"] for x in r] == ["auto", "queue"]
