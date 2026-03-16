export default function ConfidenceNote({ note, nodes }) {
  const inferredCount = nodes?.filter(n => n.is_inferred).length ?? 0
  return (
    <div className="border border-border/40 rounded-lg p-3 bg-surface/20">
      <div className="flex items-start gap-2">
        <span className="text-text-secondary flex-shrink-0 mt-0.5">◈</span>
        <div>
          <p className="text-xs text-text-secondary leading-relaxed">{note}</p>
          {inferredCount > 0 && (
            <p className="text-xs text-text-secondary/50 mt-1">
              {inferredCount} node{inferredCount !== 1 ? 's' : ''} in this analysis are marked ◈ (inferred beyond explicit intake data).
            </p>
          )}
        </div>
      </div>
    </div>
  )
}
