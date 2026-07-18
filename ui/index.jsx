import { useState, useRef, useEffect } from "react"

const MS = {
  empiricist: { label:"Empiriste", desc:"Données · mesure · falsifiabilité", icon:"ti-test-pipe",
    sys:`Tu es l'Agent A — Empiriste. Tu valides uniquement ce qui est observable et falsifiable. Tu cites des preuves concrètes. Maintiens ta position si les données la soutiennent. 4-5 phrases dans la langue de l'hypothèse.` },
  rationalist: { label:"Rationaliste", desc:"Principes · cohérence · déduction", icon:"ti-math-function",
    sys:`Tu es l'Agent B — Rationaliste. Tu pars des principes premiers et de la cohérence logique. Tu contestes les arguments sans fondation théorique. Maintiens ta position si la logique la soutient. 4-5 phrases dans la langue de l'hypothèse.` },
  skeptic:    { label:"Sceptique",    desc:"Doute · charge de la preuve", icon:"ti-help-circle",
    sys:`Tu es un agent Sceptique. Tu appliques le doute méthodique à toute affirmation. Tu identifies qui porte la charge de la preuve. Tu repères les biais et sophismes. 4-5 phrases dans la langue de l'hypothèse.` },
  pragmatist: { label:"Pragmatiste",  desc:"Conséquences · utilité pratique", icon:"ti-route",
    sys:`Tu es un agent Pragmatiste. Tu évalues les idées par leurs conséquences pratiques. Tu rejettes les débats abstraits sans application réelle. Tu cherches le consensus opérationnel. 4-5 phrases dans la langue de l'hypothèse.` },
}

const JUDGE = `Tu es un juge impartial d'un débat académique. Réponds UNIQUEMENT en JSON valide, sans markdown :
{"verdict":"CONFIRMED|NUANCED|REJECTED|PENDING","confidence":0.XX,"agreement":["accord 1"],"disagreement":["désaccord 1"],"rationale":"Justification en une phrase."}
CONFIRMED=soutenue ; NUANCED=partielle (disagreement non vide) ; REJECTED=réfutée ; PENDING=insuffisant. Confidence 0.50-0.95.`

const VC = {
  CONFIRMED: { lbl:"Confirmé",   icon:"ti-circle-check", cls:"confirmed" },
  NUANCED:   { lbl:"Nuancé",     icon:"ti-adjustments",  cls:"nuanced"   },
  REJECTED:  { lbl:"Rejeté",     icon:"ti-circle-x",     cls:"rejected"  },
  PENDING:   { lbl:"En attente", icon:"ti-clock",         cls:"pending"   },
}

