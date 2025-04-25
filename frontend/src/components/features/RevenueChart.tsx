'use client'

import { useState, useEffect } from 'react'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'

interface RevenueData {
  month: string
  revenue: number
}

const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-[#1a2634] p-3 rounded-lg border border-secondary/20">
        <p className="text-sm font-medium">{label}</p>
        <p className="text-primary text-lg font-bold">
          €{payload[0].value.toLocaleString('de-DE')}
        </p>
      </div>
    )
  }
  return null
}

export function RevenueChart() {
  const [data, setData] = useState<RevenueData[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/revenue')
        if (!response.ok) {
          throw new Error('Failed to fetch revenue data')
        }
        const revenueData = await response.json()
        setData(revenueData)
        setError(null)
      } catch (err) {
        setError('Error loading revenue data')
        console.error('Error fetching revenue data:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  if (loading) {
    return (
      <div className="w-full h-[300px] flex items-center justify-center">
        <div className="text-secondary">Loading revenue data...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="w-full h-[300px] flex items-center justify-center">
        <div className="text-red-500">{error}</div>
      </div>
    )
  }

  return (
    <div className="w-full h-[300px] relative">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart
          data={data}
          margin={{ top: 10, right: 20, left: 10, bottom: 10 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#808080" opacity={0.1} />
          <XAxis
            dataKey="month"
            stroke="#808080"
            tick={{ fill: '#808080' }}
            tickLine={{ stroke: '#808080' }}
          />
          <YAxis
            stroke="#808080"
            tick={{ fill: '#808080' }}
            tickLine={{ stroke: '#808080' }}
            tickFormatter={(value) => `€${value}`}
          />
          <Tooltip content={<CustomTooltip />} />
          <Line
            type="monotone"
            dataKey="revenue"
            stroke="#4285f4"
            strokeWidth={2}
            dot={{ fill: '#4285f4', r: 4 }}
            activeDot={{ r: 6, fill: '#4285f4' }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
} 