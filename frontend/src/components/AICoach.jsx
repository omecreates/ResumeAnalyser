// ============================================================
// AICoach.jsx — AI Analysis Results Component
// Place this file at: frontend/src/components/AICoach.jsx
// ============================================================

import { useState } from "react";

// ── Impact / Effort color helpers ──
const impactColor = { high: "#10b981", medium: "#f59e0b", low: "#6b7280" };
const effortColor  = { low: "#10b981", medium: "#f59e0b", high: "#ef4444" };

// ── Small badge component ──
function Badge({ label, color }) {
  return (
    <span style={{
      display: "inline-block", padding: "2px 10px", borderRadius: "999px",
      fontSize: "0.7rem", fontWeight: 700, letterSpacing: "0.06em",
      textTransform: "uppercase", border: `1px solid ${color}50`,
      background: color + "18", color,
    }}>
      {label}
    </span>
  );
}

// ── Collapsible section wrapper ──
function Section({ title, icon, children, defaultOpen = true, accent = "#6366f1" }) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div className="aic-section">
      <button className="aic-section-hdr" onClick={() => setOpen(!open)}
        style={{ borderLeft: `3px solid ${accent}` }}>
        <span className="aic-section-title"><span>{icon}</span> {title}</span>
        <span className="aic-chevron" style={{ transform: open ? "rotate(180deg)" : "rotate(0deg)" }}>
          ▾
        </span>
      </button>
      {open && <div className="aic-section-body">{children}</div>}
    </div>
  );
}