const S = `
  *{box-sizing:border-box;margin:0;padding:0}
  .app{font-family:var(--font-sans);border:0.5px solid var(--border);border-radius:12px;overflow:hidden}
  .hdr{display:flex;align-items:center;gap:10px;padding:12px 20px;border-bottom:0.5px solid var(--border);background:var(--surface-1)}
  .brand{font-size:16px;font-weight:500;color:var(--text-primary)}
  .sub{font-size:12px;color:var(--text-secondary)}
  .nav{display:flex;gap:8px;margin-left:auto;align-items:center}
  .nbtn{display:inline-flex;align-items:center;gap:5px;padding:5px 12px;border:0.5px solid var(--border-strong);border-radius:var(--radius);background:none;color:var(--text-secondary);font-size:12px;font-weight:500;cursor:pointer;text-decoration:none}
  .nbtn.act{background:var(--bg-accent);border-color:var(--border-accent);color:var(--text-accent)}
  .compose{max-width:640px;margin:0 auto;padding:24px 20px;display:flex;flex-direction:column;gap:18px}
  .field-lbl{display:block;font-size:13px;font-weight:500;color:var(--text-primary);margin-bottom:8px}
  textarea{width:100%;padding:12px 14px;font-size:14px;border:0.5px solid var(--border-strong);border-radius:var(--radius);background:var(--surface-1);color:var(--text-primary);font-family:var(--font-sans);resize:vertical;outline:none;line-height:1.6}
  textarea:focus{border-color:var(--border-accent)}
  .agents{display:grid;grid-template-columns:1fr 1fr;gap:16px}
  .acol{display:flex;flex-direction:column;gap:8px}
  .ahdr{display:flex;align-items:center;gap:8px;padding-bottom:4px}
  .av{width:28px;height:28px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:500;flex-shrink:0}
  .av-a{background:var(--bg-accent);border:0.5px solid var(--border-accent);color:var(--text-accent)}
  .av-b{background:var(--bg-warning);border:0.5px solid var(--border-warning);color:var(--text-warning)}
  .anm{font-size:13px;font-weight:500;color:var(--text-primary)}
  .mc{display:flex;align-items:center;gap:9px;padding:9px 11px;border:0.5px solid var(--border);border-radius:var(--radius);background:var(--surface-1);cursor:pointer;text-align:left;width:100%;transition:all .12s}
  .mc:hover:not(:disabled){border-color:var(--border-strong);background:var(--surface-2)}
  .mc:disabled{opacity:.3;cursor:not-allowed}
  .mc.sa{background:var(--bg-accent);border-color:var(--border-accent)}
  .mc.sb{background:var(--bg-warning);border-color:var(--border-warning)}
  .mc.sa i,.mc.sa .mn,.mc.sa .md{color:var(--text-accent)}
  .mc.sb i,.mc.sb .mn,.mc.sb .md{color:var(--text-warning)}
  .mc i{font-size:16px;color:var(--text-secondary);flex-shrink:0}
  .mn{font-size:12px;font-weight:500;color:var(--text-primary);margin-bottom:1px}
  .md{font-size:11px;color:var(--text-secondary)}
  .opts{display:flex;align-items:center;gap:9px;padding:10px 14px;background:var(--surface-1);border-radius:var(--radius);border:0.5px solid var(--border);flex-wrap:wrap}
  .ol{font-size:12px;color:var(--text-secondary);font-weight:500}
  .rb{width:30px;height:30px;border-radius:var(--radius);border:0.5px solid var(--border-strong);background:transparent;color:var(--text-secondary);font-size:13px;font-weight:500;cursor:pointer}
  .rb.rs{border-color:var(--border-accent);background:var(--bg-accent);color:var(--text-accent)}
  .on{font-size:11px;color:var(--text-muted);margin-right:auto}
  .ctog{display:flex;align-items:center;gap:4px;font-size:12px;color:var(--text-secondary);background:none;border:none;cursor:pointer;padding:4px}
  .carea{padding:12px 14px;background:var(--surface-1);border-radius:var(--radius);border:0.5px solid var(--border);display:flex;flex-direction:column;gap:8px}
  .dz{border:0.5px dashed var(--border-strong);border-radius:var(--radius);padding:14px;text-align:center;cursor:pointer;transition:all .15s}
  .dz.dov,.dz:hover{border-color:var(--border-accent)}
  .dz i{display:block;font-size:22px;color:var(--text-muted);margin-bottom:6px}
  .dz span{font-size:12px;color:var(--text-secondary)}
  .dz.hf i{color:var(--text-success)}.dz.hf span{color:var(--text-success)}
  .cfr{display:flex;justify-content:space-between;align-items:center}
  .cnote{font-size:11px;color:var(--text-success)}.crm{font-size:11px;color:var(--text-secondary);background:none;border:none;cursor:pointer}
  .warn{display:flex;align-items:center;gap:8px;padding:9px 12px;background:var(--bg-warning);border-radius:var(--radius);border:0.5px solid var(--border-warning);font-size:12px;color:var(--text-warning)}
  .lbtn{width:100%;padding:13px;border:0.5px solid var(--border-accent);border-radius:var(--radius);background:var(--bg-accent);color:var(--text-accent);font-size:14px;font-weight:500;cursor:pointer;display:flex;align-items:center;justify-content:center;gap:8px}
  .lbtn:hover:not(:disabled){background:var(--fill-accent);color:var(--on-accent)}
  .lbtn:disabled{background:transparent;border-color:var(--border);color:var(--text-muted);cursor:not-allowed}
  .qbar{display:flex;align-items:center;gap:10px;padding:10px 20px;border-bottom:0.5px solid var(--border);background:var(--surface-1)}
  .qtxt{font-size:13px;color:var(--text-primary);font-style:italic;flex:1}
  .qtags{display:flex;gap:6px;align-items:center;flex-shrink:0;font-size:11px}
  .tx{padding:20px;display:flex;flex-direction:column;gap:14px}
  .tn{display:flex;flex-direction:column;gap:5px}
  .tn-a{align-items:flex-start}.tn-b{align-items:flex-end}
  .thd{display:flex;align-items:center;gap:7px}.thd-r{flex-direction:row-reverse}
  .tla{font-size:11px;font-weight:500;color:var(--text-accent)}.tlb{font-size:11px;font-weight:500;color:var(--text-warning)}
  .trn{font-size:11px;color:var(--text-muted)}
  .bb{max-width:78%;padding:11px 15px;font-size:13px;line-height:1.7;color:var(--text-primary)}
  .bb-a{background:var(--bg-accent);border:0.5px solid var(--border-accent);border-radius:2px 12px 12px 12px}
  .bb-b{background:var(--bg-warning);border:0.5px solid var(--border-warning);border-radius:12px 2px 12px 12px}
  @keyframes fp{0%,100%{opacity:1}50%{opacity:.4}}
  .ld{display:flex;align-items:center;gap:8px;color:var(--text-secondary);font-size:12px;padding:6px 0;animation:fp 1.5s infinite}
  .eb{padding:11px 14px;background:var(--bg-danger);border:0.5px solid var(--border-danger);border-radius:var(--radius);font-size:12px;color:var(--text-danger)}
  .vwrap{padding:16px 20px;border-top:0.5px solid var(--border)}
  .vc{border-radius:12px;padding:16px 18px}
  .vc.confirmed{background:var(--bg-success);border:0.5px solid var(--border-success)}
  .vc.nuanced{background:var(--bg-warning);border:0.5px solid var(--border-warning)}
  .vc.rejected{background:var(--bg-danger);border:0.5px solid var(--border-danger)}
  .vc.pending{background:var(--bg-pro);border:0.5px solid var(--border-pro)}
  .vh{display:flex;align-items:center;gap:12px;margin-bottom:10px}
  .vi{font-size:22px}
  .confirmed .vi,.confirmed .vn{color:var(--text-success)}
  .nuanced .vi,.nuanced .vn{color:var(--text-warning)}
  .rejected .vi,.rejected .vn{color:var(--text-danger)}
  .pending .vi,.pending .vn{color:var(--text-pro)}
  .vn{font-size:18px;font-weight:500}
  .vpc{margin-left:auto;text-align:right}
  .vpn{display:block;font-size:17px;font-weight:500}
  .confirmed .vpn{color:var(--text-success)}.nuanced .vpn{color:var(--text-warning)}
  .rejected .vpn{color:var(--text-danger)}.pending .vpn{color:var(--text-pro)}
  .vpl{font-size:11px;color:var(--text-secondary)}
  .cbar{height:4px;background:var(--border-strong);border-radius:2px;overflow:hidden;margin-bottom:12px}
  .cf{height:100%;border-radius:2px;transition:width .8s}
  .confirmed .cf{background:var(--text-success)}.nuanced .cf{background:var(--text-warning)}
  .rejected .cf{background:var(--text-danger)}.pending .cf{background:var(--text-pro)}
  .vr{font-size:13px;color:var(--text-primary);line-height:1.65;margin-bottom:12px;font-style:italic}
  .vls{display:flex;gap:16px;margin-bottom:12px;flex-wrap:wrap}
  .vl{flex:1;min-width:130px}.vll{font-size:11px;font-weight:500;color:var(--text-secondary);margin-bottom:5px}
  .vli{font-size:12px;color:var(--text-primary);padding:2px 0 2px 4px}
  .va{display:flex;gap:8px;align-items:center;flex-wrap:wrap;padding-top:12px;border-top:0.5px solid var(--border);margin-top:4px}
  .ba{display:inline-flex;align-items:center;gap:5px;padding:7px 14px;border:0.5px solid var(--border-accent);border-radius:var(--radius);background:var(--bg-accent);color:var(--text-accent);font-size:12px;font-weight:500;cursor:pointer}
  .bg{display:inline-flex;align-items:center;gap:5px;padding:6px 12px;border:0.5px solid var(--border-strong);border-radius:var(--radius);background:none;color:var(--text-secondary);font-size:12px;cursor:pointer}
  .dn{font-size:11px;color:var(--text-muted);margin-left:auto}
  .vb{display:inline-flex;align-items:center;gap:4px;padding:3px 9px;border-radius:var(--radius);font-size:11px;font-weight:500;white-space:nowrap}
  .vb.confirmed{background:var(--bg-success);border:0.5px solid var(--border-success);color:var(--text-success)}
  .vb.nuanced{background:var(--bg-warning);border:0.5px solid var(--border-warning);color:var(--text-warning)}
  .vb.rejected{background:var(--bg-danger);border:0.5px solid var(--border-danger);color:var(--text-danger)}
  .vb.pending{background:var(--bg-pro);border:0.5px solid var(--border-pro);color:var(--text-pro)}
  .hi{padding:20px}.he{text-align:center;padding:60px 20px}
  .he i{font-size:40px;color:var(--text-muted);display:block;margin-bottom:14px}
  .he-t{font-size:14px;font-weight:500;color:var(--text-primary);margin-bottom:6px}
  .he-s{font-size:13px;color:var(--text-secondary);margin-bottom:20px}
  .hl{display:flex;flex-direction:column;gap:8px}
  .sc{display:flex;gap:14px;padding:14px 16px;background:var(--surface-2);border:0.5px solid var(--border);border-radius:var(--radius);cursor:pointer;text-align:left;align-items:center;width:100%}
  .sc:hover{border-color:var(--border-strong)}.si{flex:1}
  .sh{font-size:13px;color:var(--text-primary);font-style:italic;margin-bottom:5px;line-height:1.4}
  .sm{display:flex;align-items:center;gap:8px;font-size:11px;color:var(--text-secondary)}
  .stt{margin-left:auto;font-size:11px;color:var(--text-muted)}
  .dhdr{display:flex;align-items:center;gap:10px;padding:10px 20px;border-bottom:0.5px solid var(--border);background:var(--surface-1)}
  .bk{display:flex;align-items:center;gap:5px;font-size:12px;color:var(--text-secondary);background:none;border:none;cursor:pointer;padding:4px;flex-shrink:0}
  .dq{font-size:12px;color:var(--text-primary);font-style:italic;flex:1}
`

