import { call, useLoad, State, inr, Complaints, Bank, Dash } from "./core.jsx";
import { useState, useEffect, useRef } from "react";

const L = {
  en: { home: "Home", pay: "Pay", help: "Help", guests: "Guests", book: "Book", due: "Maintenance due", payNow: "Pay now", report: "Report a problem", open: "Open complaints", paid: "All paid up", visitors: "Visitors today", notices: "Notices", out: "Sign out" },
  hi: { home: "होम", pay: "भुगतान", help: "शिकायत", guests: "मेहमान", book: "बुकिंग", due: "बकाया रखरखाव", payNow: "अभी भुगतान करें", report: "समस्या दर्ज करें", open: "खुली शिकायतें", paid: "सब चुकता", visitors: "आज के आगंतुक", notices: "सूचनाएं", out: "साइन आउट" },
  mr: { home: "मुख्यपृष्ठ", pay: "भरणा", help: "तक्रार", guests: "पाहुणे", book: "बुकिंग", due: "थकबाकी देखभाल शुल्क", payNow: "आता भरा", report: "समस्या नोंदवा", open: "खुल्या तक्रारी", paid: "सर्व भरले", visitors: "आजचे पाहुणे", notices: "सूचना", out: "साइन आउट" },
};
let T = L.en;
const tomorrow = () => new Date(Date.now() + 864e5).toISOString().slice(0, 10);

function useAct(after) {
  const [busy, setBusy] = useState(false), [msg, setMsg] = useState("");
  const run = async (f) => { setBusy(true); setMsg(""); try { await f(); after && (await after()); } catch (e) { setMsg(e.message); } setBusy(false); };
  return [run, busy, msg];
}
const Msg = ({ m }) => (m ? <p className="err" role="alert">{m}</p> : null);

function CountUp({ to, ms = 1400 }) {
  const ref = useRef(null), [n, setN] = useState(0);
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches || !("IntersectionObserver" in window)) { setN(to); return; }
    let raf;
    const io = new IntersectionObserver(([e]) => {
      if (!e.isIntersecting) return;
      io.disconnect();
      const t0 = performance.now();
      const tick = (t) => {
        const p = Math.min(1, (t - t0) / ms);
        setN(Math.round(to * (1 - Math.pow(1 - p, 3))));
        if (p < 1) raf = requestAnimationFrame(tick);
      };
      raf = requestAnimationFrame(tick);
    }, { threshold: 0.4 });
    io.observe(el);
    return () => { io.disconnect(); cancelAnimationFrame(raf); };
  }, [to, ms]);
  return <span ref={ref}>{n.toLocaleString("en-IN")}</span>;
}

