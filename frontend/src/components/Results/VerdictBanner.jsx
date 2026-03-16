const VERDICT = {
  LOW: { text: 'text-low', bg: 'bg-low/10', border: 'border-low/30' },
  MODERATE: { text: 'text-medium', bg: 'bg-medium/10', border: 'border-medium/30' },
  HIGH: { text: 'text-high', bg: 'bg-high/10', border: 'border-high/30' },
  CRITICAL: { text: 'text-critical', bg: 'bg-critical/10', border: 'border-critical/30' },
}

export default function VerdictBanner({ verdict, score, summary, title }) {
  const cfg = VERDICT[verdict] || VERDICT.MODERATE
  const pct = Math.round(score * 100)

  return (
    <div className={`border rounded-xl p-5 ${cfg.bg} ${cfg.border}`}>
      <div className="flex items-start justify-between gap-4 mb-3">
        <div className="flex-1 min-w-0">
          <p className="text-xs text-text-secondary font-mono mb-1 uppercase tracking-wider">Blast Radius Assessment</p>
          <h2 className="text-base font-semibold text-text-primary leading-snug">{title}</h2>
        </div>
        <div className="text-right flex-shrink-0">
          <div className={`text-4xl font-mono font-bold leading-none ${cfg.text}`}>{pct}</div>
          <div className="text-xs text-text-secondary font-mono mt-0.5">risk score</div>
          <div className={`inline-block mt-1.5 text-xs font-mono font-bold px-2.5 py-0.5 rounded border ${cfg.text} ${cfg.bg} ${cfg.border}`}>
            {verdict}
          </div>
        </div>
      </div>
      <p className="text-sm text-text-secondary leading-relaxed">{summary}</p>
    </div>
  )
}
