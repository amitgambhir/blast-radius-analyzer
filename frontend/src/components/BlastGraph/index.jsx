import { useEffect, useRef, useState, useCallback } from 'react'
import * as d3 from 'd3'
import NodeDrawer from '../NodeDrawer.jsx'
import { ZoomIn, ZoomOut, RotateCcw, Tag } from 'lucide-react'

const NODE_FILL = {
  decision: '#f0883e',
  direct: '#f85149',
  'second-order': '#e3b341',
  'third-order': '#58a6ff',
  team: '#58a6ff',
  process: '#6e7681',
  external: '#a371f7',
  unaffected: '#21262d',
}

const NODE_RADIUS = {
  critical: 20,
  high: 16,
  medium: 13,
  low: 11,
  none: 8,
}

function nodeColor(node) {
  if (node.type === 'decision') return NODE_FILL.decision
  if (node.type === 'team') return NODE_FILL.team
  if (node.type === 'process') return NODE_FILL.process
  if (node.type === 'external') return NODE_FILL.external
  if (node.impact_level === 'unaffected') return NODE_FILL.unaffected
  return NODE_FILL[node.impact_level] || '#8b949e'
}

function nodeRadius(node) {
  if (node.type === 'decision') return 22
  return NODE_RADIUS[node.risk_severity] || 10
}

const WIDTH = 700
const HEIGHT = 420