// ── Main AICoach component ──
export default function AICoach({ ai, jobRole, score }) {
  const [copiedIdx, setCopiedIdx] = useState(null);
  const [rewriteText, setRewriteText] = useState("");
  const [rewriteResult, setRewriteResult] = useState(null);
  const [rewriting, setRewriting] = useState(false);

  const copyToClipboard = (text, idx) => {
    navigator.clipboard.writeText(text);
    setCopiedIdx(idx);
    setTimeout(() => setCopiedIdx(null), 2000);
  };

  const handleRewrite = async () => {
    if (!rewriteText.trim()) return;
    setRewriting(true);
    setRewriteResult(null);
    try {
      const res = await fetch("http://localhost:5000/rewrite", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: rewriteText, context: jobRole || "software developer" }),
      });
      const data = await res.json();
      setRewriteResult(data);
    } catch {
      setRewriteResult({ error: "Could not reach AI. Is Flask running?" });
    }
    setRewriting(false);
  };

  if (!ai) return null;

  return (
    <div className="aicoach">
      {/* ── Header ── */}
      <div className="aicoach-header">
        <div className="aicoach-badge">
          <span className="ai-dot" />
          AI Coach · Groq · Llama 3.1
        </div>
        <h3 className="aicoach-title">Deep Resume Analysis</h3>
        {jobRole && <p className="aicoach-role">Targeting: <strong>{jobRole}</strong></p>}
      </div>

      {/* ── Overall Assessment ── */}
      {ai.overall_assessment && (
        <div className="aic-assessment">
          <p>{ai.overall_assessment}</p>
        </div>
      )}

      {/* ── Score Projection ── */}
      {ai.estimated_score_after_fixes > 0 && (
        <div className="aic-projection">
          <div className="proj-item">
            <span className="proj-label">Current Score</span>
            <span className="proj-val" style={{ color: "#f59e0b" }}>{score}</span>
          </div>
          <div className="proj-arrow">→</div>
          <div className="proj-item">
            <span className="proj-label">After AI Fixes</span>
            <span className="proj-val" style={{ color: "#10b981" }}>~{ai.estimated_score_after_fixes}</span>
          </div>
          <div className="proj-gain">
            +{ai.estimated_score_after_fixes - score} points potential
          </div>
        </div>
      )}

      {/* ── Priority Actions ── */}
      {ai.priority_actions?.length > 0 && (
        <Section title="Priority Actions" icon="🎯" accent="#ef4444">
          <div className="aic-actions">
            {ai.priority_actions.map((a, i) => (
              <div key={i} className="aic-action-card">
                <div className="aic-action-top">
                  <span className="aic-action-num">{i + 1}</span>
                  <span className="aic-action-title">{a.action}</span>
                  <div className="aic-action-badges">
                    <Badge label={`Impact: ${a.impact}`} color={impactColor[a.impact] || "#6366f1"} />
                    <Badge label={`Effort: ${a.effort}`} color={effortColor[a.effort] || "#6366f1"} />
                  </div>
                </div>
                {a.description && <p className="aic-action-desc">{a.description}</p>}
              </div>
            ))}
          </div>
        </Section>
      )}

      {/* ── Strengths ── */}
      {ai.strengths?.length > 0 && (
        <Section title="What's Working" icon="✅" accent="#10b981">
          <ul className="aic-list aic-list-green">
            {ai.strengths.map((s, i) => <li key={i}>{s}</li>)}
          </ul>
        </Section>
      )}

      {/* ── Critical Weaknesses ── */}
      {ai.critical_weaknesses?.length > 0 && (
        <Section title="Critical Weaknesses" icon="⚠️" accent="#ef4444">
          <ul className="aic-list aic-list-red">
            {ai.critical_weaknesses.map((w, i) => <li key={i}>{w}</li>)}
          </ul>
        </Section>
      )}

      {/* ── Improved Bullet Points ── */}
      {ai.improved_bullet_points?.length > 0 && (
        <Section title="Rewritten Bullet Points" icon="✍️" accent="#8b5cf6">
          <p className="aic-sub-note">AI rewrote your weakest lines — copy and paste these directly.</p>
          {ai.improved_bullet_points.map((bp, i) => (
            <div key={i} className="aic-bullet-card">
              <div className="aic-bullet-before">
                <span className="aic-bullet-label aic-label-before">Before</span>
                <p className="aic-bullet-text aic-text-before">{bp.original || "—"}</p>
              </div>
              <div className="aic-bullet-arrow">↓</div>
              <div className="aic-bullet-after">
                <span className="aic-bullet-label aic-label-after">After</span>
                <p className="aic-bullet-text aic-text-after">{bp.improved}</p>
                <button className="aic-copy-btn" onClick={() => copyToClipboard(bp.improved, i)}>
                  {copiedIdx === i ? "✓ Copied!" : "Copy"}
                </button>
              </div>
              {bp.why && <p className="aic-bullet-why">💡 {bp.why}</p>}
            </div>
          ))}
        </Section>
      )}

      {/* ── Missing Skills ── */}
      {ai.missing_skills?.length > 0 && (
        <Section title="Skills You Should Add" icon="🔧" accent="#f59e0b">
          <p className="aic-sub-note">These skills are commonly expected for modern tech roles.</p>
          <div className="aic-missing-skills">
            {ai.missing_skills.map((s, i) => (
              <span key={i} className="aic-missing-chip">{s}</span>
            ))}
          </div>
        </Section>
      )}

      {/* ── Section Feedback ── */}
      {ai.section_feedback && Object.keys(ai.section_feedback).length > 0 && (
        <Section title="Section-by-Section Feedback" icon="📋" accent="#06b6d4">
          <div className="aic-section-feedback">
            {Object.entries(ai.section_feedback).map(([sec, feedback]) => (
              feedback ? (
                <div key={sec} className="aic-sf-row">
                  <span className="aic-sf-name">{sec.charAt(0).toUpperCase() + sec.slice(1)}</span>
                  <p className="aic-sf-text">{feedback}</p>
                </div>
              ) : null
            ))}
          </div>
        </Section>
      )}

      {/* ── ATS Tips ── */}
      {ai.ats_optimization_tips?.length > 0 && (
        <Section title="ATS Optimization Tips" icon="🤖" accent="#6366f1">
          <ul className="aic-list aic-list-purple">
            {ai.ats_optimization_tips.map((t, i) => <li key={i}>{t}</li>)}
          </ul>
        </Section>
      )}

      {/* ── Career Advice ── */}
      {ai.career_advice?.length > 0 && (
        <Section title="Career Advice" icon="🚀" accent="#8b5cf6" defaultOpen={false}>
          <ul className="aic-list aic-list-purple">
            {ai.career_advice.map((a, i) => <li key={i}>{a}</li>)}
          </ul>
        </Section>
      )}

      {/* ── Score Justification ── */}
      {ai.score_justification && (
        <Section title="Why This Score?" icon="📊" accent="#06b6d4" defaultOpen={false}>
          <p className="aic-justify">{ai.score_justification}</p>
        </Section>
      )}

      {/* ── Bullet Rewriter Tool ── */}
      <Section title="Bullet Point Rewriter" icon="⚡" accent="#f59e0b" defaultOpen={false}>
        <p className="aic-sub-note">Paste any resume line and AI will make it stronger.</p>
        <textarea
          className="aic-textarea"
          placeholder="e.g. worked on a project to improve website speed"
          value={rewriteText}
          onChange={(e) => setRewriteText(e.target.value)}
          rows={3}
        />
        <button
          className="aic-rewrite-btn"
          onClick={handleRewrite}
          disabled={rewriting || !rewriteText.trim()}
        >
          {rewriting ? "Rewriting…" : "✨ Rewrite with AI"}
        </button>
        {rewriteResult && !rewriteResult.error && (
          <div className="aic-rewrite-result">
            <div className="aic-bullet-after" style={{ marginTop: 0 }}>
              <span className="aic-bullet-label aic-label-after">Rewritten</span>
              <p className="aic-bullet-text aic-text-after">{rewriteResult.rewritten}</p>
              <button className="aic-copy-btn" onClick={() => copyToClipboard(rewriteResult.rewritten, "rw")}>
                {copiedIdx === "rw" ? "✓ Copied!" : "Copy"}
              </button>
            </div>
            {rewriteResult.alternative && (
              <div className="aic-bullet-after" style={{ marginTop: 10, borderColor: "rgba(99,102,241,0.2)" }}>
                <span className="aic-bullet-label" style={{ color: "#6366f1" }}>Alternative</span>
                <p className="aic-bullet-text" style={{ color: "#c4b5fd" }}>{rewriteResult.alternative}</p>
                <button className="aic-copy-btn" onClick={() => copyToClipboard(rewriteResult.alternative, "alt")}>
                  {copiedIdx === "alt" ? "✓ Copied!" : "Copy"}
                </button>
              </div>
            )}
            {rewriteResult.explanation && (
              <p className="aic-bullet-why">💡 {rewriteResult.explanation}</p>
            )}
          </div>
        )}
        {rewriteResult?.error && (
          <div className="error-box" style={{ marginTop: 12 }}>⚠ {rewriteResult.error}</div>
        )}
      </Section>

      {/* ── AI Attribution ── */}
      <div className="aic-footer">
        Powered by {ai.ai_provider || "Groq · Llama 3.1"} · Analysis may vary. Always review AI suggestions critically.
      </div>
    </div>
  );
}