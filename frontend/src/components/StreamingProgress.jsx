import { CheckCircle, Loader } from 'lucide-react'

const PASS_NAMES = [
  'Decision Classification',
  'First-Order Impact',
  'Second-Order Propagation',
  'Organizational Impact',
  'Risk Scoring & Synthesis',
]

const PASS_HINTS = [
  'Classifying decision type, primary risk category, and analysis playbook…',
  'Building NetworkX dependency graph, computing 1-hop neighbors, mapping first-order technical impacts…',
  'Computing 2-hop neighbors, reasoning about dampened vs amplified propagation…',
  'Mapping technical impacts to team workload, roadmap disruption, and SLA risk…',
  'Scoring 5 risk dimensions, computing overall verdict, synthesizing executive summary…',
]

export default function StreamingProgress({ passes, currentPass }) {
  const completedNums = new Set(passes.map(p => p.pass))

  return (
    <div className="p-8 max-w-xl mx-auto">
      <div className="mb-8 text-center">
        <h2 className="text-lg font-semibold text-text-primary">Analyzing blast radius…</h2>
        <p className="text-sm text-text-secondary mt-1">5-pass multi-model reasoning chain</p>
      </div>

      <div className="space-y-3">
        {PASS_NAMES.map((name, i) => {
          const n = i + 1
          const isComplete = completedNums.has(n)
          const isActive = currentPass?.pass === n
          const isFuture = !isComplete && !isActive
          const completed = passes.find(p => p.pass === n)

          return (
            <div
              key={n}
              className={`border rounded-lg p-4 transition-all duration-300 ${
                isComplete ? 'border-low/30 bg-low/5' :
                isActive ? 'border-accent/50 bg-accent/5' :
                'border-border bg-surface/40'
              }`}
            >
              <div className="flex items-start gap-3">
                <div className="flex-shrink-0 mt-0.5">
                  {isComplete
                    ? <CheckCircle size={15} className="text-low" />
                    : isActive
                    ? <Loader size={15} className="text-accent animate-spin" />
                    : <div className="w-[15px] h-[15px] rounded-full border border-border" />}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-mono text-text-secondary">Pass {n}</span>
                    <span className={`text-sm font-medium ${
                      isComplete ? 'text-text-primary' :
                      isActive ? 'text-accent' :
                      'text-text-secondary'
                    }`}>{name}</span>
                  </div>
                  {isActive && (
                    <p className="text-xs text-text-secondary/70 mt-1 animate-pulse leading-relaxed">
                      {currentPass?.message || PASS_HINTS[i]}
                    </p>
                  )}
                  {isComplete && completed?.summary && (
                    <p className="text-xs text-text-secondary mt-1 leading-relaxed">{completed.summary}</p>
                  )}
                  {isFuture && (
                    <p className="text-xs text-text-secondary/30 mt-1">{PASS_HINTS[i]}</p>
                  )}
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
