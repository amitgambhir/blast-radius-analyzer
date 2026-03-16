import VerdictBanner from './VerdictBanner.jsx'
import RiskDimensions from './RiskDimensions.jsx'
import OrgImpact from './OrgImpact.jsx'
import ImmediateActions from './ImmediateActions.jsx'
import OpenQuestions from './OpenQuestions.jsx'
import ConfidenceNote from './ConfidenceNote.jsx'
import AnalysisLog from './AnalysisLog.jsx'
import ExportButton from './ExportButton.jsx'
import BlastGraph from '../BlastGraph/index.jsx'

export default function ResultsPanel({ result, passes }) {
  const teamNodes = result.nodes.filter(n => n.type === 'team' || n.type === 'process' || n.type === 'external')

  return (
    <div className="p-6 space-y-6 fade-in">
      <VerdictBanner
        verdict={result.overall_verdict}
        score={result.overall_risk_score}
        summary={result.executive_summary}
        title={result.decision_title}
      />

      <BlastGraph nodes={result.nodes} edges={result.edges} />

      <RiskDimensions dimensions={result.risk_dimensions} />

      {teamNodes.length > 0 && <OrgImpact nodes={teamNodes} />}

      <ImmediateActions actions={result.immediate_actions} />

      <OpenQuestions questions={result.questions_to_answer} />

      <ConfidenceNote note={result.confidence_note} nodes={result.nodes} />

      <div className="flex justify-end">
        <ExportButton result={result} />
      </div>

      <AnalysisLog passes={result.analysis_passes} />
    </div>
  )
}