async function ask(sys, msgs, max = 400) {
  const r = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ model: "claude-sonnet-4-6", max_tokens: max, system: sys, messages: msgs })
  })
  const d = await r.json()
  if (d.error) throw new Error(d.error.message)
  return d.content[0].text
}

function VBadge({ v, large }) {
  const c = VC[v] || {}
  return (
    <span className={`vb ${c.cls}`} style={large ? { fontSize: 13, padding: "4px 11px" } : {}}>
      <i className={`ti ${c.icon}`} aria-hidden="true" />
      {c.lbl}
    </span>
  )
}

function Avatar({ agent }) {
  return <div className={`av av-${agent.toLowerCase()}`} aria-hidden="true">{agent}</div>
}

function Turn({ t, msA, msB }) {
  const isA = t.agent === "A"
  const ms = isA ? MS[msA] : MS[msB]
  return (
    <div className={`tn tn-${isA ? "a" : "b"}`}>
      <div className={`thd${isA ? "" : " thd-r"}`}>
        <Avatar agent={t.agent} />
        <span className={isA ? "tla" : "tlb"}>{ms?.label}</span>
        <span className="trn">Tour {t.round}</span>
      </div>
      <div className={`bb bb-${isA ? "a" : "b"}`}>{t.content}</div>
    </div>
  )
}

