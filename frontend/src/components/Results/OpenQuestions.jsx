import { useState } from 'react'
import { Copy, CheckCheck } from 'lucide-react'

function QuestionRow({ q }) {
  const [copied, setCopied] = useState(false)
  return (
    <div className="flex items-start gap-2.5 py-2 border-b border-border last:border-0">
      <div className="w-4 h-4 border border-border rounded mt-0.5 flex-shrink-0" />
      <span className="text-sm text-text-secondary flex-1 leading-relaxed">{q}</span>
      <button
        onClick={() => { navigator.clipboard.writeText(q); setCopied(true); setTimeout(() => setCopied(false), 2000) }}
        className="text-text-secondary hover:text-accent transition-colors flex-shrink-0"
      >
        {copied ? <CheckCheck size={11} className="text-low" /> : <Copy size={11} />}
      </button>
    </div>
  )
}

export default function OpenQuestions({ questions }) {
  if (!questions?.length) return null
  return (
    <div>
      <div className="flex items-center gap-2 mb-3">
        <h3 className="text-sm font-semibold text-text-primary">Open Questions</h3>
        <span className="text-xs text-text-secondary">— answer before proceeding</span>
      </div>
      <div className="bg-surface border border-border rounded-lg px-4 py-1">
        {questions.map((q, i) => <QuestionRow key={i} q={q} />)}
      </div>
    </div>
  )
}