/* ---------- landing + sign in ---------- */
function Landing({ onStart }) {
  const feats = [
    ["pay", "Pay maintenance in two taps", "See exactly what you owe, including late interest, and pay by UPI or card. Every receipt is kept in your ledger."],
    ["help", "Complaints that never vanish", "Describe the problem in a sentence. It reaches the right team, and you follow its status until it is closed."],
    ["guests", "Guests, approved from your phone", "The gate asks you before anyone comes in. Invite regulars ahead with a one-time code."],
    ["book", "Clubhouse and courts, booked", "Pick a slot, see the fee, and know straight away whether it is free."],
    ["bell", "Notices that reach everyone", "Water cuts and event timings go to every resident, not to 28 separate chat groups."],
    ["gate", "In your language", "Use Nivas in English, Hindi or Marathi, on any phone, with nothing to download."],
  ];
  const steps = [["Sign in", "Enter your registered mobile number and the one-time code we send."], ["See everything", "Your home screen shows dues, open complaints and today's visitors."], ["Act in two taps", "Pay, report a problem, allow a guest or book a slot from there."]];
  const staff = [["bank", "Help desk", "Upload a bank statement and clear payments match to flats on their own. Unclear ones wait in a queue for a person, and nothing is posted by guesswork."], ["gate", "Gate guards", "A tablet screen with very large buttons to log visitors, ask residents for approval and let people in."], ["chart", "Committee", "Collections, dues by age and complaint response times, in one view the committee can trust."]];
  return <div className="lp">
    <header className="lp-nav"><div className="lp-wrap lp-navin"><b className="logo">Nivas</b>
      <nav className="lp-links" aria-label="Sections"><a href="#features">Features</a><a href="#how">How it works</a><a href="#staff">For staff</a></nav>
      <button className="p" onClick={onStart}>Sign in</button></div></header>

    <section className="lp-wrap lp-hero">
      <div><h1>Your society, handled.</h1>
        <p className="lp-lead">One app for maintenance, complaints, visitors and bookings across every tower, with the committee looking at the same numbers you do.</p>
        <div className="lp-cta"><button className="p lg" onClick={onStart}>Sign in with your mobile number</button></div>
        <p className="mute lp-note">Sign-in uses a one-time code. No password to remember.</p></div>
      <div className="lp-mock" aria-hidden="true">
        <div className="stat primary"><span>Maintenance due</span><div className="big">₹6,370</div><small>T12-0408 · This month</small></div>
        <div className="item row"><span>Water leak in bathroom</span><Pill s="assigned" /></div>
        <div className="item row"><span>Courier at the gate</span><span className="lp-allow"><span className="pill ok">Allow</span><span className="pill">Deny</span></span></div>
        <div className="item row"><span>Clubhouse · 7 pm</span><Pill s="approved" /></div>
      </div>
    </section>

    <section className="lp-strip"><div className="lp-wrap lp-stats">
      {[[2400, "homes"], [28, "towers"], [180, "on-site staff"], [3, "languages"]].map(([n, l]) => <div key={l}><b><CountUp to={n} /></b><span>{l}</span></div>)}</div></section>

    <section id="features" className="lp-wrap lp-sec"><h2>Everything residents need, nothing they don't</h2>
      <p className="lp-sub">Built for people who open the app for a few seconds at a time.</p>
      <div className="lp-grid">{feats.map(([i, h, p]) => <div className="lp-feat" key={h}><span className="lp-ico"><Icon n={i} /></span><h3>{h}</h3><p className="mute">{p}</p></div>)}</div></section>

    <section id="how" className="lp-wrap lp-sec"><h2>Simple from the first tap</h2>
      <ol className="lp-steps">{steps.map(([h, p], i) => <li key={h}><span className="lp-num">{i + 1}</span><h3>{h}</h3><p className="mute">{p}</p></li>)}</ol></section>

    <section id="staff" className="lp-staff"><div className="lp-wrap lp-sec"><h2>Run the society with less paperwork</h2>
      <p className="lp-sub">The same app gives each team the screen it needs.</p>
      <div className="lp-grid3">{staff.map(([i, h, p]) => <div className="lp-feat" key={h}><span className="lp-ico"><Icon n={i} /></span><h3>{h}</h3><p className="mute">{p}</p></div>)}</div></div></section>

    <section className="lp-wrap lp-final"><h2>Ready to see your dues and complaints in one place?</h2><button className="p lg" onClick={onStart}>Sign in</button></section>

    <footer className="lp-foot"><div className="lp-wrap lp-footin"><b className="logo">Nivas</b>
      <p className="mute">Your details are used only to run your society. Visitor records are deleted after 90 days, as the DPDP Act 2023 requires. Demo project for a 2,400-flat township in Pune.</p></div></footer>
  </div>;
}

