const DECISION_TYPES = [
  { value: 'architecture', label: '⚙️  Architecture' },
  { value: 'migration', label: '🔄  Migration' },
  { value: 'deprecation', label: '🗑️  Deprecation' },
  { value: 'reorg', label: '👥  Reorg' },
  { value: 'vendor', label: '🤝  Vendor' },
  { value: 'api-change', label: '🔌  API Change' },
  { value: 'infrastructure', label: '🏗️  Infrastructure' },
]

function SegmentedControl({ options, value, onChange }) {
  return (
    <div className="flex rounded overflow-hidden border border-border">
      {options.map(opt => (
        <button
          key={opt.value}
          onClick={() => onChange(opt.value)}
          className={`flex-1 text-xs py-1.5 px-1 transition-colors ${
            value === opt.value
              ? 'bg-accent text-white font-semibold'
              : 'bg-bg text-text-secondary hover:text-text-primary hover:bg-surface'
          }`}
        >
          {opt.label}
        </button>
      ))}
    </div>
  )
}

export default function DecisionSection({ decision, additionalContext, services, onChange }) {
  const update = (field, value) => onChange({ ...decision, [field]: value }, additionalContext)

  const toggleService = (serviceId) => {
    const current = decision.affected_services || []
    const next = current.includes(serviceId)
      ? current.filter(id => id !== serviceId)
      : [...current, serviceId]
    update('affected_services', next)
  }

  return (
    <div className="px-5 space-y-3">
      <div>
        <label className="text-xs text-text-secondary block mb-1">Decision title *</label>
        <input
          type="text"
          placeholder="e.g. Migrating auth database to Aurora"
          value={decision.title}
          onChange={e => update('title', e.target.value)}
          className="w-full bg-bg border border-border rounded px-2.5 py-2 text-sm text-text-primary placeholder-text-secondary/50 focus:outline-none focus:border-accent transition-colors"
        />
      </div>

      <div>
        <label className="text-xs text-text-secondary block mb-1">Description</label>
        <textarea
          placeholder="What is being changed? What is the approach? What are the constraints?"
          value={decision.description}
          onChange={e => update('description', e.target.value)}
          rows={4}
          className="w-full bg-bg border border-border rounded px-2.5 py-2 text-sm text-text-secondary placeholder-text-secondary/50 focus:outline-none focus:border-accent transition-colors resize-none"
        />
      </div>

      <div>
        <label className="text-xs text-text-secondary block mb-1">Decision type</label>
        <select
          value={decision.decision_type}
          onChange={e => update('decision_type', e.target.value)}
          className="w-full bg-bg border border-border rounded px-2.5 py-2 text-sm text-text-primary focus:outline-none focus:border-accent transition-colors"
        >
          {DECISION_TYPES.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
        </select>
      </div>

      {services.length > 0 && (
        <div>
          <label className="text-xs text-text-secondary block mb-1.5">Directly affected services</label>
          <div className="flex flex-wrap gap-1.5">
            {services.map(s => {
              const selected = (decision.affected_services || []).includes(s.id)
              return (
                <button
                  key={s.id}
                  onClick={() => toggleService(s.id)}
                  className={`text-xs px-2.5 py-1 rounded-full border transition-colors ${
                    selected
                      ? 'bg-accent border-accent text-white font-medium'
                      : 'bg-bg border-border text-text-secondary hover:border-text-secondary'
                  }`}
                >
                  {s.name || s.id}
                </button>
              )
            })}
          </div>
        </div>
      )}

      <div>
        <label className="text-xs text-text-secondary block mb-1.5">Timeline</label>
        <SegmentedControl
          value={decision.timeline}
          onChange={v => update('timeline', v)}
          options={[
            { value: 'immediate', label: 'Immediate' },
            { value: 'weeks', label: 'Weeks' },
            { value: 'months', label: 'Months' },
            { value: 'quarters', label: 'Quarters' },
          ]}
        />
      </div>

      <div>
        <label className="text-xs text-text-secondary block mb-1.5">Reversibility</label>
        <SegmentedControl
          value={decision.reversibility}
          onChange={v => update('reversibility', v)}
          options={[
            { value: 'easy', label: 'Easy' },
            { value: 'moderate', label: 'Moderate' },
            { value: 'hard', label: 'Hard' },
            { value: 'irreversible', label: 'Irreversible' },
          ]}
        />
      </div>

      <div>
        <label className="text-xs text-text-secondary block mb-1">Additional context</label>
        <textarea
          placeholder="Add constraints, history, compliance considerations, or anything the form above doesn't capture. In production this field would be replaced by your incident history and change management data."
          value={additionalContext || ''}
          onChange={e => onChange(decision, e.target.value)}
          rows={3}
          className="w-full bg-bg border border-border rounded px-2.5 py-2 text-xs text-text-secondary placeholder-text-secondary/50 focus:outline-none focus:border-accent transition-colors resize-none"
        />
      </div>
    </div>
  )
}
