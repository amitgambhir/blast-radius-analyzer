import { useState } from 'react'
import { ChevronDown, ChevronRight } from 'lucide-react'

function PassLog({ pass }) {
  const [open, setOpen] = useState(false)
  return (
    <div className="border-b border-border last:border-0">
      <button
        onClick={() => setOpen(o => !o)}
        className="w-full flex items-center gap-2 px-4 py-2.5 hover:bg-[#21262d] transition-colors text-left"
      >
        {open ? <ChevronDown size={11} className="text-text-secondary flex-shrink-0" /> : <ChevronRight size={11} className="text-text-secondary flex-shrink-0" />}
        <span className="text-xs font-mono text-text-secondary">Pass {pass.pass}</span>
        <span className="text-xs text-text-primary">{pass.name}</span>
      </button>
      {open && (
        <pre className="px-4 pb-4 text-xs font-mono text-text-secondary overflow-x-auto leading-relaxed max-h-80 overflow-y-auto bg-bg/50">
          {JSON.stringify(pass.output, null, 2)}
        </pre>
      )}
    </div>
  )
}

export default function AnalysisLog({ passes }) {
  const [open, setOpen] = useState(false)
  if (!passes?.length) return null
  return (
    <div className="border border-border rounded-lg overflow-hidden">
      <button
        onClick={() => setOpen(o => !o)}
        className="w-full flex items-center gap-2 px-4 py-3 hover:bg-surface transition-colors text-left"
      >
        {open ? <ChevronDown size={13} className="text-text-secondary" /> : <ChevronRight size={13} className="text-text-secondary" />}
        <span className="text-sm text-text-secondary">Analysis Log</span>
        <span className="text-xs text-text-secondary/50 ml-1">— full reasoning chain output</span>
      </button>
      {open && (
        <div className="border-t border-border">
          {passes.map(p => <PassLog key={p.pass} pass={p} />)}
        </div>
      )}
    </div>
  )
}
