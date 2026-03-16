import { useState } from 'react'
import { Info } from 'lucide-react'
import IntakeForm from './components/IntakeForm/index.jsx'
import ResultsPanel from './components/Results/index.jsx'
import StreamingProgress from './components/StreamingProgress.jsx'
import AboutPanel from './components/AboutPanel/index.jsx'
import { useAnalysis } from './hooks/useAnalysis.js'

const INITIAL_FORM = {
  services: [
    { id: '', name: '', owner_team: '', criticality: 'medium', description: '' },
    { id: '', name: '', owner_team: '', criticality: 'medium', description: '' },
    { id: '', name: '', owner_team: '', criticality: 'medium', description: '' },
  ],
  dependencies: [],
  teams: [],
  decision: {
    title: '',
    description: '',
    decision_type: 'architecture',
    affected_services: [],
    timeline: 'weeks',
    reversibility: 'moderate',
  },
  additional_context: '',
}

export default function App() {
  const [formData, setFormData] = useState(INITIAL_FORM)
  const [showAbout, setShowAbout] = useState(false)
  const { status, passes, currentPass, result, error, startAnalysis, reset } = useAnalysis()

  const handleSubmit = () => {
    const services = formData.services.filter(s => s.name && s.id)
    if (services.length === 0) {
      alert('Add at least one service before analyzing.')
      return
    }
    if (!formData.decision.title) {
      alert('Enter a decision title before analyzing.')
      return
    }

    // Filter incomplete teams
    let teams = formData.teams.filter(t => t.name && t.id)

    // If no teams defined, auto-derive from service owner_team fields
    if (teams.length === 0) {
      const seen = new Set()
      teams = services
        .filter(s => s.owner_team)
        .reduce((acc, s) => {
          if (!seen.has(s.owner_team)) {
            seen.add(s.owner_team)
            acc.push({
              id: s.owner_team,
              name: s.owner_team.replace(/-/g, ' ').replace(/\b\w/g, c => c.toUpperCase()),
              owns: services.filter(sv => sv.owner_team === s.owner_team).map(sv => sv.id),
              size: 5,
              focus: 'product',
            })
          }
          return acc
        }, [])
    }

    startAnalysis({ ...formData, services, teams })
  }

  const handleLoadExample = (exampleData) => {
    setFormData(exampleData)
    reset()
  }

  return (
    <div className="flex flex-col h-screen bg-bg overflow-hidden">
      {/* Nav */}
      <nav className="flex items-center justify-between px-6 py-3 border-b border-border flex-shrink-0 bg-surface/50">
        <div className="flex items-center gap-3">
          <span className="text-2xl leading-none">💥</span>
          <div>
            <h1 className="font-mono text-sm font-semibold text-text-primary leading-none tracking-tight">
              Blast Radius Analyzer
            </h1>
            <p className="text-xs text-text-secondary mt-0.5">
              Map the impact of your decisions before they map you.
            </p>
          </div>
        </div>
        <button
          onClick={() => setShowAbout(true)}
          className="flex items-center gap-1.5 text-text-secondary hover:text-text-primary transition-colors text-sm px-3 py-1.5 rounded border border-border hover:border-text-secondary"
        >
          <Info size={14} />
          About
        </button>
      </nav>

      {/* Main two-panel layout */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left — intake form (40%) */}
        <div className="w-[40%] min-w-[360px] border-r border-border overflow-y-auto flex-shrink-0">
          <IntakeForm
            formData={formData}
            onChange={setFormData}
            onSubmit={handleSubmit}
            onLoadExample={handleLoadExample}
            isAnalyzing={status === 'streaming'}
          />
        </div>

        {/* Right — results (60%) */}
        <div className="flex-1 overflow-y-auto">
          {status === 'idle' && (
            <div className="flex flex-col items-center justify-center h-full text-center p-12 gap-4">
              <div className="text-5xl">🎯</div>
              <h2 className="text-lg font-semibold text-text-primary">Ready to analyze</h2>
              <p className="text-text-secondary text-sm max-w-xs leading-relaxed">
                Fill in your system context, or load one of the example scenarios to see a full analysis in under 60 seconds.
              </p>
              <p className="text-xs text-text-secondary/60 font-mono">
                Click "Load Example ▾" in the top-left of the form.
              </p>
            </div>
          )}

          {status === 'streaming' && (
            <StreamingProgress passes={passes} currentPass={currentPass} />
          )}

          {status === 'error' && (
            <div className="flex flex-col items-center justify-center h-full p-12 gap-3">
              <div className="text-4xl">⚠️</div>
              <h2 className="text-base font-semibold text-critical">Analysis failed</h2>
              <p className="text-text-secondary text-sm font-mono max-w-lg text-center leading-relaxed">{error}</p>
              <button
                onClick={reset}
                className="mt-2 px-4 py-2 border border-border rounded text-sm text-text-secondary hover:text-text-primary transition-colors"
              >
                Try again
              </button>
            </div>
          )}

          {status === 'complete' && result && (
            <ResultsPanel result={result} passes={passes} />
          )}
        </div>
      </div>

      {showAbout && <AboutPanel onClose={() => setShowAbout(false)} />}
    </div>
  )
}