// sign in page
function Login({ onIn, back }) {
  const [phone, setPhone] = useState(""), [otp, setOtp] = useState(""), [demo, setDemo] = useState(null), [err, setErr] = useState(""), [busy, setBusy] = useState(false);
  const step2 = demo !== null;
  const go = async (f) => { setBusy(true); setErr(""); try { await f(); } catch (e) { setErr(e.message); } setBusy(false); };
  const submit = (e) => {
    e.preventDefault();
    if (busy) return;
    if (step2) otp.length === 6 && go(async () => onIn(await call("/auth/verify", null, "POST", { phone, otp })));
    else phone.length === 10 && go(async () => setDemo((await call("/auth/otp", null, "POST", { phone })).demo_otp || ""));
  };
  const reset = () => { setDemo(null); setOtp(""); setErr(""); };
  const quick = [["Resident", "9000000002"], ["Help desk", "9000000010"], ["Committee", "9000000020"], ["Gate guard", "9000000030"]];
  return <div className="auth">
    <aside className="auth-side">
      <b className="logo">Nivas</b>
      <div><h2>Everything for your society, in one place.</h2>
        <ul><li>Pay maintenance and keep every receipt</li><li>Track complaints until they are closed</li><li>Approve guests from your phone</li><li>Book the clubhouse and courts</li></ul></div>
      <p>Your details are used only to run your society. Visitor records are deleted after 90 days.</p>
    </aside>
    <section className="auth-main">
      <b className="logo auth-logo">Nivas</b>
      <form className="auth-card" onSubmit={submit} noValidate>
        <button type="button" className="link" onClick={step2 ? reset : back}>Back</button>
        <h1>{step2 ? "Enter your OTP" : "Welcome back"}</h1>
        <p className="mute">{step2 ? `We sent a 6-digit code to +91 ${phone}.` : "Sign in with the mobile number registered with your society."}</p>
        {!step2 ? <>
          <label htmlFor="phone">Mobile number</label>
          <div className="phone-field"><span>+91</span><input id="phone" type="tel" autoComplete="tel-national" inputMode="numeric" maxLength={10} value={phone} placeholder="98765 43210" autoFocus onChange={(e) => setPhone(e.target.value.replace(/\D/g, ""))} /></div>
          <button className="p lg" type="submit" disabled={busy || phone.length !== 10}>{busy ? "Sending…" : "Send OTP"}</button>
          <div className="demo"><span className="mute">Try a demo account</span><div className="chips">{quick.map(([n, p]) => <button type="button" key={p} className="chip" onClick={() => setPhone(p)}>{n}</button>)}</div></div>
        </> : <>
          {demo && <p className="demo-otp">Demo mode: your OTP is <b>{demo}</b></p>}
          <label htmlFor="otp">One-time password</label>
          <input id="otp" className="otp-input" type="text" autoComplete="one-time-code" inputMode="numeric" maxLength={6} value={otp} placeholder="------" autoFocus onChange={(e) => setOtp(e.target.value.replace(/\D/g, ""))} />
          <button className="p lg" type="submit" disabled={busy || otp.length !== 6}>{busy ? "Verifying…" : "Verify and continue"}</button>
          <button type="button" className="link" onClick={reset}>Use a different number</button>
        </>}
        <Msg m={err} />
      </form>
    </section>
  </div>;
}

/* ---------- shared bits ---------- */
const ICONS = {
  home: "M3 11l9-8 9 8v9a1 1 0 0 1-1 1h-5v-6H9v6H4a1 1 0 0 1-1-1z",
  pay: "M3 6h18v13H3zM3 10h18M7 15h3",
  help: "M4 5h16v11H9l-5 4z",
  guests: "M16 20v-1a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v1M10 11a3 3 0 1 0 0-6 3 3 0 0 0 0 6M20 20v-1a3 3 0 0 0-2-2.8",
  book: "M4 6h16v14H4zM4 10h16M8 3v4M16 3v4",
  bank: "M3 10l9-6 9 6M5 10v8M10 10v8M14 10v8M19 10v8M3 20h18",
  bell: "M6 16v-5a6 6 0 0 1 12 0v5l2 2H4zM10 21h4",
  chart: "M5 20V10M12 20V4M19 20v-7",
  gate: "M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z",
};
const ICON_OF = { Complaints: "help", "Bank matching": "bank", Notices: "bell", Dashboard: "chart", Gate: "gate" };
const Icon = ({ n }) => <svg className="ico" viewBox="0 0 24 24" aria-hidden="true"><path d={ICONS[n]} /></svg>;
const PILL = { approved: "ok", inside: "ok", closed: "ok", pending: "warn", waiting: "warn", open: "warn", assigned: "info", in_progress: "info", preapproved: "info", denied: "bad" };
const Pill = ({ s }) => <span className={"pill " + (PILL[s] || "")}>{s === "preapproved" ? "invited" : s.replace("_", " ")}</span>;
const Card = ({ title, action, children }) => <section className="card">{(title || action) && <div className="card-h"><h2>{title}</h2>{action}</div>}{children}</section>;
const Empty = ({ n, text }) => <div className="empty"><Icon n={n} /><span>{text}</span></div>;
const initials = (n) => n.split(/\s+/).filter(Boolean).slice(0, 2).map((w) => w[0]).join("").toUpperCase();
const ROLE = { resident: "Resident", helpdesk: "Help desk", committee: "Committee", guard: "Gate guard" };