export default function BlastGraph({ nodes, edges }) {
  const svgRef = useRef(null)
  const zoomRef = useRef(null)
  const gRef = useRef(null)
  const [selectedNode, setSelectedNode] = useState(null)
  const [showLabels, setShowLabels] = useState(true)
  const [activeFilter, setActiveFilter] = useState(null)

  const buildGraph = useCallback(() => {
    if (!svgRef.current || !nodes?.length) return

    const svg = d3.select(svgRef.current)
    svg.selectAll('*').remove()

    // Defs
    const defs = svg.append('defs')
    defs.append('marker')
      .attr('id', 'arrow')
      .attr('viewBox', '0 -4 8 8')
      .attr('refX', 22)
      .attr('refY', 0)
      .attr('markerWidth', 5)
      .attr('markerHeight', 5)
      .attr('orient', 'auto')
      .append('path')
      .attr('d', 'M0,-4L8,0L0,4')
      .attr('fill', '#30363d')

    const glow = defs.append('filter').attr('id', 'node-glow')
    glow.append('feGaussianBlur').attr('stdDeviation', '3').attr('result', 'blur')
    const feMerge = glow.append('feMerge')
    feMerge.append('feMergeNode').attr('in', 'blur')
    feMerge.append('feMergeNode').attr('in', 'SourceGraphic')

    // Zoom
    const zoom = d3.zoom().scaleExtent([0.2, 4]).on('zoom', e => g.attr('transform', e.transform))
    zoomRef.current = zoom
    svg.call(zoom)

    const g = svg.append('g')
    gRef.current = g

    // Clone nodes for simulation (avoid mutating props)
    const simNodes = nodes.map(n => ({
      ...n,
      x: WIDTH / 2 + (Math.random() - 0.5) * 80,
      y: HEIGHT / 2 + (Math.random() - 0.5) * 80,
    }))

    // Fix decision node at center
    const decisionNode = simNodes.find(n => n.type === 'decision')
    if (decisionNode) {
      decisionNode.fx = WIDTH / 2
      decisionNode.fy = HEIGHT / 2
    }

    const nodeById = new Map(simNodes.map(n => [n.id, n]))

    const simEdges = edges
      .filter(e => nodeById.has(e.source) && nodeById.has(e.target))
      .map(e => ({ ...e }))

    const linkDistanceFn = (d) => {
      const src = nodeById.get(d.source?.id || d.source)
      const tgt = nodeById.get(d.target?.id || d.target)
      if (!src || !tgt) return 110
      if (src.impact_level === 'direct' || tgt.impact_level === 'direct') return 95
      if (src.impact_level === 'second-order' || tgt.impact_level === 'second-order') return 140
      return 170
    }

    const simulation = d3.forceSimulation(simNodes)
      .force('link', d3.forceLink(simEdges).id(d => d.id).distance(linkDistanceFn).strength(0.45))
      .force('charge', d3.forceManyBody().strength(-220))
      .force('center', d3.forceCenter(WIDTH / 2, HEIGHT / 2))
      .force('collision', d3.forceCollide().radius(d => nodeRadius(d) + 12))

    // Edges
    const link = g.append('g')
      .selectAll('line')
      .data(simEdges)
      .join('line')
      .attr('stroke', '#30363d')
      .attr('stroke-width', d => d.strength > 0.7 ? 2 : 1)
      .attr('stroke-dasharray', d => d.strength < 0.5 ? '5,3' : null)
      .attr('marker-end', 'url(#arrow)')
      .attr('opacity', 0.55)

    // Node groups
    const nodeGroup = g.append('g')
      .selectAll('g')
      .data(simNodes)
      .join('g')
      .attr('class', 'node')
      .style('cursor', 'pointer')
      .call(
        d3.drag()
          .on('start', (e, d) => { if (!e.active) simulation.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y })
          .on('drag', (e, d) => { d.fx = e.x; d.fy = e.y })
          .on('end', (e, d) => { if (!e.active) simulation.alphaTarget(0); if (d.type !== 'decision') { d.fx = null; d.fy = null } })
      )
      .on('click', (e, d) => { e.stopPropagation(); setSelectedNode(d) })

    // Pulse ring for decision node
    nodeGroup.filter(d => d.type === 'decision')
      .append('circle')
      .attr('r', d => nodeRadius(d) + 9)
      .attr('fill', 'none')
      .attr('stroke', '#f0883e')
      .attr('stroke-width', 1.5)
      .attr('opacity', 0.4)
      .attr('class', 'decision-pulse')

    // Main circles
    nodeGroup.append('circle')
      .attr('r', nodeRadius)
      .attr('fill', nodeColor)
      .attr('fill-opacity', d => d.impact_level === 'unaffected' ? 0.4 : 0.85)
      .attr('stroke', d => d3.color(nodeColor(d))?.brighter(0.6)?.toString() || '#fff')
      .attr('stroke-width', 1.5)
      .attr('filter', d => d.type === 'decision' ? 'url(#node-glow)' : null)

    // Inferred marker
    nodeGroup.filter(d => d.is_inferred)
      .append('text')
      .attr('text-anchor', 'middle')
      .attr('dy', '0.35em')
      .attr('font-size', '7px')
      .attr('fill', 'rgba(255,255,255,0.5)')
      .attr('pointer-events', 'none')
      .text('◈')

    // Labels
    nodeGroup.append('text')
      .attr('class', 'node-label')
      .attr('text-anchor', 'middle')
      .attr('dy', d => nodeRadius(d) + 13)
      .attr('font-size', '9.5px')
      .attr('fill', '#6e7681')
      .attr('pointer-events', 'none')
      .text(d => d.name?.length > 20 ? d.name.slice(0, 18) + '…' : d.name)

    // Tooltip
    const tooltip = d3.select('body')
      .selectAll('.bra-tooltip')
      .data([null])
      .join('div')
      .attr('class', 'bra-tooltip')
      .style('position', 'fixed')
      .style('background', '#161b22')
      .style('border', '1px solid #30363d')
      .style('border-radius', '8px')
      .style('padding', '10px 14px')
      .style('font-family', '"IBM Plex Sans", sans-serif')
      .style('font-size', '12px')
      .style('color', '#e6edf3')
      .style('pointer-events', 'none')
      .style('opacity', 0)
      .style('max-width', '280px')
      .style('z-index', '9999')
      .style('box-shadow', '0 8px 24px rgba(0,0,0,0.6)')
      .style('line-height', '1.5')

    nodeGroup
      .on('mouseenter', (e, d) => {
        const color = nodeColor(d)
        tooltip.transition().duration(120).style('opacity', 1)
        tooltip.html(`
          <div style="font-weight:600;color:${color};margin-bottom:3px">${d.name}</div>
          <div style="color:#8b949e;font-size:11px;margin-bottom:5px">${d.type} · ${d.impact_level} · <span style="color:${color}">${d.risk_severity}</span></div>
          <div style="color:#e6edf3;line-height:1.5">${(d.impact_description || '').slice(0, 130)}${(d.impact_description || '').length > 130 ? '…' : ''}</div>
          ${d.is_inferred ? '<div style="color:#6e7681;margin-top:5px;font-size:10px">◈ inferred node</div>' : ''}
          <div style="color:#6e7681;margin-top:4px;font-size:10px">Click for full details</div>
        `)
      })
      .on('mousemove', (e) => {
        tooltip.style('left', (e.clientX + 15) + 'px').style('top', (e.clientY - 8) + 'px')
      })
      .on('mouseleave', () => {
        tooltip.transition().duration(200).style('opacity', 0)
      })

    simulation.on('tick', () => {
      link
        .attr('x1', d => d.source.x)
        .attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x)
        .attr('y2', d => d.target.y)
      nodeGroup.attr('transform', d => `translate(${d.x},${d.y})`)
    })

    svg.on('click', () => setSelectedNode(null))

    return () => {
      simulation.stop()
      tooltip.remove()
    }
  }, [nodes, edges])

  useEffect(() => {
    const cleanup = buildGraph()
    return cleanup
  }, [buildGraph])

  useEffect(() => {
    if (!gRef.current) return
    gRef.current.selectAll('.node-label').style('display', showLabels ? null : 'none')
  }, [showLabels])

  useEffect(() => {
    if (!gRef.current) return
    gRef.current.selectAll('.node').style('opacity', d =>
      activeFilter ? (d.risk_severity === activeFilter ? 1 : 0.15) : 1
    )
  }, [activeFilter])

  const zoomBy = (factor) => {
    if (svgRef.current && zoomRef.current)
      d3.select(svgRef.current).transition().duration(300).call(zoomRef.current.scaleBy, factor)
  }

  const resetView = () => {
    if (svgRef.current && zoomRef.current)
      d3.select(svgRef.current).transition().duration(400).call(zoomRef.current.transform, d3.zoomIdentity)
  }

  const FILTERS = [
    { sev: 'critical', color: '#f85149' },
    { sev: 'high', color: '#e3b341' },
    { sev: 'medium', color: '#58a6ff' },
    { sev: 'low', color: '#3fb950' },
  ]

  const LEGEND = [
    { color: '#f0883e', label: 'Decision' },
    { color: '#f85149', label: 'Direct' },
    { color: '#e3b341', label: '2nd order' },
    { color: '#58a6ff', label: 'Org/team' },
    { color: '#30363d', label: 'Unaffected' },
  ]

  return (
    <div>
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-sm font-semibold text-text-primary">Impact Graph</h3>
        <div className="flex items-center gap-3">
          {/* Severity filter chips */}
          <div className="flex items-center gap-1">
            {FILTERS.map(({ sev, color }) => (
              <button
                key={sev}
                onClick={() => setActiveFilter(activeFilter === sev ? null : sev)}
                className="text-xs px-2 py-0.5 rounded-full border transition-all"
                style={
                  activeFilter === sev
                    ? { backgroundColor: color, borderColor: color, color: '#fff' }
                    : { borderColor: '#30363d', color: '#8b949e' }
                }
              >
                {sev}
              </button>
            ))}
          </div>
          {/* Controls */}
          <div className="flex items-center border border-border rounded overflow-hidden">
            <button onClick={() => zoomBy(1.4)} title="Zoom in" className="p-1.5 text-text-secondary hover:text-text-primary hover:bg-surface transition-colors">
              <ZoomIn size={12} />
            </button>
            <button onClick={() => zoomBy(0.7)} title="Zoom out" className="p-1.5 text-text-secondary hover:text-text-primary hover:bg-surface transition-colors border-x border-border">
              <ZoomOut size={12} />
            </button>
            <button onClick={resetView} title="Reset" className="p-1.5 text-text-secondary hover:text-text-primary hover:bg-surface transition-colors border-r border-border">
              <RotateCcw size={12} />
            </button>
            <button
              onClick={() => setShowLabels(l => !l)}
              title="Toggle labels"
              className={`p-1.5 transition-colors hover:bg-surface ${showLabels ? 'text-accent' : 'text-text-secondary hover:text-text-primary'}`}
            >
              <Tag size={12} />
            </button>
          </div>
        </div>
      </div>

      {/* Legend */}
      <div className="flex items-center gap-3 mb-2 flex-wrap">
        {LEGEND.map(({ color, label }) => (
          <div key={label} className="flex items-center gap-1.5 text-xs text-text-secondary">
            <div className="w-2.5 h-2.5 rounded-full flex-shrink-0" style={{ backgroundColor: color }} />
            {label}
          </div>
        ))}
      </div>

      <div className="border border-border rounded-lg overflow-hidden bg-bg">
        <svg
          ref={svgRef}
          width={WIDTH}
          height={HEIGHT}
          className="w-full block"
          style={{ height: `${HEIGHT}px` }}
        />
      </div>

      {selectedNode && selectedNode.type !== 'decision' && (
        <NodeDrawer node={selectedNode} onClose={() => setSelectedNode(null)} />
      )}
    </div>
  )
}
