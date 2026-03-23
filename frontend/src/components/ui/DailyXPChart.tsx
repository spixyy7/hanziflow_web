'use client'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts';

interface DailyXPChartProps {
  history: { date: string; xp: number }[];
  goal: number;
}

export function DailyXPChart({ history, goal }: DailyXPChartProps) {
  // Formatiramo podatke za grafikon
  const data = history?.map(d => ({
    ...d,
    name: new Date(d.date).toLocaleDateString('sr-RS', { day: 'numeric', month: 'short' })
  })) || [];

  return (
    <div className="card p-6 h-[300px] w-full" 
         style={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: '12px' }}>
      <h3 className="text-sm font-semibold mb-4 text-gray-400 uppercase tracking-wider">XP Aktivnost</h3>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
          <XAxis dataKey="name" stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} />
          <YAxis hide domain={[0, (dataMax: number) => Math.max(dataMax, goal + 10)]} />
          <Tooltip 
            contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #1e3a5f', borderRadius: '8px' }}
            itemStyle={{ color: '#3b82f6' }}
          />
          <ReferenceLine y={goal} stroke="#ef4444" strokeDasharray="3 3" />
          <Line 
            type="monotone" 
            dataKey="xp" 
            stroke="#3b82f6" 
            strokeWidth={3} 
            dot={{ fill: '#3b82f6', r: 4 }}
            activeDot={{ r: 6 }} 
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}