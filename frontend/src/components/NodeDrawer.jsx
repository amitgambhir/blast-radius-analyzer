import { X, AlertTriangle } from 'lucide-react'

const SEVERITY_STYLES = {
  critical: { text: 'text-critical', border: 'border-critical/30', bg: 'bg-critical/5' },
  high: { text: 'text-high', border: 'border-high/30', bg: 'bg-high/5' },
  medium: { text: 'text-medium', border: 'border-medium/30', bg: 'bg-medium/5' },
  low: { text: 'text-low', border: 'border-low/30', bg: 'bg-low/5' },
  none: { text: 'text-text-secondary', border: 'border-border', bg: '' },
}

export default function NodeDrawer({ node, onClose }) {
  if (!node) return null
  const s = SEVERITY_STYLES[node.risk_severity] || SEVERITY_STYLES.none

  return (
    <div className="fixed inset-0 z-50 flex" onClick={onClose}>
      <div className="flex-1 bg-black/40" />
      <div
        className="w-96 bg-surface border-l border-border overflow-y-auto slide-in-right flex flex-col"
        onClick={e => e.stopPropagation()}
      >
        {/* Header */}
        <div className="sticky top-0 bg-surface z-10 border-b border-border p-4 flex items-start justify-between gap-3">
          <div className="min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <span className="text-xs font-mono text-text-secondary uppercase tracking-wider">{node.type}</span>
              <span className={`text-xs font-mono uppercase font-semibold ${s.text}`}>{node.risk_severity}</span>
              {node.is_inferred && <span className="text-xs text-text-secondary">◈ inferred</span>}
            </div>
            <h3 className="text-base font-semibold text-text-primary leading-tight">{node.name}</h3>
            <p className="text-xs text-text-secondary mt-0.5 font-mono">{node.impact_level}</p>
          </div>
          <button onClick={onClose} className="text-text-secondary hover:text-text-primary transition-colors flex-shrink-0 mt-0.5">
            <X size={17} />
          </button>
        </div>

        <div className="p-4 space-y-4 flex-1">
          {/* Impact */}
          <div>
            <h4 className="text-xs font-semibold text-text-secondary uppercase tracking-wider mb-2">Impact</h4>
            <p className="text-sm text-text-primary leading-relaxed">{node.impact_description || '—'}</p>
          </div>

          {/* Actions */}
          {node.recommended_actions?.length > 0 && (
            <div>
              <h4 className="text-xs font-semibold text-text-secondary uppercase tracking-wider mb-2">Recommended Actions</h4>
              <ul className="space-y-2">
                {node.recommended_actions.map((action, i) => (
                  <li key={i} className="flex gap-2 text-sm text-text-primary">
                    <span className="text-accent flex-shrink-0 mt-0.5">→</span>
                    <span className="leading-relaxed">{action}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Inferred warning */}
          {node.is_inferred && (
            <div className="flex items-start gap-2 border border-high/20 bg-high/5 rounded-lg p-3">
              <AlertTriangle size={14} className="text-high flex-shrink-0 mt-0.5" />
              <p className="text-xs text-text-secondary leading-relaxed">
                This node was <strong className="text-high">inferred</strong> by the analysis engine — not explicitly defined in your intake. Verify before acting on it.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
