import { useState } from 'react'
import { Plus, Trash2, ArrowRight } from 'lucide-react'

const DEP_TYPES = ['sync-api', 'async-event', 'database', 'shared-library']
const DEP_COLORS = {
  'sync-api': '#f85149',
  'async-event': '#e3b341',
  'database': '#58a6ff',
  'shared-library': '#3fb950',
}

export default function DependenciesSection({ dependencies, services, onChange }) {
  const [form, setForm] = useState({
    from_service: '',
    to_service: '',
    dependency_type: 'sync-api',
    strength: 'hard',
  })

  if (services.length < 2) {
    return (
      <div className="px-5 py-3 text-xs text-text-secondary/60 italic">
        Add at least 2 services to define dependencies.
      </div>
    )
  }

  const addDep = () => {
    if (!form.from_service || !form.to_service || form.from_service === form.to_service) return
    const exists = dependencies.some(
      d => d.from_service === form.from_service && d.to_service === form.to_service
    )
    if (exists) return
    onChange([...dependencies, { ...form }])
    setForm(f => ({ ...f, from_service: '', to_service: '' }))
  }

  const removeDep = (i) => onChange(dependencies.filter((_, idx) => idx !== i))

  return (
    <div className="px-5 space-y-3">
      {/* Builder */}
      <div className="bg-surface border border-border rounded-lg p-3">
        <div className="flex flex-wrap items-end gap-2">
          <div className="flex-1 min-w-20">
            <label className="text-xs text-text-secondary block mb-1">From</label>
            <select
              value={form.from_service}
              onChange={e => setForm(f => ({ ...f, from_service: e.target.value }))}
              className="w-full bg-bg border border-border rounded px-2 py-1.5 text-xs text-text-primary focus:outline-none focus:border-accent"
            >
              <option value="">Select…</option>
              {services.map(s => <option key={s.id} value={s.id}>{s.name || s.id}</option>)}
            </select>
          </div>
          <ArrowRight size={13} className="text-text-secondary mb-2 flex-shrink-0" />
          <div className="flex-1 min-w-20">
            <label className="text-xs text-text-secondary block mb-1">To</label>
            <select
              value={form.to_service}
              onChange={e => setForm(f => ({ ...f, to_service: e.target.value }))}
              className="w-full bg-bg border border-border rounded px-2 py-1.5 text-xs text-text-primary focus:outline-none focus:border-accent"
            >
              <option value="">Select…</option>
              {services.filter(s => s.id !== form.from_service).map(s => (
                <option key={s.id} value={s.id}>{s.name || s.id}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="text-xs text-text-secondary block mb-1">Type</label>
            <select
              value={form.dependency_type}
              onChange={e => setForm(f => ({ ...f, dependency_type: e.target.value }))}
              className="bg-bg border border-border rounded px-2 py-1.5 text-xs text-text-primary focus:outline-none focus:border-accent"
            >
              {DEP_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
            </select>
          </div>
          <div>
            <label className="text-xs text-text-secondary block mb-1">Strength</label>
            <select
              value={form.strength}
              onChange={e => setForm(f => ({ ...f, strength: e.target.value }))}
              className="bg-bg border border-border rounded px-2 py-1.5 text-xs text-text-primary focus:outline-none focus:border-accent"
            >
              <option value="hard">Hard</option>
              <option value="soft">Soft</option>
            </select>
          </div>
          <button
            onClick={addDep}
            disabled={!form.from_service || !form.to_service || form.from_service === form.to_service}
            className="flex items-center gap-1 px-2.5 py-1.5 bg-accent hover:bg-[#d97730] disabled:opacity-40 disabled:cursor-not-allowed text-white rounded text-xs font-medium transition-colors"
          >
            <Plus size={12} />
            Add
          </button>
        </div>
      </div>

      {/* List */}
      {dependencies.length > 0 && (
        <div className="space-y-1.5">
          {dependencies.map((dep, i) => (
            <div key={i} className="flex items-center gap-2 bg-surface border border-border rounded px-3 py-2">
              <span className="text-xs font-mono text-text-primary truncate max-w-[100px]">{dep.from_service}</span>
              <ArrowRight size={10} className="text-text-secondary flex-shrink-0" />
              <span className="text-xs font-mono text-text-primary truncate max-w-[100px]">{dep.to_service}</span>
              <span className="text-xs ml-1 flex-shrink-0" style={{ color: DEP_COLORS[dep.dependency_type] }}>
                {dep.dependency_type}
              </span>
              <span className="text-xs text-text-secondary/60 flex-shrink-0">·</span>
              <span className={`text-xs flex-shrink-0 ${dep.strength === 'hard' ? 'text-high' : 'text-text-secondary'}`}>
                {dep.strength}
              </span>
              <button
                onClick={() => removeDep(i)}
                className="text-text-secondary hover:text-critical transition-colors ml-auto flex-shrink-0"
              >
                <Trash2 size={11} />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
