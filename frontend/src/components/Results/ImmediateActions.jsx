import { useState } from 'react'
import { Copy, CheckCheck } from 'lucide-react'

function CopyBtn({ text }) {
  const [copied, setCopied] = useState(false)
  return (
    <button
      onClick={() => { navigator.clipboard.writeText(text); setCopied(true); setTimeout(() => setCopied(false), 2000) }}
      className="flex items-center gap-1 text-xs text-text-secondary hover:text-accent transition-colors flex-shrink-0"
    >
      {copied ? <CheckCheck size={11} className="text-low" /> : <Copy size={11} />}
      <span className="hidden sm:inline">{copied ? 'Copied' : 'Copy for Jira'}</span>
    </button>
  )
}

export default function ImmediateActions({ actions }) {
  if (!actions?.length) return null
  return (
    <div>
      <h3 className="text-sm font-semibold text-text-primary mb-3">Immediate Actions</h3>
      <div className="space-y-2">
        {actions.slice(0, 6).map((action, i) => (
          <div key={i} className="flex items-start gap-3 bg-surface border border-border rounded-lg p-3">
            <span className="font-mono text-accent font-bold text-sm flex-shrink-0 mt-0.5">{String(i + 1).padStart(2, '0')}</span>
            <span className="text-sm text-text-primary flex-1 leading-relaxed">{action}</span>
            <CopyBtn text={action} />
          </div>
        ))}
      </div>
    </div>
  )
}