function VerdictCard({ v, onNew, onJSON, onMD }) {
  const c = VC[v.verdict] || {}
  const pct = Math.round((v.confidence || 0) * 100)
  return (
    <div className={`vc ${c.cls}`}>
      <div className="vh">
        <i className={`ti ${c.icon} vi`} aria-hidden="true" />
        <span className="vn">{c.lbl}</span>
        <div className="vpc">
          <span className="vpn">{pct}%</span>
          <span className="vpl">confiance</span>
        </div>
      </div>
      <div className="cbar"><div className="cf" style={{ width: `${pct}%` }} /></div>
      {v.rationale && <div className="vr">{v.rationale}</div>}
      {(v.agreement?.length > 0 || v.disagreement?.length > 0) && (
        <div className="vls">
          {v.agreement?.length > 0 && (
            <div className="vl">
              <div className="vll">Points d'accord</div>
              {v.agreement.map((a, i) => <div key={i} className="vli">· {a}</div>)}
            </div>
          )}
          {v.disagreement?.length > 0 && (
            <div className="vl">
              <div className="vll">Désaccords persistants</div>
              {v.disagreement.map((d, i) => <div key={i} className="vli">· {d}</div>)}
            </div>
          )}
        </div>
      )}
      <div className="va">
        <button className="ba" onClick={onNew}><i className="ti ti-plus" aria-hidden="true" /> Nouveau débat</button>
        <button className="bg" onClick={onJSON}><i className="ti ti-download" aria-hidden="true" /> JSON</button>
        <button className="bg" onClick={onMD}><i className="ti ti-download" aria-hidden="true" /> Markdown</button>
        <span className="dn">Mode démo · Claude × Claude</span>
      </div>
    </div>
  )
}

