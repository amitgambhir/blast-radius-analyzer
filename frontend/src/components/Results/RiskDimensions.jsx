const DIM_ICONS = { technical: '⚙️', delivery: '🚀', people: '👥', compliance: '🔒', financial: '💰' }

function scoreColor(s) {
  if (s > 0.75) return '#f85149'
  if (s > 0.5) return '#e3b341'
  if (s > 0.3) return '#58a6ff'
  return '#3fb950'
}

function ScoreBar({ score }) {
  const pct = Math.round(score * 100)
  const color = scoreColor(score)
  return (
    <div className="flex items-center gap-2 my-2">
      <div className="flex-1 h-1.5 bg-border rounded-full overflow-hidden">
        <div className="h-full rounded-full score-bar-fill" style={{ width: `${pct}%`, backgroundColor: color }} />
      </div>
      <span className="text-xs font-mono font-semibold w-6 text-right" style={{ color }}>{pct}</span>
    </div>
  )
}

export default function RiskDimensions({ dimensions }) {
  if (!dimensions?.length) return null
  return (
    <div>
      <h3 className="text-sm font-semibold text-text-primary mb-3">Risk Dimensions</h3>
      <div className="grid grid-cols-5 gap-2">
        {dimensions.map(dim => (
          <div key={dim.dimension} className="bg-surface border border-border rounded-lg p-3">
            <div className="flex items-center gap-1.5 mb-0.5">
              <span className="text-sm">{DIM_ICONS[dim.dimension]}</span>
              <span className="text-xs font-semibold text-text-primary capitalize">{dim.dimension}</span>
            </div>
            <ScoreBar score={dim.score} />
            <p className="text-xs text-text-secondary leading-relaxed mb-2">{dim.summary}</p>
            {dim.top_risks?.slice(0, 2).map((r, i) => (
              <div key={i} className="flex gap-1 text-xs text-text-secondary mb-1">
                <span className="text-critical/70 flex-shrink-0">▸</span>
                <span className="leading-tight">{r}</span>
              </div>
            ))}
            {dim.mitigations?.[0] && (
              <div className="flex gap-1 text-xs text-low mt-2">
                <span className="flex-shrink-0">✓</span>
                <span className="leading-tight">{dim.mitigations[0]}</span>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
