import { Users } from 'lucide-react'

const SEV = {
  critical: 'text-critical border-critical/25 bg-critical/5',
  high: 'text-high border-high/25 bg-high/5',
  medium: 'text-medium border-medium/25 bg-medium/5',
  low: 'text-low border-low/25 bg-low/5',
  none: 'text-text-secondary border-border',
}

export default function OrgImpact({ nodes }) {
  if (!nodes?.length) return null
  return (
    <div>
      <div className="flex items-center gap-2 mb-3">
        <Users size={15} className="text-accent" />
        <h3 className="text-sm font-semibold text-text-primary">Organizational Impact</h3>
        <span className="text-xs font-mono text-accent bg-accent/10 px-1.5 py-0.5 rounded">Pass 4</span>
        <span className="text-xs text-text-secondary">Most tools stop at technical impact.</span>
      </div>
      <div className="space-y-3">
        {nodes.map(node => (
          <div key={node.id} className={`border rounded-lg p-4 ${SEV[node.risk_severity] || SEV.none}`}>
            <div className="flex items-start justify-between gap-2 mb-2">
              <div>
                <span className="text-sm font-medium text-text-primary">{node.name}</span>
                {node.is_inferred && <span className="ml-2 text-xs text-text-secondary">◈ inferred</span>}
                <span className="ml-2 text-xs text-text-secondary/60 font-mono">{node.type}</span>
              </div>
              <span className={`text-xs font-mono font-semibold uppercase flex-shrink-0 ${
                node.risk_severity === 'critical' ? 'text-critical' :
                node.risk_severity === 'high' ? 'text-high' :
                node.risk_severity === 'medium' ? 'text-medium' :
                'text-low'
              }`}>{node.risk_severity}</span>
            </div>
            <p className="text-xs text-text-secondary leading-relaxed">{node.impact_description}</p>
            {node.recommended_actions?.length > 0 && (
              <ul className="mt-2 space-y-1">
                {node.recommended_actions.map((a, i) => (
                  <li key={i} className="flex gap-1.5 text-xs text-text-secondary">
                    <span className="text-accent flex-shrink-0">→</span>{a}
                  </li>
                ))}
              </ul>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
