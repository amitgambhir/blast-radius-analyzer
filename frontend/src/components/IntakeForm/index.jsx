import { useState } from 'react'
import { ChevronDown, ChevronRight } from 'lucide-react'
import ServicesSection from './ServicesSection.jsx'
import DependenciesSection from './DependenciesSection.jsx'
import DecisionSection from './DecisionSection.jsx'
import TeamsSection from './TeamsSection.jsx'
import { EXAMPLES } from '../../data/examples.js'

function Section({ title, badge, children, defaultOpen = true }) {
  const [open, setOpen] = useState(defaultOpen)
  return (
    <div className="border-b border-border">
      <button
        onClick={() => setOpen(o => !o)}
        className="w-full flex items-center justify-between px-5 py-3 hover:bg-surface/40 transition-colors"
      >
        <div className="flex items-center gap-2">
          {open
            ? <ChevronDown size={13} className="text-text-secondary" />
            : <ChevronRight size={13} className="text-text-secondary" />}
          <span className="text-xs font-semibold text-text-primary uppercase tracking-wide">{title}</span>
          {badge !== undefined && (
            <span className="text-xs font-mono text-accent bg-accent/10 px-1.5 py-0.5 rounded">{badge}</span>
          )}
        </div>
      </button>
      {open && <div className="pb-4">{children}</div>}
    </div>
  )
}

export default function IntakeForm({ formData, onChange, onSubmit, onLoadExample, isAnalyzing }) {
  const [showExamples, setShowExamples] = useState(false)
  const validServices = formData.services.filter(s => s.name && s.id)
  const validTeams = formData.teams.filter(t => t.name && t.id)

  return (
    <div className="flex flex-col h-full">
      {/* Top bar */}
      <div className="flex items-center justify-between px-5 py-2.5 border-b border-border bg-surface/30">
        <span className="text-xs font-mono text-text-secondary uppercase tracking-wider">System Context</span>
        <div className="relative">
          <button
            onClick={() => setShowExamples(s => !s)}
            className="flex items-center gap-1 text-xs px-2.5 py-1.5 rounded border border-border text-text-secondary hover:text-text-primary hover:border-text-secondary transition-colors"
          >
            Load Example
            <ChevronDown size={10} />
          </button>
          {showExamples && (
            <div className="absolute right-0 top-9 z-50 w-60 bg-surface border border-border rounded-lg shadow-2xl overflow-hidden">
              {EXAMPLES.map(ex => (
                <button
                  key={ex.id}
                  onClick={() => { onLoadExample(ex.data); setShowExamples(false) }}
                  className="w-full text-left px-4 py-3 hover:bg-[#21262d] transition-colors border-b border-border last:border-0"
                >
                  <div className="text-sm text-text-primary font-medium">{ex.label}</div>
                  <div className="text-xs text-text-secondary mt-0.5">{ex.description}</div>
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Collapsible sections */}
      <div className="flex-1">
        <Section title="A — Services" badge={validServices.length}>
          <ServicesSection
            services={formData.services}
            onChange={services => onChange({ ...formData, services })}
          />
        </Section>

        <Section title="B — Dependencies" badge={formData.dependencies.length}>
          <DependenciesSection
            dependencies={formData.dependencies}
            services={validServices}
            onChange={deps => onChange({ ...formData, dependencies: deps })}
          />
        </Section>

        <Section title="C — Teams" badge={validTeams.length}>
          <TeamsSection
            teams={formData.teams}
            services={validServices}
            onChange={teams => onChange({ ...formData, teams })}
          />
        </Section>

        <Section title="D — The Decision">
          <DecisionSection
            decision={formData.decision}
            additionalContext={formData.additional_context}
            services={validServices}
            onChange={(decision, additional_context) =>
              onChange({ ...formData, decision, additional_context })
            }
          />
        </Section>
      </div>

      {/* CTA */}
      <div className="px-5 py-4 border-t border-border bg-surface/20">
        <button
          onClick={onSubmit}
          disabled={isAnalyzing}
          className="w-full py-3 bg-accent hover:bg-[#d97730] active:bg-[#c76820] disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold rounded-lg transition-colors text-sm shadow-lg shadow-accent/20"
        >
          {isAnalyzing
            ? <span className="flex items-center justify-center gap-2"><span className="animate-spin inline-block">⟳</span> Analyzing…</span>
            : 'Analyze Blast Radius 💥'}
        </button>
      </div>
    </div>
  )
}
