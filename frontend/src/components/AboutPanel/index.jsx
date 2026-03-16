import { useState } from 'react'
import { X } from 'lucide-react'

const ASCII_PIPELINE = `  BlastRadiusRequest
         │
         ▼
  ┌─────────────┐
  │   Pass 1    │  Decision Classification
  │    (AI)     │  → decision_class, primary_risk,
  └──────┬──────┘    playbook_notes
         │
         ▼
  ┌─────────────┐
  │  NetworkX   │  Build nx.DiGraph from intake
  │   Graph     │  get_first_order()  → 1-hop
  │  Traversal  │  get_second_order() → 2-hop
  └──────┬──────┘  betweenness_centrality()
         │
         ▼
  ┌─────────────┐
  │   Pass 2    │  First-Order Technical Impact
  │    (AI)     │  → ImpactNode[] per neighbor
  └──────┬──────┘    grounded in real graph
         │
         ▼
  ┌─────────────┐
  │   Pass 3    │  Second-Order Propagation
  │    (AI)     │  → dampened vs amplified
  └──────┬──────┘
         │
         ▼
  ┌─────────────┐
  │   Pass 4    │  Organizational Impact
  │    (AI)     │  → team workload, SLA risk,
  └──────┬──────┘    roadmap disruption
         │
         ▼
  ┌─────────────┐
  │   Pass 5    │  Risk Scoring & Synthesis
  │    (AI)     │  → BlastRadiusResult
  └──────┬──────┘
         │
         ▼
  D3 Force Graph + Scorecards + Export`

function Tab({ label, active, onClick }) {
  return (
    <button
      onClick={onClick}
      className={`px-4 py-2.5 text-sm font-medium border-b-2 transition-colors ${
        active ? 'border-accent text-accent' : 'border-transparent text-text-secondary hover:text-text-primary'
      }`}
    >
      {label}
    </button>
  )
}