export default function App() {
  const [view, setView]       = useState("compose")
  const [hyp, setHyp]         = useState("")
  const [ctx, setCtx]         = useState("")
  const [fname, setFname]     = useState("")
  const [showCtx, setShowCtx] = useState(false)
  const [drag, setDrag]       = useState(false)
  const [msA, setMsA]         = useState("empiricist")
  const [msB, setMsB]         = useState("rationalist")
  const [rds, setRds]         = useState(3)
  const [turns, setTurns]     = useState([])
  const [verdict, setVerdict] = useState(null)
  const [step, setStep]       = useState("")
  const [err, setErr]         = useState(null)
  const [sessions, setSessions] = useState([])
  const [detail, setDetail]   = useState(null)
  const txRef  = useRef(null)
  const fileRef = useRef(null)
  const trRef  = useRef([])

  useEffect(() => {
    if (txRef.current) txRef.current.scrollTop = txRef.current.scrollHeight
  }, [turns, step, err])

  const addTurn = (agent, round, content) => {
    const t = { agent, round, content, id: Date.now() + Math.random() }
    trRef.current = [...trRef.current, t]
    setTurns(p => [...p, t])
  }

  const handleFile = async (file) => {
    if (!file) return
    setFname(file.name)
    setCtx((await file.text()).slice(0, 2000))
  }

  const dl = (content, name, type) => {
    const a = document.createElement("a")
    a.href = URL.createObjectURL(new Blob([content], { type }))
    a.download = name; a.click()
  }

  const buildSession = (s) => ({
    hypothesis: s.hyp, timestamp: new Date().toISOString(),
    models: { A: "anthropic:claude-sonnet-4-6", B: "anthropic:claude-sonnet-4-6", judge: "anthropic:claude-sonnet-4-6" },
    mindsets: { A: s.msA, B: s.msB }, rounds: s.rds, transcript: s.turns, verdict: s.verdict
  })

  const doJSON = (s) => dl(JSON.stringify(buildSession(s), null, 2), `agora_${Date.now()}.json`, "application/json")
  const doMD = (s) => {
    const c = VC[s.verdict?.verdict] || {}
    let md = `# Agora\n\n**Hypothèse** : ${s.hyp}\n**Date** : ${new Date().toISOString()}\n**Agents** : ${MS[s.msA]?.label} vs ${MS[s.msB]?.label} · ${s.rds} tours\n\n---\n\n## Transcription\n\n`
    s.turns.forEach(t => { md += `### Tour ${t.round} — Agent ${t.agent} (${MS[t.agent === "A" ? s.msA : s.msB]?.label})\n\n${t.content}\n\n` })
    md += `---\n\n## Verdict : ${c.lbl} (${Math.round((s.verdict?.confidence || 0) * 100)}%)\n\n${s.verdict?.rationale}\n\n`
    if (s.verdict?.agreement?.length) md += `**Accord** :\n${s.verdict.agreement.map(a => `- ${a}`).join("\n")}\n\n`
    if (s.verdict?.disagreement?.length) md += `**Désaccords** :\n${s.verdict.disagreement.map(d => `- ${d}`).join("\n")}\n\n`
    dl(md, `agora_${Date.now()}.md`, "text/markdown")
  }

  const goCompose = () => { setDetail(null); setView("compose") }
  const goHistory = () => setView("history")
  const openDetail = (s) => { setDetail(s); setView("detail") }

  const canLaunch = hyp.trim() && msA !== msB
  const curSess = detail || (verdict ? { hyp, verdict, turns, msA, msB, rds } : null)

  const runDebate = async () => {
    if (!canLaunch) return
    trRef.current = []
    setTurns([]); setVerdict(null); setErr(null); setStep("")
    const mA = MS[msA], mB = MS[msB]
    const base = ctx ? `Hypothèse : "${hyp}"\n\nContexte :\n${ctx.slice(0, 600)}` : `Hypothèse : "${hyp}"`
    const hA = [], hB = []
    setView("debate")
    try {
      for (let r = 0; r < rds; r++) {
        setStep(`Tour ${r} · Agent A — ${mA.label}…`)
        const pA = r === 0 ? `${base}\n\nDonne ta position initiale.`
          : `L'Agent B : "${hB.at(-1)?.content?.slice(0, 280)}"\n\nRéponds. Maintiens ta position si justifiée.`
        hA.push({ role: "user", content: pA })
        const rA = await ask(mA.sys, hA)
        hA.push({ role: "assistant", content: rA })
        addTurn("A", r, rA)

        setStep(`Tour ${r} · Agent B — ${mB.label}…`)
        const pB = r === 0 ? `${base}\n\nDonne ta position initiale.`
          : `L'Agent A : "${hA.at(-2)?.content?.slice(0, 280)}"\n\nRéponds. Maintiens ta position si justifiée.`
        hB.push({ role: "user", content: pB })
        const rB = await ask(mB.sys, hB)
        hB.push({ role: "assistant", content: rB })
        addTurn("B", r, rB)
      }
      setStep("Juge · délibération…")
      let tx = `Hypothèse : "${hyp}"\n\n`
      for (let r = 0; r < rds; r++) {
        tx += `--- Tour ${r} ---\n`
        const a = hA.filter(m => m.role === "assistant")[r]
        const b = hB.filter(m => m.role === "assistant")[r]
        if (a) tx += `Agent A (${mA.label}) : ${a.content}\n\n`
        if (b) tx += `Agent B (${mB.label}) : ${b.content}\n\n`
      }
      const jr = await ask(JUDGE, [{ role: "user", content: tx }], 512)
      let v
      try { v = JSON.parse(jr.replace(/```json|```/g, "").trim()) }
      catch { v = { verdict: "PENDING", confidence: 0.5, agreement: [], disagreement: [], rationale: jr.slice(0, 200) } }
      setVerdict(v)
      setSessions(s => [{ id: Date.now(), hyp, verdict: v, turns: trRef.current, msA, msB, rds, ts: new Date() }, ...s])
      setStep("")
    } catch (e) {
      setErr(e.message); setStep("")
    }
  }

  return (
    <>
      <style>{S}</style>
      <div className="app">
        <span style={{ position: "absolute", width: 1, height: 1, overflow: "hidden", clip: "rect(0,0,0,0)" }}>
          <h2>Agora — laboratoire de débat agentique : formulez une hypothèse, configurez deux agents, lancez le débat, consultez le verdict.</h2>
        </span>

        {/* Header */}
        <div className="hdr">
          <i className="ti ti-messages" style={{ fontSize: 18, color: "var(--text-accent)" }} aria-hidden="true" />
          <span className="brand">Agora</span>
          <span className="sub">laboratoire de débat agentique</span>
          <div className="nav">
            {(view === "debate" || view === "history" || view === "detail") && (
              <button className="nbtn" onClick={goCompose}>
                <i className="ti ti-plus" aria-hidden="true" /> Nouveau débat
              </button>
            )}
            <button className={`nbtn${view === "history" || view === "detail" ? " act" : ""}`} onClick={goHistory}>
              <i className="ti ti-history" aria-hidden="true" />
              Historique{sessions.length > 0 ? ` (${sessions.length})` : ""}
            </button>
            <a href="https://github.com/symbioticode/agora" target="_blank" className="nbtn">
              <i className="ti ti-brand-github" aria-hidden="true" />
            </a>
          </div>
        </div>

        {/* Compose */}
        {view === "compose" && (
          <div className="compose">
            <div>
              <label className="field-lbl">Hypothèse à débattre</label>
              <textarea rows={4} value={hyp} onChange={e => setHyp(e.target.value)}
                placeholder="Formulez une hypothèse, une question ou une affirmation. Les deux agents débattront de sa validité." />
            </div>

            <div className="agents">
              {["A", "B"].map(ag => (
                <div key={ag} className="acol">
                  <div className="ahdr">
                    <Avatar agent={ag} />
                    <span className="anm">Agent {ag}</span>
                  </div>
                  {Object.entries(MS).map(([id, m]) => {
                    const selA = ag === "A" && msA === id
                    const selB = ag === "B" && msB === id
                    const blocked = (ag === "A" && msB === id) || (ag === "B" && msA === id)
                    return (
                      <button key={id}
                        className={`mc${selA ? " sa" : selB ? " sb" : ""}`}
                        disabled={blocked}
                        onClick={() => ag === "A" ? setMsA(id) : setMsB(id)}>
                        <i className={`ti ${m.icon}`} aria-hidden="true" />
                        <div>
                          <div className="mn">{m.label}</div>
                          <div className="md">{m.desc}</div>
                        </div>
                        {(selA || selB) && <i className="ti ti-check" style={{ fontSize: 14, marginLeft: "auto" }} aria-hidden="true" />}
                      </button>
                    )
                  })}
                </div>
              ))}
            </div>

            <div className="opts">
              <span className="ol">Tours</span>
              {[1, 2, 3, 4, 5].map(n => (
                <button key={n} className={`rb${rds === n ? " rs" : ""}`} onClick={() => setRds(n)}>{n}</button>
              ))}
              <span className="on">~{rds * 2 + 1} appels API</span>
              <button className="ctog" onClick={() => setShowCtx(x => !x)}>
                <i className={`ti ${showCtx ? "ti-chevron-down" : "ti-chevron-right"}`} aria-hidden="true" />
                Contexte {ctx && "✓"}
              </button>
            </div>

            {showCtx && (
              <div className="carea">
                <div className={`dz${drag ? " dov" : ""}${fname ? " hf" : ""}`}
                  onClick={() => fileRef.current?.click()}
                  onDrop={e => { e.preventDefault(); setDrag(false); handleFile(e.dataTransfer.files[0]) }}
                  onDragOver={e => { e.preventDefault(); setDrag(true) }}
                  onDragLeave={() => setDrag(false)}
                  role="button" tabIndex={0}>
                  <i className={`ti ${fname ? "ti-file-check" : "ti-file-upload"}`} aria-hidden="true" />
                  <span>{fname || "Déposer un fichier .txt ou .md, ou cliquer"}</span>
                </div>
                <input ref={fileRef} type="file" accept=".txt,.md,.csv" style={{ display: "none" }} onChange={e => handleFile(e.target.files[0])} />
                {ctx && (
                  <div className="cfr">
                    <span className="cnote">{ctx.length} caractères chargés</span>
                    <button className="crm" onClick={() => { setCtx(""); setFname("") }}>Retirer</button>
                  </div>
                )}
              </div>
            )}

            {msA === msB && (
              <div className="warn">
                <i className="ti ti-alert-triangle" aria-hidden="true" /> Les deux agents doivent avoir des mindsets différents.
              </div>
            )}

            <button className="lbtn" onClick={runDebate} disabled={!canLaunch}>
              <i className="ti ti-player-play" aria-hidden="true" /> Lancer le débat
            </button>
          </div>
        )}

        {/* Debate */}
        {view === "debate" && (
          <>
            <div className="qbar">
              <i className="ti ti-quote" style={{ fontSize: 15, color: "var(--text-secondary)", flexShrink: 0 }} aria-hidden="true" />
              <span className="qtxt">"{hyp.slice(0, 110)}{hyp.length > 110 ? "…" : ""}"</span>
              <div className="qtags">
                <span style={{ color: "var(--text-accent)", fontWeight: 500 }}>{MS[msA].label}</span>
                <span style={{ color: "var(--text-muted)" }}>vs</span>
                <span style={{ color: "var(--text-warning)", fontWeight: 500 }}>{MS[msB].label}</span>
                <span style={{ color: "var(--text-muted)" }}>· {rds} tour{rds > 1 ? "s" : ""}</span>
              </div>
            </div>
            <div className="tx" ref={txRef}>
              {turns.map(t => <Turn key={t.id} t={t} msA={msA} msB={msB} />)}
              {step && <div className="ld"><i className="ti ti-loader-2" aria-hidden="true" /> {step}</div>}
              {err && <div className="eb"><strong>Erreur</strong> — {err}</div>}
            </div>
            {verdict && (
              <div className="vwrap">
                <VerdictCard v={verdict} onNew={goCompose}
                  onJSON={() => doJSON({ hyp, verdict, turns, msA, msB, rds })}
                  onMD={() => doMD({ hyp, verdict, turns, msA, msB, rds })} />
              </div>
            )}
          </>
        )}

        {/* History */}
        {view === "history" && (
          <div className="hi">
            {sessions.length === 0 ? (
              <div className="he">
                <i className="ti ti-history" aria-hidden="true" />
                <div className="he-t">Aucune session enregistrée</div>
                <div className="he-s">Les sessions apparaissent ici après chaque débat lancé.</div>
                <button className="ba" onClick={goCompose}><i className="ti ti-plus" aria-hidden="true" /> Lancer un premier débat</button>
              </div>
            ) : (
              <div className="hl">
                {sessions.map((s, i) => (
                  <button key={s.id} className="sc" onClick={() => openDetail(s)}>
                    <div className="si">
                      <div className="sh">"{s.hyp.slice(0, 90)}{s.hyp.length > 90 ? "…" : ""}"</div>
                      <div className="sm">
                        <span style={{ color: "var(--text-accent)" }}>{MS[s.msA]?.label}</span>
                        <span>vs</span>
                        <span style={{ color: "var(--text-warning)" }}>{MS[s.msB]?.label}</span>
                        <span>· {s.rds} tour{s.rds > 1 ? "s" : ""}</span>
                        <span className="stt">{new Date(s.ts).toLocaleTimeString("fr-FR", { hour: "2-digit", minute: "2-digit" })}</span>
                      </div>
                    </div>
                    <VBadge v={s.verdict?.verdict} />
                    <i className="ti ti-chevron-right" style={{ fontSize: 16, color: "var(--text-muted)" }} aria-hidden="true" />
                  </button>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Detail */}
        {view === "detail" && detail && (
          <>
            <div className="dhdr">
              <button className="bk" onClick={goHistory}><i className="ti ti-arrow-left" aria-hidden="true" /> Historique</button>
              <span style={{ fontSize: 12, color: "var(--text-muted)" }}>·</span>
              <span className="dq">"{detail.hyp.slice(0, 80)}{detail.hyp.length > 80 ? "…" : ""}"</span>
              <VBadge v={detail.verdict?.verdict} />
            </div>
            <div className="tx">
              {detail.turns.map(t => <Turn key={t.id} t={t} msA={detail.msA} msB={detail.msB} />)}
            </div>
            {detail.verdict && (
              <div className="vwrap">
                <VerdictCard v={detail.verdict} onNew={goCompose}
                  onJSON={() => doJSON(detail)} onMD={() => doMD(detail)} />
              </div>
            )}
          </>
        )}
      </div>
    </>
  )
}
