import { useState, useEffect, useCallback } from "react";
const API = import.meta.env.VITE_API_URL || "http://localhost:8000";
export const inr = (n) => "₹" + Number(n).toLocaleString("en-IN");
export async function call(path, tok, method = "GET", body, form) {
  const r = await fetch(API + path, { method, headers: { ...(tok && { Authorization: "Bearer " + tok }), ...(body && { "Content-Type": "application/json" }) }, body: form || (body && JSON.stringify(body)) }).catch(() => { throw new Error("Can't reach the server. Check your connection and retry."); });
  const j = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(typeof j.detail === "string" ? j.detail : "Please check the details and try again.");
  return j;
}
export function useLoad(path, tok) {
  const [s, set] = useState({ data: null, err: "", loading: true });
  const load = useCallback(() => { set((x) => ({ ...x, loading: true })); call(path, tok).then((data) => set({ data, err: "", loading: false })).catch((e) => set({ data: null, err: e.message, loading: false })); }, [path, tok]);
  useEffect(load, [load]); return { ...s, load };
}
export const State = ({ s, children }) => s.loading && !s.data ? <p className="mute">Loading…</p> : s.err ? <p className="err">{s.err} <button onClick={s.load}>Retry</button></p> : children;

export function Complaints({ tok }) {
  const s = useLoad("/complaints", tok), [e, setE] = useState("");
  const patch = (id, b) => call("/complaints/" + id, tok, "PATCH", b).then(s.load).catch((x) => setE(x.message));
  return <State s={s}>{e && <p className="err">{e}</p>}{s.data?.length === 0 && <p className="mute">No open complaints.</p>}
    {s.data?.map((c) => <div className="item" key={c.id}><div className="row"><b className={c.urgency === "critical" ? "crit" : ""}>{c.urgency === "critical" ? "Critical: " : ""}{c.text}</b></div>
      <p className="mute" style={{ margin: "2px 0 8px" }}>{c.flat_no} · {c.assignee}{c.safety ? " · safety rule: escalated to duty manager" : ""}{c.duplicate_of ? ` · linked to #${c.duplicate_of}` : ""}{c.category === "needs_triage" ? " · AI unsure, please categorise" : ` · AI ${Math.round(c.confidence * 100)}% sure`}</p>
      <div className="row"><select aria-label="Category" value={c.category} onChange={(x) => patch(c.id, { category: x.target.value })}>{["plumbing", "electrical", "lift", "housekeeping", "security", "parking", "needs_triage"].map((k) => <option key={k} value={k}>{k.replace("_", " ")}</option>)}</select>
        <select aria-label="Status" value={c.status} onChange={(x) => patch(c.id, { status: x.target.value })}>{["open", "assigned", "in_progress", "closed"].map((k) => <option key={k} value={k}>{k.replace("_", " ")}</option>)}</select></div></div>)}</State>;
}

export function Bank({ tok }) {
  const q = useLoad("/bank/queue", tok), [r, setR] = useState(""), [e, setE] = useState(""), [pick, setPick] = useState({});
  const upload = async (ev) => { const f = ev.target.files[0]; if (!f) return; const fd = new FormData(); fd.append("file", f); setE(""); try { const j = await call("/bank/upload", tok, "POST", null, fd); setR(`${j.rows} rows: ${j.auto_posted} posted automatically, ${j.queued} need your review.`); q.load(); } catch (x) { setE(x.message); } };
  const resolve = (id, path, b) => call(`/bank/queue/${id}/${path}`, tok, "POST", b).then(q.load).catch((x) => setE(x.message));
  return <><p className="mute">Upload a bank statement CSV (date, reference, upi, amount). Clear matches post themselves; unclear ones wait here and are never posted without you.</p>
    <input type="file" accept=".csv" onChange={upload} aria-label="Bank statement CSV" />{r && <p><b>{r}</b></p>}{e && <p className="err" role="alert">{e}</p>}
    <h2>Accounts queue</h2><State s={q}>{q.data?.length === 0 && <p className="mute">Queue is clear. Upload a statement to begin.</p>}
      {q.data?.map((x) => <div className="item" key={x.id}><div className="row"><b>{inr(x.amount)}</b><span className="mute">{x.date}</span></div><p className="mute" style={{ margin: "2px 0 8px" }}>{x.ref || "no reference"} {x.upi && "· " + x.upi}<br />{x.note}</p>
        <div className="row"><input placeholder="Flat, e.g. T12-0408" value={pick[x.id] ?? x.flat_no ?? ""} onChange={(v) => setPick({ ...pick, [x.id]: v.target.value })} aria-label="Flat number" /><button className="p" onClick={() => resolve(x.id, "assign", { flat_no: pick[x.id] ?? x.flat_no ?? "" })}>Post</button><button onClick={() => resolve(x.id, "reject")}>Reject</button></div>
        {x.suggestions.length > 0 && <p className="mute">Flats with this exact amount due: {x.suggestions.map((f) => <button key={f} onClick={() => setPick({ ...pick, [x.id]: f })} style={{ minHeight: 32, margin: 2 }}>{f}</button>)}</p>}</div>)}</State></>;
}

export function Dash({ tok }) {
  const s = useLoad("/committee/summary", tok), d = s.data, tot = d ? Object.values(d.ageing).reduce((a, b) => a + b, 0) : 0;
  return <State s={s}>{d && <><h2>Collected this month</h2><div className="big">{d.collection_pct}%</div><div className="bar"><i style={{ width: d.collection_pct + "%" }} /></div><p className="mute">{inr(d.collected)} of {inr(d.billed)} billed</p>
    <h2>Unpaid dues by age</h2>{Object.entries(d.ageing).map(([k, v]) => <div className="item row" key={k}><span>{k} days overdue</span><b>{inr(v)}</b></div>)}<p className="mute">{inr(tot)} outstanding in total</p>
    <h2>Complaints</h2><div className="grid"><div><div className="big">{d.open_complaints}</div><span className="mute">open</span></div><div><div className="big">{d.avg_resolution_hours ?? "–"}</div><span className="mute">avg hours to close</span></div><div><div className={"big " + (d.overdue_sla ? "crit" : "")}>{d.overdue_sla}</div><span className="mute">past response time</span></div><div><div className="big">{d.accounts_queue}</div><span className="mute">payments awaiting review</span></div></div></>}</State>;
}

