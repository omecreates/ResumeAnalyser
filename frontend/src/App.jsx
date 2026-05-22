// ============================================================
// App.jsx — AI-Upgraded Version
// Replace your existing frontend/src/App.jsx with this file
// ============================================================

import { useState, useCallback, useRef, useEffect } from "react";
import axios from "axios";
import "./App.css";
import AICoach from "./components/AICoach";
import "./components/AICoach.css";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:5000";

const getScoreColor = (score) => {
  if (score >= 75) return "#10b981";
  if (score >= 50) return "#f59e0b";
  return "#ef4444";
};
const getScoreLabel = (score) => {
  if (score >= 80) return "Excellent";
  if (score >= 65) return "Good";
  if (score >= 45) return "Average";
  return "Needs Work";
};
const getScoreGrade = (score) => {
  if (score >= 80) return "A";
  if (score >= 65) return "B";
  if (score >= 45) return "C";
  return "D";
};

function AnimatedNumber({ target, duration = 1500 }) {
  const [display, setDisplay] = useState(0);
  const frameRef = useRef(null);
  const startRef = useRef(null);
  useEffect(() => {
    startRef.current = null;
    const animate = (ts) => {
      if (!startRef.current) startRef.current = ts;
      const p = Math.min((ts - startRef.current) / duration, 1);
      setDisplay(Math.round((1 - Math.pow(1 - p, 3)) * target));
      if (p < 1) frameRef.current = requestAnimationFrame(animate);
    };
    frameRef.current = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(frameRef.current);
  }, [target, duration]);
  return <>{display}</>;
}

function ScoreRing({ score, size = 160 }) {
  const r = 58, circ = 2 * Math.PI * r;
  const offset = circ - (score / 100) * circ;
  const color = getScoreColor(score);
  return (
    <div className="ring-wrap">
      <svg width={size} height={size} viewBox="0 0 140 140">
        <circle cx="70" cy="70" r={r} fill="none" stroke="rgba(255,255,255,0.04)" strokeWidth="12" />
        <circle cx="70" cy="70" r={r} fill="none" stroke={color} strokeWidth="12"
          strokeLinecap="round" strokeDasharray={circ} strokeDashoffset={offset}
          transform="rotate(-90 70 70)"
          style={{ transition: "stroke-dashoffset 1.4s cubic-bezier(0.34,1.56,0.64,1)" }} />
        <circle cx="70" cy="70" r="46" fill="rgba(255,255,255,0.02)" />
      </svg>
      <div className="ring-center">
        <span className="ring-score" style={{ color }}><AnimatedNumber target={score} /></span>
        <span className="ring-max">/100</span>
        <span className="ring-label" style={{ color }}>{getScoreLabel(score)}</span>
        <span className="ring-grade" style={{ background: color + "22", color, border: `1px solid ${color}44` }}>
          {getScoreGrade(score)}
        </span>
      </div>
    </div>
  );
}

function ProgressBar({ label, score, max, icon, delay = 0 }) {
  const pct = Math.round((score / max) * 100);
  const color = getScoreColor(pct);
  return (
    <div className="prog-item" style={{ animationDelay: `${delay}ms` }}>
      <div className="prog-header">
        <span className="prog-icon">{icon}</span>
        <span className="prog-label">{label}</span>
        <span className="prog-val" style={{ color }}>{score}<span className="prog-max">/{max}</span></span>
      </div>
      <div className="prog-track">
        <div className="prog-fill" style={{ width: `${pct}%`, background: color, transitionDelay: `${delay + 200}ms` }} />
      </div>
      <span className="prog-pct">{pct}%</span>
    </div>
  );
}

function SkillChip({ skill, index }) {
  const colors = [["#6366f1","#6366f120"],["#8b5cf6","#8b5cf620"],["#06b6d4","#06b6d420"],["#10b981","#10b98120"],["#f59e0b","#f59e0b20"],["#ec4899","#ec489920"],["#3b82f6","#3b82f620"],["#14b8a6","#14b8a620"]];
  const [fg, bg] = colors[index % colors.length];
  return <span className="chip" style={{ color: fg, background: bg, borderColor: fg + "40" }}>{skill}</span>;
}

