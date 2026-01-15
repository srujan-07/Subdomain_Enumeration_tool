import React from 'react'
import { RadialBar, RadialBarChart, ResponsiveContainer } from 'recharts'

type GaugeProps = {
  value: number
}

export const GaugeChart: React.FC<GaugeProps> = ({ value }) => {
  const data = [{ name: 'score', value, fill: '#7c3aed' }]
  return (
    <div className="w-full h-40">
      <ResponsiveContainer>
        <RadialBarChart
          cx="50%"
          cy="50%"
          innerRadius="70%"
          outerRadius="90%"
          barSize={18}
          data={data}
          startAngle={180}
          endAngle={-180}
        >
          <RadialBar minAngle={15} background clockWise dataKey="value" cornerRadius={8} />
          <text x="50%" y="50%" textAnchor="middle" dominantBaseline="middle" className="text-xl font-bold">
            {value}
          </text>
        </RadialBarChart>
      </ResponsiveContainer>
    </div>
  )
}

export const Gauge = GaugeChart