/* ---------- resident pages ---------- */
function VisitorRow({ x, decide }) {
  return <div className="item"><div className="row"><span><b>{x.name}</b> <span className="mute">{x.purpose}</span></span><Pill s={x.status} /></div>
    {x.status === "pending" && <div className="row2"><button className="p" onClick={() => decide(x.id, true)}>Allow</button><button onClick={() => decide(x.id, false)}>Deny</button></div>}
    {x.status === "preapproved" && <p className="mute">Guest code <b className="code">{x.code}</b>. Share it with your guest.</p>}</div>;
}
function Notices({ tok, limit }) {
  const n = useLoad("/notices", tok);
  return <State s={n}>{n.data?.length === 0 && <Empty n="bell" text="No notices right now." />}{n.data?.slice(0, limit).map((x) => <div className="item" key={x.id}><b>{x.title}</b><p className="mute">{x.body}</p></div>)}</State>;
}

function Home({ tok, go }) {
  const h = useLoad("/home", tok), v = useLoad("/visitors", tok), [run, , msg] = useAct(() => v.load());
  const b = h.data?.bill, open = h.data?.complaints.filter((c) => c.status !== "closed") || [];
  const decide = (id, a) => run(() => call(`/visitors/${id}/decision`, tok, "POST", { approve: a }));
  return <State s={h}>{h.data && <>
    <div className="stats">
      <div className="stat primary"><span>{T.due}</span><div className="big">{b.total_due > 0 ? inr(b.total_due) : T.paid}</div><small>{h.data.flat_no} · {b.month}</small>{b.total_due > 0 && <button className="p" onClick={() => go("pay")}>{T.payNow}</button>}</div>
      <button className="stat" onClick={() => go("help")}><span>{T.open}</span><div className="big">{open.length}</div><small>{T.report}</small></button>
      <button className="stat" onClick={() => go("guests")}><span>{T.visitors}</span><div className="big">{v.data ? v.data.length : "–"}</div><small>Invite a guest</small></button>
    </div>
    <div className="quick"><button onClick={() => go("help")}><Icon n="help" />{T.report}</button><button onClick={() => go("guests")}><Icon n="guests" />Invite a guest</button><button onClick={() => go("book")}><Icon n="book" />Book an amenity</button></div>
    <div className="two">
      <Card title={T.open} action={<button className="link" onClick={() => go("help")}>View all</button>}>
        {open.length === 0 ? <Empty n="help" text="Nothing open. Report a problem and track it here." /> : open.slice(0, 3).map((c) => <div className="item row" key={c.id}><span>{c.text}</span><Pill s={c.status} /></div>)}</Card>
      <Card title={T.visitors}><State s={v}>{v.data?.length === 0 && <Empty n="guests" text="No visitors yet today." />}{v.data?.map((x) => <VisitorRow key={x.id} x={x} decide={decide} />)}<Msg m={msg} /></State></Card>
    </div>
    <Card title={T.notices}><Notices tok={tok} limit={2} /></Card></>}</State>;
}