function UploadZone({ onFile, loading }) {
  const [drag, setDrag] = useState(false);
  const [hover, setHover] = useState(false);
  const onDrop = (e) => { e.preventDefault(); setDrag(false); const f = e.dataTransfer.files[0]; if (f?.type === "application/pdf") onFile(f); };
  return (
    <label className={`upload-zone ${drag?"dragging":""} ${hover?"hovered":""} ${loading?"busy":""}`}
      onDragOver={(e)=>{e.preventDefault();setDrag(true);}} onDragLeave={()=>setDrag(false)}
      onDrop={onDrop} onMouseEnter={()=>setHover(true)} onMouseLeave={()=>setHover(false)}>
      <input type="file" accept=".pdf" style={{display:"none"}} onChange={(e)=>e.target.files[0]&&onFile(e.target.files[0])} disabled={loading} />
      {loading ? (
        <div className="upload-inner">
          <div className="loader-ring"><div/><div/><div/><div/></div>
          <p className="uz-title">Analyzing your resume…</p>
          <p className="uz-sub">Running AI deep analysis — this takes 10-15 seconds</p>
          <div className="progress-dots"><span/><span/><span/></div>
        </div>
      ) : (
        <div className="upload-inner">
          <div className="uz-icon-wrap">
            <svg className="uz-icon" viewBox="0 0 24 24" fill="none">
              <path d="M12 15V3m0 0L8 7m4-4l4 4" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M2 17l.621 2.485A2 2 0 004.561 21h14.878a2 2 0 001.94-1.515L22 17" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round"/>
            </svg>
          </div>
          <p className="uz-title">{drag ? "Release to upload" : "Drop your resume here"}</p>
          <p className="uz-sub">PDF files only · Max 16MB</p>
          <div className="uz-btn"><span>Browse Files</span>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none"><path d="M5 12h14m-7-7l7 7-7 7" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/></svg>
          </div>
        </div>
      )}
    </label>
  );
}

function StatCard({ value, label, icon, color = "#6366f1" }) {
  return (
    <div className="stat-card" style={{ "--card-accent": color }}>
      <div className="stat-icon" style={{ color, background: color + "18" }}>{icon}</div>
      <div className="stat-body">
        <span className="stat-value" style={{ color }}><AnimatedNumber target={typeof value === "number" ? value : 0} /></span>
        <span className="stat-label">{label}</span>
      </div>
    </div>
  );
}

function SectionPill({ name, found }) {
  return (
    <div className={`section-pill ${found ? "found" : "missing"}`}>
      <span className="pill-dot" /><span>{name}</span>
    </div>
  );
}

function RecCard({ text, index }) {
  const icons = ["📝","🔧","🎯","📊","💼","⚡","🎓","✅"];
  return (
    <div className="rec-card" style={{ animationDelay: `${index * 80}ms` }}>
      <span className="rec-num">{String(index+1).padStart(2,"0")}</span>
      <span className="rec-icon">{icons[index%icons.length]}</span>
      <p className="rec-text">{text}</p>
    </div>
  );
}

