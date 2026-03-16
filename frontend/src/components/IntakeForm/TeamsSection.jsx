import { Plus, Trash2 } from 'lucide-react'

const FOCUS_OPTIONS = ['platform', 'product', 'data', 'security', 'other']

function slugify(str) {
  return str.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '')
}

export default function TeamsSection({ teams, services, onChange }) {
  const update = (index, field, value) => {
    onChange(teams.map((t, i) => {
      if (i !== index) return t
      const next = { ...t, [field]: value }
      if (field === 'name' && !t._idManuallySet) {
        next.id = slugify(value)
      }
      if (field === 'id') {
        next._idManuallySet = true
      }
      return next
    }))
  }

  const toggleOwns = (index, serviceId) => {
    const team = teams[index]
    const current = team.owns || []
    const next = current.includes(serviceId)
      ? current.filter(id => id !== serviceId)
      : [...current, serviceId]
    update(index, 'owns', next)
  }

  const addTeam = () => {
    onChange([...teams, { id: '', name: '', owns: [], size: 5, focus: 'product' }])
  }

  const removeTeam = (index) => {
    onChange(teams.filter((_, i) => i !== index))
  }

  return (
    <div className="px-5 space-y-3">
      {teams.map((team, i) => (
        <div key={i} className="bg-surface border border-border rounded-lg p-3 space-y-2">
          <div className="flex items-center gap-2">
            <input
              type="text"
              placeholder="Team name"
              value={team.name}
              onChange={e => update(i, 'name', e.target.value)}
              className="flex-1 bg-bg border border-border rounded px-2.5 py-1.5 text-sm text-text-primary placeholder-text-secondary/50 focus:outline-none focus:border-accent transition-colors"
            />
            <select
              value={team.focus}
              onChange={e => update(i, 'focus', e.target.value)}
              className="bg-bg border border-border rounded px-2 py-1.5 text-xs text-text-secondary focus:outline-none focus:border-accent"
            >
              {FOCUS_OPTIONS.map(f => <option key={f} value={f}>{f}</option>)}
            </select>
            <button
              onClick={() => removeTeam(i)}
              className="text-text-secondary hover:text-critical transition-colors p-1 flex-shrink-0"
            >
              <Trash2 size={13} />
            </button>
          </div>

          <div className="flex items-center gap-2">
            <input
              type="text"
              placeholder="id (e.g. platform)"
              value={team.id}
              onChange={e => update(i, 'id', e.target.value)}
              className="w-36 bg-bg border border-border rounded px-2.5 py-1.5 text-xs font-mono text-text-secondary placeholder-text-secondary/50 focus:outline-none focus:border-accent transition-colors"
            />
            <div className="flex items-center gap-1.5">
              <label className="text-xs text-text-secondary whitespace-nowrap">Size</label>
              <input
                type="number"
                min={1}
                max={200}
                value={team.size}
                onChange={e => update(i, 'size', parseInt(e.target.value) || 1)}
                className="w-14 bg-bg border border-border rounded px-2 py-1.5 text-xs text-text-secondary focus:outline-none focus:border-accent text-center"
              />
            </div>
          </div>

          {services.length > 0 && (
            <div>
              <p className="text-xs text-text-secondary mb-1.5">Owns services</p>
              <div className="flex flex-wrap gap-1.5">
                {services.map(s => {
                  const owned = (team.owns || []).includes(s.id)
                  return (
                    <button
                      key={s.id}
                      onClick={() => toggleOwns(i, s.id)}
                      className={`text-xs px-2 py-0.5 rounded-full border transition-colors ${
                        owned
                          ? 'bg-medium/20 border-medium/50 text-medium'
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
        </div>
      ))}

      <button
        onClick={addTeam}
        className="flex items-center gap-1.5 text-xs text-text-secondary hover:text-accent transition-colors py-1"
      >
        <Plus size={13} />
        Add team
      </button>
    </div>
  )
}
