import React from 'react'
import ReactFlow, { Background, Controls, MiniMap } from 'reactflow'
import 'reactflow/dist/style.css'
import { mockGraphEdges, mockGraphNodes } from '../data/mock'

type GraphViewProps = {
  nodes?: typeof mockGraphNodes
  edges?: typeof mockGraphEdges
}

export const GraphView: React.FC<GraphViewProps> = ({ nodes = mockGraphNodes, edges = mockGraphEdges }) => {
  return (
    <div className="card h-[520px] p-2">
      <div className="px-2 pt-2 pb-1 text-sm font-semibold text-slate-700">Defect Knowledge Graph</div>
      <div className="h-full">
        <ReactFlow nodes={nodes} edges={edges} fitView>
          <MiniMap pannable zoomable />
          <Controls />
          <Background gap={16} color="#e2e8f0" />
        </ReactFlow>
      </div>
    </div>
  )
}