// ── Main App ──
export default function App() {
  const [file, setFile]         = useState(null);
  const [loading, setLoading]   = useState(false);
  const [result, setResult]     = useState(null);
  const [error, setError]       = useState(null);
  const [activeTab, setActiveTab] = useState("overview");
  const [jobRole, setJobRole]   = useState("");

  const handleFile = useCallback((f) => { setFile(f); setError(null); setResult(null); }, []);

  const analyze = async () => {
    if (!file) return;
    setLoading(true); setError(null); setResult(null);
    const fd = new FormData();
    fd.append("resume", file);
    fd.append("job_role", jobRole);
    fd.append("ai_enabled", "true");
    try {
      const res = await axios.post(`${API_URL}/analyze`, fd, {
        headers: { "Content-Type": "multipart/form-data" },
        timeout: 60000,   // 60s timeout to allow AI analysis time
      });
      setResult(res.data);
      setActiveTab("overview");
      setTimeout(() => document.getElementById("results-anchor")?.scrollIntoView({ behavior: "smooth" }), 100);
    } catch (err) {
      setError(err.response?.data?.error || err.message || "Something went wrong.");
    } finally {
      setLoading(false);
    }
  };

  const reset = () => { setFile(null); setResult(null); setError(null); setJobRole(""); window.scrollTo({ top: 0, behavior: "smooth" }); };

  const allSections = ["education", "experience", "skills", "projects", "contact"];
  const foundSections = result?.score_breakdown?.sections?.found || [];

  // Tabs — add AI Coach tab only if AI analysis is present
  const tabs = [
    { id: "overview", label: "Score Breakdown" },
    { id: "skills",   label: `Skills (${result?.skills_count || 0})` },
    { id: "sections", label: "Sections Audit" },
    { id: "recs",     label: `Tips (${result?.recommendations?.length || 0})` },
    ...(result?.ai_analysis ? [{ id: "ai", label: "🤖 AI Coach" }] : []),
  ];

  return (
    <div className="app">
      <div className="ambient" aria-hidden="true">
        <div className="amb-blob amb-1" /><div className="amb-blob amb-2" /><div className="amb-blob amb-3" />
        <div className="grid-overlay" />
      </div>

      <nav className="nav">
        <div className="nav-inner">
          <div className="brand">
            <div className="brand-icon">
              <svg viewBox="0 0 24 24" fill="none" width="18" height="18">
                <path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" stroke="white" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </div>
            <span className="brand-name">ResumeAI</span>
            <span className="brand-badge">AI POWERED</span>
          </div>
          <div className="nav-links">
            <a href="#analyzer">Analyzer</a>
            <a href="#how">How it works</a>
            {result && <button className="nav-reset" onClick={reset}>← New Resume</button>}
          </div>
        </div>
      </nav>

      <main className="main">
        {!result && (
          <section className="hero" id="analyzer">
            <div className="hero-content">
              <div className="hero-eyebrow"><span className="eyebrow-dot" />AI-Powered · Groq Llama 3.1 · Free</div>
              <h1 className="hero-h1">
                Your personal<br /><span className="hero-highlight">AI Resume Coach</span><br />in seconds
              </h1>
              <p className="hero-p">
                Upload your PDF. Our AI reads every line, detects weaknesses, rewrites bullet points,
                calculates your ATS score, and gives personalized career advice — all in under 15 seconds.
              </p>
              <div className="hero-stats">
                {[["60+","Skills Tracked"],["AI","Deep Analysis"],["<15s","Full Report"]].map(([v,l]) => (
                  <div key={l} className="hero-stat"><span className="hs-val">{v}</span><span className="hs-lbl">{l}</span></div>
                ))}
              </div>
            </div>

            <div className="upload-col">
              <div className="upload-card">
                <div className="uc-header">
                  <span className="uc-title">Upload Resume</span>
                  <span className="uc-step">AI Analysis Included</span>
                </div>
                <UploadZone onFile={handleFile} loading={loading} />

                {/* Job role input — NEW: makes AI advice personalized */}
                <div className="job-role-input">
                  <label className="jri-label">Target Job Role (optional)</label>
                  <input
                    className="jri-field"
                    type="text"
                    placeholder="e.g. Backend Developer, Data Scientist, ML Engineer"
                    value={jobRole}
                    onChange={(e) => setJobRole(e.target.value)}
                    disabled={loading}
                  />
                  <p className="jri-hint">Helps AI give role-specific feedback</p>
                </div>

                {file && !loading && (
                  <div className="file-info">
                    <div className="file-icon-wrap">
                      <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                        <path d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" stroke="#6366f1" strokeWidth="1.8"/>
                        <path d="M13 3v6h6" stroke="#6366f1" strokeWidth="1.8" strokeLinecap="round"/>
                      </svg>
                    </div>
                    <div className="file-meta">
                      <span className="file-name">{file.name}</span>
                      <span className="file-size">{(file.size/1024).toFixed(1)} KB</span>
                    </div>
                    <button className="file-clear" onClick={()=>setFile(null)}>✕</button>
                  </div>
                )}
                {error && <div className="error-box"><span>⚠</span>{error}</div>}
                <button className={`analyze-btn ${!file||loading?"disabled":""}`} onClick={analyze} disabled={!file||loading}>
                  {loading ? "AI is analyzing…" : "Analyze with AI"}
                  {!loading && <svg width="16" height="16" viewBox="0 0 24 24" fill="none"><path d="M5 12h14m-7-7l7 7-7 7" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/></svg>}
                </button>
                <p className="uc-note">🔒 File processed instantly · Never stored · Powered by Groq</p>
              </div>
            </div>
          </section>
        )}

        {result && (
          <section className="results" id="results-anchor">
            <div className="results-banner">
              <div className="rb-left">
                <span className="rb-label">
                  {result.ai_analysis ? "✓ AI Analysis Complete" : "Analysis Complete"}
                </span>
                <h2 className="rb-title">{file?.name}</h2>
                {result.job_role && <p style={{fontSize:"0.8rem",color:"var(--text-muted)",marginTop:4}}>Role: {result.job_role}</p>}
              </div>
              <button className="rb-reset" onClick={reset}>← Analyze Another</button>
            </div>

            <div className="score-hero">
              <div className="sh-ring-col">
                <ScoreRing score={result.ats_score} />
                <p className="sh-hint">
                  {result.ats_score >= 75 ? "Strong ATS performance! AI has suggestions to push higher."
                    : result.ats_score >= 50 ? "Decent start. Check the AI Coach tab for improvements."
                    : "Check AI Coach tab for critical improvements."}
                </p>
                {result.ai_analysis?.estimated_score_after_fixes > result.ats_score && (
                  <div className="potential-score">
                    AI predicts <strong style={{color:"#10b981"}}>~{result.ai_analysis.estimated_score_after_fixes}</strong> after fixes
                  </div>
                )}
              </div>
              <div className="sh-stats">
                <StatCard value={result.skills_count} label="Skills Detected" icon="🔧" color="#6366f1" />
                <StatCard value={result.word_count} label="Word Count" icon="📝" color="#06b6d4" />
                <StatCard value={foundSections.length} label="Sections Found" icon="📋" color="#10b981" />
                <StatCard value={result.score_breakdown?.formatting?.action_verbs_found||0} label="Action Verbs" icon="⚡" color="#f59e0b" />
              </div>
            </div>

            {/* AI error notice */}
            {result.ai_error && (
              <div className="ai-error-banner">
                <span>🤖</span>
                <div>
                  <strong>AI Analysis Unavailable</strong>
                  <p>{result.ai_error}</p>
                </div>
              </div>
            )}

            <div className="tabs">
              {tabs.map((t) => (
                <button key={t.id} className={`tab-btn ${activeTab===t.id?"active":""} ${t.id==="ai"?"tab-ai":""}`} onClick={()=>setActiveTab(t.id)}>
                  {t.label}
                </button>
              ))}
            </div>

            <div className="tab-panel">
              {activeTab === "overview" && (
                <div className="panel-overview">
                  <ProgressBar label="Skills Match" score={result.score_breakdown.skills_match.score} max={40} icon="🔧" delay={0} />
                  <ProgressBar label="Resume Sections" score={result.score_breakdown.sections.score} max={25} icon="📋" delay={80} />
                  <ProgressBar label="Content Length" score={result.score_breakdown.content_length.score} max={20} icon="📝" delay={160} />
                  <ProgressBar label="Formatting Quality" score={result.score_breakdown.formatting.score} max={15} icon="✨" delay={240} />
                  <div className="overview-extra">
                    <div className="oe-card"><span className="oe-icon">📧</span><div><p className="oe-label">Email</p><p className="oe-val">{result.contact_info?.email||"Not detected"}</p></div></div>
                    <div className="oe-card"><span className="oe-icon">📱</span><div><p className="oe-label">Phone</p><p className="oe-val">{result.contact_info?.phone||"Not detected"}</p></div></div>
                    <div className="oe-card"><span className="oe-icon">📊</span><div><p className="oe-label">Quantified Results</p><p className="oe-val" style={{color:result.score_breakdown.formatting.has_quantified_results?"#10b981":"#ef4444"}}>{result.score_breakdown.formatting.has_quantified_results?"✓ Found":"✗ None found"}</p></div></div>
                  </div>
                </div>
              )}

              {activeTab === "skills" && (
                <div className="panel-skills">
                  {result.skills_found.length > 0 ? (
                    <>
                      <p className="panel-note">{result.skills_count} skills detected from 60+ technical keywords.</p>
                      <div className="chips-wrap">{result.skills_found.map((s,i)=><SkillChip key={s} skill={s} index={i}/>)}</div>
                      <div className="skills-tip"><span>💡</span><p>Tailor your skills to the specific job description for better ATS scores.</p></div>
                    </>
                  ) : (
                    <div className="empty-state"><span>🔍</span><p>No technical skills detected. Add specific tools, languages, and frameworks.</p></div>
                  )}
                </div>
              )}

              {activeTab === "sections" && (
                <div className="panel-sections">
                  <p className="panel-note">ATS systems look for these standard resume sections.</p>
                  <div className="sections-grid">
                    {allSections.map((s) => <SectionPill key={s} name={s.charAt(0).toUpperCase()+s.slice(1)} found={foundSections.includes(s)}/>)}
                  </div>
                  <div className="section-score-row">
                    <div className="ssr-bar"><div className="ssr-fill" style={{width:`${(foundSections.length/allSections.length)*100}%`}}/></div>
                    <span className="ssr-label">{foundSections.length}/{allSections.length} sections found</span>
                  </div>
                  {result.text_preview && (
                    <div className="preview-box"><p className="pb-label">Extracted text preview</p><p className="pb-text">{result.text_preview}</p></div>
                  )}
                </div>
              )}

              {activeTab === "recs" && (
                <div className="panel-recs">
                  <p className="panel-note">Apply these improvements to boost your ATS score.</p>
                  {result.recommendations.map((r,i)=><RecCard key={i} text={r} index={i}/>)}
                </div>
              )}

              {activeTab === "ai" && result.ai_analysis && (
                <AICoach ai={result.ai_analysis} jobRole={result.job_role} score={result.ats_score} />
              )}
            </div>
          </section>
        )}

        {!result && (
          <section className="how-section" id="how">
            <div className="how-header">
              <span className="how-eyebrow">The Process</span>
              <h2>How it works</h2>
            </div>
            <div className="how-grid">
              {[
                {n:"01",icon:"📤",title:"Upload PDF",desc:"Drop your resume PDF. Text-based PDFs work best."},
                {n:"02",icon:"📖",title:"Text Extraction",desc:"pdfplumber reads every word accurately from your PDF."},
                {n:"03",icon:"🔧",title:"Skill Detection",desc:"spaCy + NLTK detect 60+ technical skills and keywords."},
                {n:"04",icon:"📊",title:"ATS Scoring",desc:"4 weighted dimensions: skills, sections, content, formatting."},
                {n:"05",icon:"🤖",title:"AI Deep Analysis",desc:"Groq Llama 3.1 reads your resume and gives personal feedback, rewrites weak lines, and suggests improvements."},
                {n:"06",icon:"🚀",title:"Apply & Iterate",desc:"Apply AI suggestions, re-upload, and track your score improvement."},
              ].map((s)=>(
                <div key={s.n} className="how-card">
                  <div className="hc-top"><span className="hc-num">{s.n}</span><span className="hc-icon">{s.icon}</span></div>
                  <h4>{s.title}</h4><p>{s.desc}</p>
                </div>
              ))}
            </div>
          </section>
        )}
      </main>

      <footer className="footer">
        <div className="footer-inner">
          <span className="brand-name" style={{fontSize:"0.9rem"}}>ResumeAI</span>
          <span className="footer-sep">·</span>
          <span>Flask · React · Groq · Llama 3.1 · spaCy</span>
          <span className="footer-sep">·</span>
          <span>VIT B.Tech Project</span>
        </div>
      </footer>
    </div>
  );
}