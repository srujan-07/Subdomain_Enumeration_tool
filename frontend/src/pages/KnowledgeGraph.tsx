import React from 'react'
import { GraphView } from '../components/GraphView'

export const KnowledgeGraph: React.FC = () => {
  return (
    <div className="space-y-4">
      <div className="card p-4">
        <h3 className="text-lg font-semibold">Defect Knowledge Graph</h3>
        <p className="text-sm text-slate-600">Interactive view of Page → Issue relationships.</p>
      </div>
      <GraphView />
    </div>
  )
}
