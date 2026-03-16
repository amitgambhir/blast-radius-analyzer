import { Plus, Trash2 } from 'lucide-react'

const CRITICALITY_COLORS = {
  critical: 'text-critical',
  high: 'text-high',
  medium: 'text-medium',
  low: 'text-low',
}

function slugify(str) {
  return str.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '')
}

export default function ServicesSection({ services, onChange }) {
  const update = (index, field, value) => {
    const updated = services.map((s, i) => {
      if (i !== index) return s
      const next = { ...s, [field]: value }
      // Auto-generate id from name if id hasn't been manually set
      if (field === 'name' && !s._idManuallySet) {
        next.id = slugify(value)
      }
      if (field === 'id') {
        next._idManuallySet = true
      }
      return next
    })
    onChange(updated)
  }

  const addService = () => {
    onChange([...services, { id: '', name: '', owner_team: '', criticality: 'medium', description: '' }])
  }

  const removeService = (index) => {
    onChange(services.filter((_, i) => i !== index))
  }

  return (
    <div className="px-5 space-y-3">
      {services.map((service, i) => (
        <div key={i} className="bg-surface border border-border rounded-lg p-3 space-y-2">
          <div className="flex items-center gap-2">
            <input
              type="text"
              placeholder="Service name"
              value={service.name}
              onChange={e => update(i, 'name', e.target.value)}
              className="flex-1 bg-bg border border-border rounded px-2.5 py-1.5 text-sm text-text-primary placeholder-text-secondary/50 focus:outline-none focus:border-accent transition-colors"
            />
            <select
              value={service.criticality}
              onChange={e => update(i, 'criticality', e.target.value)}
              className={`bg-bg border border-border rounded px-2 py-1.5 text-xs focus:outline-none focus:border-accent ${CRITICALITY_COLORS[service.criticality]}`}
            >
              <option value="critical">Critical</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </select>
            <button
              onClick={() => removeService(i)}
              className="text-text-secondary hover:text-critical transition-colors p-1 flex-shrink-0"
            >
              <Trash2 size={13} />
            </button>
          </div>
          <div className="flex gap-2">
            <input
              type="text"
              placeholder="id (e.g. auth-service)"
              value={service.id}
              onChange={e => update(i, 'id', e.target.value)}
              className="w-36 bg-bg border border-border rounded px-2.5 py-1.5 text-xs font-mono text-text-secondary placeholder-text-secondary/50 focus:outline-none focus:border-accent transition-colors"
            />
            <input
              type="text"
              placeholder="Owner team"
              value={service.owner_team}
              onChange={e => update(i, 'owner_team', e.target.value)}
              className="flex-1 bg-bg border border-border rounded px-2.5 py-1.5 text-xs text-text-secondary placeholder-text-secondary/50 focus:outline-none focus:border-accent transition-colors"
            />
          </div>
          <textarea
            placeholder="What does this service do? (be specific for better analysis)"
            value={service.description}
            onChange={e => update(i, 'description', e.target.value)}
            rows={2}
            className="w-full bg-bg border border-border rounded px-2.5 py-1.5 text-xs text-text-secondary placeholder-text-secondary/50 focus:outline-none focus:border-accent transition-colors resize-none"
          />
        </div>
      ))}
      <button
        onClick={addService}
        className="flex items-center gap-1.5 text-xs text-text-secondary hover:text-accent transition-colors py-1"
      >
        <Plus size={13} />
        Add service
      </button>
    </div>
  )
}