function DataTable({ headers, rows }) {
  return (
    <div className="overflow-x-auto my-3 rounded-lg border border-border">
      <table className="w-full text-xs">
        <thead>
          <tr className="border-b border-border bg-surface">
            {headers.map(h => (
              <th key={h} className="text-left px-3 py-2 text-text-secondary font-semibold">{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, i) => (
            <tr key={i} className="border-b border-border last:border-0 hover:bg-surface/50 transition-colors">
              {row.map((cell, j) => (
                <td key={j} className="px-3 py-2.5 text-text-primary leading-relaxed">{cell}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

function HowItWorks() {
  return (
    <div className="space-y-5 text-sm">
      <div>
        <h3 className="text-base font-semibold text-text-primary mb-2">5-Pass AI Reasoning Chain</h3>
        <p className="text-text-secondary leading-relaxed">
          Each analysis runs five sequential model passes. Every pass receives the structured JSON output of all previous passes as context. Pass 5 has seen everything Passes 1–4 found. This produces dramatically better output than a single mega-prompt.
        </p>
      </div>

      <pre className="bg-bg border border-border rounded-lg p-4 text-xs font-mono text-text-secondary overflow-x-auto leading-[1.6] whitespace-pre">
        {ASCII_PIPELINE}
      </pre>

      <div className="space-y-4">
        {[
          {
            n: 1, name: 'Decision Classification',
            desc: 'Classifies the decision type, identifies the primary risk category, and determines which analysis approach to apply. Output informs all subsequent passes.',
          },
          {
            n: 2, name: 'First-Order Impact (Graph-Traversal Assisted)',
            desc: 'NetworkX builds a real nx.DiGraph from intake data. get_first_order() computes all 1-hop neighbors algorithmically. The model then reasons about the specific technical impact on each neighbor — interpreting a real graph structure, not guessing at dependencies.',
          },
          {
            n: 3, name: 'Second-Order Propagation',
            desc: 'get_second_order() extends traversal to 2-hop neighbors. The model reasons about whether each impact signal is dampened (soft/async dependency) or amplified (hard/sync dependency) as it propagates.',
          },
          {
            n: 4, name: 'Organizational Impact Mapping',
            desc: 'The differentiator pass. Most tools stop at technical impact. This pass maps technical impacts to human and organizational impacts: team workload, roadmap disruption, SLA risk, stakeholder commitments, and communication overhead. It\'s what a Staff Engineer or EM actually needs to know.',
          },
          {
            n: 5, name: 'Risk Scoring and Synthesis',
            desc: 'Scores five dimensions (technical, delivery, people, compliance, financial) 0–100. Computes overall verdict. Writes executive summary. Generates immediate actions and open questions. Produces the complete BlastRadiusResult.',
          },
        ].map(({ n, name, desc }) => (
          <div key={n} className="flex gap-3">
            <span className="font-mono text-accent font-bold text-sm flex-shrink-0 w-5">{n}</span>
            <div>
              <p className="font-semibold text-text-primary mb-1">{name}</p>
              <p className="text-text-secondary text-xs leading-relaxed">{desc}</p>
            </div>
          </div>
        ))}
      </div>

      <div className="bg-surface border border-border rounded-lg p-4">
        <h4 className="font-semibold text-text-primary mb-2 text-sm">Why NetworkX?</h4>
        <p className="text-text-secondary text-xs leading-relaxed">
          The dependency graph is a real <code className="font-mono text-accent bg-bg px-1 py-0.5 rounded">nx.DiGraph</code>. Hop-distance propagation, betweenness centrality, and dependency strength weighting are computed algorithmically before the model reasons about them. This is not the model guessing — it is graph traversal producing structured input that the model interprets. In production, a Terraform graph parser or Datadog service map replaces the intake form. The traversal code is identical.
        </p>
      </div>
    </div>
  )
}

function PocVsProduction() {
  return (
    <div className="space-y-7 text-sm">
      <div className="border border-accent/25 bg-accent/5 rounded-lg p-4">
        <p className="text-text-primary font-medium mb-1">This tab is a product requirements document.</p>
        <p className="text-text-secondary text-xs leading-relaxed">
          Every person evaluating this tool should read it. The answers below are specific and honest about what this POC is, what production requires, and why the gap is bridgeable.
        </p>
      </div>

      {/* Q1 */}
      <div>
        <h3 className="font-semibold text-text-primary mb-2">
          Q1: The context I enter manually — how would that be automated in production?
        </h3>
        <DataTable
          headers={['What you enter manually', 'Production replacement']}
          rows={[
            ['Service list + descriptions', 'Backstage / OpsLevel service catalog API'],
            ['Service dependencies', 'Terraform/CloudFormation parsed graph, Datadog service map'],
            ['Team ownership', 'Workday org chart API, PagerDuty escalation policies'],
            ['Historical incidents', 'PagerDuty / OpsGenie incident history API'],
            ['SLA commitments', 'Internal SLA registry, Confluence/Notion page'],
          ]}
        />
        <p className="text-text-secondary text-xs leading-relaxed">
          Each of these is a well-understood integration. The intake form is a product requirements document for those integrations, not a limitation of the approach.
        </p>
      </div>

      {/* Q2 */}
      <div>
        <h3 className="font-semibold text-text-primary mb-2">
          Q2: How does graph traversal work without a real dependency map?
        </h3>
        <p className="text-text-secondary leading-relaxed text-xs">
          The dependencies you define in the intake form are used to build a real <code className="font-mono text-accent bg-bg px-1 rounded">nx.DiGraph</code>. The traversal logic — hop-distance propagation, betweenness centrality, dependency strength weighting — is production-ready as built. Only the data source changes in production. A Terraform parser or Datadog service map API replaces the form; the <code className="font-mono text-accent bg-bg px-1 rounded">get_first_order()</code> and <code className="font-mono text-accent bg-bg px-1 rounded">get_second_order()</code> functions are identical.
        </p>
      </div>

      {/* Q3 */}
      <div>
        <h3 className="font-semibold text-text-primary mb-2">
          Q3: What stops this from producing generic AI output?
        </h3>
        <div className="space-y-2">
          {[
            {
              n: '1',
              title: 'Structured intake forces specificity',
              desc: "Analysis is grounded in your services, your teams, and your decision. The model cannot hallucinate a dependency that isn't in the graph.",
            },
            {
              n: '2',
              title: 'Multi-pass reasoning',
              desc: 'Each pass receives structured output of all previous passes. Pass 5 has seen everything Passes 1–4 found. The final synthesis is not a single prompt — it\'s the end of a reasoning chain.',
            },
            {
              n: '3',
              title: 'NetworkX computes impact propagation before the model reasons about it',
              desc: 'Before the model touches second-order impacts, the system has already computed which services are 1 and 2 hops away. The model interprets a real graph structure.',
            },
          ].map(({ n, title, desc }) => (
            <div key={n} className="flex gap-3 bg-surface border border-border rounded-lg p-3">
              <span className="font-mono text-accent font-bold flex-shrink-0">{n}.</span>
              <div>
                <p className="font-medium text-text-primary mb-0.5 text-xs">{title}</p>
                <p className="text-text-secondary text-xs leading-relaxed">{desc}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Q4 */}
      <div>
        <h3 className="font-semibold text-text-primary mb-2">
          Q4: How would stale context be handled in production?
        </h3>
        <p className="text-text-secondary text-xs leading-relaxed">
          Every node would carry a <code className="font-mono text-accent bg-bg px-1 rounded">last_updated</code> timestamp from its source integration. The UI would surface staleness warnings: <em>"Service X was last synced 47 days ago — verify before relying on this analysis."</em> The POC addresses this with the confidence note on every analysis output and the ◈ marker on inferred nodes.
        </p>
      </div>

      {/* Q5 */}
      <div>
        <h3 className="font-semibold text-text-primary mb-2">
          Q5: What is the honest limitation of this POC?
        </h3>
        <div className="border border-high/25 bg-high/5 rounded-lg p-4">
          <p className="text-text-primary text-xs leading-relaxed mb-2">
            Output quality is proportional to context quality. Vague service descriptions and incomplete dependencies produce vague analysis.
          </p>
          <p className="text-text-secondary text-xs leading-relaxed">
            The tool is designed to make this visible — every inferred node is marked ◈ and the confidence note is always present. The analysis engine, graph traversal, visualization, and 5-pass reasoning chain are production-ready. The data layer is what a real deployment replaces.
          </p>
        </div>
      </div>

      {/* Q6 */}
      <div>
        <h3 className="font-semibold text-text-primary mb-2">
          Q6: What would a production deployment roadmap look like?
        </h3>
        <DataTable
          headers={['Phase', 'What changes', 'Status']}
          rows={[
            ['Phase 1 — POC (this repo)', 'Manual intake → analysis engine → graph UI', '✅ Complete'],
            ['Phase 2 — Integration', 'Backstage API replaces service/dependency intake', '🔷 Scoped'],
            ['Phase 3 — Intelligence', 'PagerDuty history enables pattern-matched risk', '🔷 Scoped'],
            ['Phase 4 — Workflow', 'Jira/Confluence export, change management hooks', '📋 Planned'],
            ['Phase 5 — Continuous', 'CI/CD hook — auto-analyze every arch decision', '📋 Planned'],
          ]}
        />
        <div className="border border-low/25 bg-low/5 rounded-lg p-4 mt-3">
          <p className="text-text-primary font-medium text-sm mb-1">Phase 1 is fully functional today.</p>
          <p className="text-text-secondary text-xs leading-relaxed">
            Phases 2–5 are well-scoped engineering work, not research problems. The hard architectural decisions are already made: the analysis engine, graph model, SSE streaming, and multi-pass reasoning chain are designed for production data. The only thing that changes per phase is the data source for each intake field.
          </p>
        </div>
      </div>
    </div>
  )
}

export default function AboutPanel({ onClose }) {
  const [tab, setTab] = useState('how')

  return (
    <div className="fixed inset-0 z-50 flex" onClick={onClose}>
      <div className="flex-1 bg-black/40" />
      <div
        className="w-[560px] bg-surface border-l border-border flex flex-col overflow-hidden slide-in-right"
        onClick={e => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-border flex-shrink-0">
          <div>
            <h2 className="font-semibold text-text-primary">💥 Blast Radius Analyzer</h2>
            <p className="text-xs text-text-secondary mt-0.5">How it works and what comes next</p>
          </div>
          <button onClick={onClose} className="text-text-secondary hover:text-text-primary transition-colors">
            <X size={17} />
          </button>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-border flex-shrink-0 px-6">
          <Tab label="How It Works" active={tab === 'how'} onClick={() => setTab('how')} />
          <Tab label="POC vs Production" active={tab === 'poc'} onClick={() => setTab('poc')} />
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {tab === 'how' ? <HowItWorks /> : <PocVsProduction />}
        </div>
      </div>
    </div>
  )
}
