import React from 'react'
import { Cell, Legend, Pie, PieChart, ResponsiveContainer, Tooltip } from 'recharts'
import { mockStats } from '../data/mock'

const colors = ['#7c3aed', '#10b981', '#f59e0b', '#ef4444', '#0ea5e9']

type HygieneChartsProps = {
  data?: typeof mockStats.issuesByCategory
}

export const HygieneCharts: React.FC<HygieneChartsProps> = ({ data = mockStats.issuesByCategory }) => {
  return (
    <div className="card p-4 h-full">
      <h3 className="text-lg font-semibold mb-3">Issue Categories</h3>
      <div className="h-64">
        <ResponsiveContainer>
          <PieChart>
            <Pie data={data} dataKey="value" nameKey="name" outerRadius="80%" label>
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
              ))}
            </Pie>
            <Tooltip />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