function PayPage({ tok }) {
  const h = useLoad("/home", tok), [run, busy, msg] = useAct(() => h.load()), b = h.data?.bill;
  return <State s={h}>{b && <div className="two">
    <Card title={`${b.month} maintenance`}><div className="big">{b.total_due > 0 ? inr(b.total_due) : T.paid}</div><p className="mute">Total due</p>
      <div className="item row"><span>Bill (area × ₹6.50)</span><b>{inr(b.amount)}</b></div><div className="item row"><span>Paid so far</span><b>{inr(b.paid)}</b></div>
      <div className="item row"><span>Late interest {b.days_overdue > 0 && `(${b.days_overdue} days)`}</span><b>{inr(b.late_fee)}</b></div>
      {b.total_due > 0 && <button className="p lg wide" disabled={busy} onClick={() => run(() => call("/bills/pay", tok, "POST", {}))}>{T.payNow} · {inr(b.total_due)}</button>}<Msg m={msg} /><p className="mute">Test mode: no real money moves.</p></Card>
    <Card title="Receipts and ledger">{h.data.ledger.length === 0 && <Empty n="pay" text="No payments yet." />}
      {h.data.ledger.map((p, i) => <div className="item row" key={i}><span>{new Date(p.at).toLocaleDateString()} · {p.source.replace(/_/g, " ")}</span><b>{inr(p.amount)}</b></div>)}</Card></div>}</State>;
}

function HelpPage({ tok }) {
  const h = useLoad("/home", tok), [text, setText] = useState(""), [run, busy, msg] = useAct(() => h.load());
  return <><Card title={T.report}><label>What is wrong, and where?<textarea rows={3} maxLength={500} value={text} onChange={(e) => setText(e.target.value)} /></label>
    <button className="p lg" disabled={busy || text.trim().length < 5} onClick={() => run(async () => { await call("/complaints", tok, "POST", { text }); setText(""); })}>Send complaint</button><Msg m={msg} /></Card>
    <Card title="Your complaints"><State s={h}>{h.data?.complaints.length === 0 && <Empty n="help" text="No complaints yet. Describe a problem above and track it here." />}
      {h.data?.complaints.map((c) => <div className="item" key={c.id}><div className="row"><span>{c.text}</span><Pill s={c.status} /></div>
        <span className="mute">{c.category.replace("_", " ")} · with {c.assignee}{c.status !== "closed" && ` · reply due ${new Date(c.due_by + "Z").toLocaleString()}`}{c.duplicate_of ? " · already reported by a neighbour" : ""}</span>
        {c.status === "closed" && (c.rating ? <p className="mute">You rated this {c.rating}/5</p> : <p>Rate the fix: {[1, 2, 3, 4, 5].map((n) => <button key={n} className="star" aria-label={`${n} stars`} onClick={() => run(() => call(`/complaints/${c.id}/rate`, tok, "POST", { rating: n }))}>{n}</button>)}</p>)}</div>)}</State></Card></>;
}

function GuestsPage({ tok }) {
  const v = useLoad("/visitors", tok), [name, setName] = useState(""), [run, busy, msg] = useAct(() => v.load());
  return <div className="two"><Card title="Invite a guest"><label>Guest name<input value={name} maxLength={60} onChange={(e) => setName(e.target.value)} /></label>
    <button className="p lg" disabled={busy || name.trim().length < 2} onClick={() => run(async () => { await call("/visitors/preapprove", tok, "POST", { name }); setName(""); })}>Create guest code</button><Msg m={msg} /></Card>
    <Card title={T.visitors}><State s={v}>{v.data?.length === 0 && <Empty n="guests" text="No visitors or invites yet." />}{v.data?.map((x) => <VisitorRow key={x.id} x={x} decide={(id, a) => run(() => call(`/visitors/${id}/decision`, tok, "POST", { approve: a }))} />)}</State></Card></div>;
}

