"""Pure logic (no DB): payment matching and complaint triage. Unit-tested."""
import re

SAFETY = ["fire", "gas", "lift stuck", "stuck in lift", "shock", "smoke", "short circuit"]
CATS = {
    "plumbing": ["leak", "water", "tap", "pipe", "drain", "seepage"],
    "electrical": ["light", "power", "electric", "switch", "wiring"],
    "lift": ["lift", "elevator"],
    "housekeeping": ["garbage", "clean", "dust", "sweep"],
    "security": ["guard", "gate", "stranger", "theft"],
    "parking": ["parking", "vehicle", "car "],
}
HIGH = ["no water", "flood", "blackout", "not working", "overflow"]
CONF_MIN = 0.6  # below this -> "needs_triage", never guessed


def classify(text: str) -> dict:
    t = " " + text.lower() + " "
    safety = any(re.search(r"\b" + re.escape(w) + r"\b", t) for w in SAFETY)  # rule, beats model
    scores = {c: sum(k in t for k in ks) for c, ks in CATS.items()}
    cat, best = max(scores.items(), key=lambda x: x[1])
    conf = min(1.0, 0.5 + 0.25 * best) if best else 0.0
    if conf < CONF_MIN:
        cat = "needs_triage"
    urgency = "critical" if safety else "high" if any(w in t for w in HIGH) else "normal"
    return {"category": cat, "urgency": urgency, "confidence": round(conf, 2), "safety": safety}


def similar(a: str, b: str, th: float = 0.4) -> bool:
    x, y = set(re.findall(r"\w{3,}", a.lower())), set(re.findall(r"\w{3,}", b.lower()))
    return bool(x and y) and len(x & y) / len(x | y) >= th


def _n(s): return re.sub(r"[^A-Z0-9]", "", (s or "").upper())


def match_rows(rows, flats):
    """rows: [{ref,upi,amount}]; flats: {flat_no: {due, due_with_fee, upi}}.
    Returns one result per row: status 'auto' only when ONE flat is identified by
    reference/UPI and the amount equals its dues. Everything else -> 'queue'."""
    seen, posted, out = set(), set(), []
    for r in rows:
        ref, upi, amt = _n(r.get("ref")), (r.get("upi") or "").lower(), r["amount"]
        by_ref = {f for f in flats if _n(f) in ref}
        by_upi = {f for f, d in flats.items() if upi and d["upi"] and d["upi"].lower() == upi}
        cands = by_ref | by_upi
        key = (ref, amt)
        res = {"status": "queue", "flat_no": None, "note": "", "suggestions": []}
        if key in seen and ref:
            res["note"] = "Duplicate reference in this file"
        elif len(cands) == 1:
            f = next(iter(cands)); d = flats[f]
            if d["due"] <= 0:
                res.update(flat_no=f, note="Flat has no dues (possible double payment)")
            elif f in posted:
                res.update(flat_no=f, note="Flat already matched earlier in this file")
            elif abs(amt - d["due"]) <= 1 or abs(amt - d["due_with_fee"]) <= 1:
                posted.add(f)
                res.update(status="auto", flat_no=f, note="Matched by " + ("reference+UPI" if f in by_ref and f in by_upi else "reference" if f in by_ref else "UPI") + " and amount")
            else:
                res.update(flat_no=f, note=f"Partial/mismatch: paid {amt}, due {d['due']}")
        elif len(cands) > 1:
            res["note"] = "Reference and UPI point to different flats"
        else:
            res["suggestions"] = [f for f, d in flats.items() if d["due"] == amt][:5]
            res["note"] = "No reference or UPI match; amount-only suggestions"
        seen.add(key)
        out.append(res)
    return out