function BookPage({ tok }) {
  const am = useLoad("/amenities", tok), mine = useLoad("/bookings", tok), [a, setA] = useState("Clubhouse"), [day, setDay] = useState(tomorrow()), [slot, setSlot] = useState(""), [taken, setTaken] = useState([]);
  const [run, busy, msg] = useAct(async () => { await mine.load(); await loadTaken(); }), cfg = am.data?.[a];
  const loadTaken = () => call(`/bookings/taken?amenity=${encodeURIComponent(a)}&day=${day}`, tok).then(setTaken).catch(() => setTaken([]));
  useEffect(() => { setSlot(""); loadTaken(); }, [a, day]);
  return <State s={am}>{cfg && <div className="two"><Card title="Book an amenity"><label>Amenity<select value={a} onChange={(e) => setA(e.target.value)}>{Object.keys(am.data).map((k) => <option key={k}>{k}</option>)}</select></label>
    <label>Date<input type="date" value={day} min={new Date().toISOString().slice(0, 10)} onChange={(e) => setDay(e.target.value)} /></label>
    <div className="slots" role="group" aria-label="Slots">{cfg.slots.map((s) => <button key={s} disabled={taken.includes(s)} className={slot === s ? "on" : ""} onClick={() => setSlot(s)}>{s.replace("-", ":00 to ")}:00{taken.includes(s) ? " (taken)" : ""}</button>)}</div>
    <p className="mute">Fee {cfg.fee ? inr(cfg.fee) : "free"} · up to 2 bookings per flat per day.</p><button className="p lg" disabled={busy || !slot} onClick={() => run(() => call("/bookings", tok, "POST", { amenity: a, day, slot }))}>Confirm booking</button><Msg m={msg} /></Card>
    <Card title="Your bookings">{mine.data?.length === 0 && <Empty n="book" text="No upcoming bookings." />}{mine.data?.map((x) => <div className="item row" key={x.id}><span>{x.amenity} · {x.day} · {x.slot}</span><button onClick={() => run(() => call(`/bookings/${x.id}`, tok, "DELETE"))}>Cancel</button></div>)}</Card></div>}</State>;
}

/* ---------- gate (guard tablet) ---------- */
function Gate({ tok }) {
  const g = useLoad("/visitors/gate", tok), [f, setF] = useState({ flat_no: "", name: "", purpose: "Guest", code: "" }), [run, busy, msg] = useAct(() => g.load());
  useEffect(() => { const i = setInterval(g.load, 8000); return () => clearInterval(i); }, [g.load]);
  const set = (k) => (e) => setF({ ...f, [k]: e.target.value });
  const row = (x, to, label) => <div className="item row" key={x.id}><span><b>{x.flat_no}</b> {x.name}</span><button className="p xl" onClick={() => run(() => call(`/visitors/${x.id}/move`, tok, "POST", { to }))}>{label}</button></div>;
  const list = (st) => g.data?.filter((x) => x.status === st) || [];
  return <><Card title="Log a visitor"><div className="gate"><label>Flat<input value={f.flat_no} onChange={set("flat_no")} placeholder="T12-0408" /></label><label>Visitor name<input value={f.name} onChange={set("name")} /></label>
    <label>Purpose<select value={f.purpose} onChange={set("purpose")}>{["Guest", "Delivery", "Service", "Cab"].map((k) => <option key={k}>{k}</option>)}</select></label><label>Guest code (if they have one)<input inputMode="numeric" maxLength={6} value={f.code} onChange={set("code")} /></label></div>
    <button className="p xl wide" disabled={busy || !f.flat_no || (f.name.length < 2 && !f.code)} onClick={() => run(async () => { await call("/visitors", tok, "POST", { ...f, name: f.name || "Guest code", code: f.code || null }); setF({ flat_no: "", name: "", purpose: "Guest", code: "" }); })}>Ask resident to approve</button><Msg m={msg} /></Card>
    <State s={g}>{g.data?.length === 0 && <Card><Empty n="gate" text="No visitors logged today." /></Card>}
      <div className="two"><Card title="Waiting for resident">{list("pending").length === 0 && <Empty n="guests" text="Nobody waiting." />}{list("pending").map((x) => <div className="item row" key={x.id}><span><b>{x.flat_no}</b> {x.name}</span><Pill s="waiting" /></div>)}</Card>
        <Card title="Approved, let in">{list("approved").length === 0 && <Empty n="gate" text="Nobody to let in." />}{list("approved").map((x) => row(x, "inside", "Let in"))}</Card></div>
      <Card title="Inside now">{list("inside").length === 0 && <Empty n="home" text="No visitors inside." />}{list("inside").map((x) => row(x, "left", "Left"))}</Card></State>
    <p className="mute">Notice: visitor names and flat numbers are recorded for security and deleted after 90 days (DPDP Act 2023).</p></>;
}

/* ---------- staff ---------- */
function NoticesAdmin({ tok }) {
  const [f, setF] = useState({ title: "", body: "" }), [k, setK] = useState(0), [run, busy, msg] = useAct(() => setK(k + 1));
  return <div className="two"><Card title="Post a notice"><label>Title<input value={f.title} maxLength={80} onChange={(e) => setF({ ...f, title: e.target.value })} /></label><label>Message<textarea rows={3} maxLength={500} value={f.body} onChange={(e) => setF({ ...f, body: e.target.value })} /></label>
    <button className="p" disabled={busy || f.title.length < 3 || f.body.length < 3} onClick={() => run(async () => { await call("/notices", tok, "POST", f); setF({ title: "", body: "" }); })}>Publish notice</button><Msg m={msg} /></Card>
    <Card title="Published"><Notices key={k} tok={tok} /></Card></div>;
}

/* ---------- shell ---------- */
const NAV = { resident: ["home", "pay", "help", "guests", "book"], helpdesk: ["Complaints", "Bank matching", "Notices", "Dashboard"], committee: ["Dashboard", "Notices"], guard: ["Gate"] };

function Shell({ u, lang, setLang, onOut }) {
  const nav = NAV[u.role], [page, setPage] = useState(nav[0]), t = u.token, label = (k) => T[k] || k;
  const body = { home: <Home tok={t} go={setPage} />, pay: <PayPage tok={t} />, help: <HelpPage tok={t} />, guests: <GuestsPage tok={t} />, book: <BookPage tok={t} />, Complaints: <Card title="Open complaints"><Complaints tok={t} /></Card>, "Bank matching": <Card title="Bank statement matching"><Bank tok={t} /></Card>, Notices: u.role === "resident" ? <Card><Notices tok={t} /></Card> : <NoticesAdmin tok={t} />, Dashboard: <Card title="This month"><Dash tok={t} /></Card>, Gate: <Gate tok={t} /> }[page];
  const title = page === "home" ? `Hello, ${u.name.split(" ")[0]}` : label(page);
  const navBtn = (k) => <button key={k} className={page === k ? "on" : ""} onClick={() => setPage(k)} aria-current={page === k ? "page" : undefined}><Icon n={ICON_OF[k] || k} /><span>{label(k)}</span></button>;
  return <div className="app">
    <aside className="side"><b className="logo">Nivas</b><nav aria-label="Main">{nav.map(navBtn)}</nav>
      <div className="me"><span className="avatar">{initials(u.name)}</span><div><b>{u.name}</b><small>{ROLE[u.role]}{u.flat_no ? ` · ${u.flat_no}` : ""}</small></div></div>
      <button className="out" onClick={onOut}>{T.out}</button></aside>
    <div className="content"><header className="appbar"><b className="logo mlogo">Nivas</b><span className="grow" />
      <select className="lang" value={lang} onChange={(e) => setLang(e.target.value)} aria-label="Language"><option value="en">English</option><option value="hi">हिन्दी</option><option value="mr">मराठी</option></select><button className="mout" onClick={onOut}>{T.out}</button></header>
      <main className="page"><h1 className="ptitle">{title}</h1>{body}</main></div>
    <nav className="mtabs" aria-label="Main mobile">{nav.map(navBtn)}</nav></div>;
}

export default function App() {
  const [u, setU] = useState(() => { try { return JSON.parse(sessionStorage.getItem("nivas")); } catch { return null; } });
  const [view, setView] = useState("landing"), [lang, setLang] = useState("en");
  T = L[lang];
  const sign = (x) => { try { x ? sessionStorage.setItem("nivas", JSON.stringify(x)) : sessionStorage.removeItem("nivas"); } catch { /* storage unavailable */ } setU(x); setView("landing"); };
  if (u) return <Shell u={u} lang={lang} setLang={setLang} onOut={() => sign(null)} />;
  return view === "login" ? <Login onIn={sign} back={() => setView("landing")} /> : <Landing onStart={() => setView("login")} />;
}