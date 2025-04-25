'use client'

import { RevenueChart } from './RevenueChart'

export function RevenueView() {
  return (
    <div className="w-full px-4 py-4">
      <h2 className="text-2xl font-bold mb-4">Umsatzentwicklung 2024</h2>
      
      <div className="bg-[#1a2634] rounded-lg p-4">
        <RevenueChart />
      </div>

      <div className="mt-2 text-right text-secondary text-sm">
        {new Date().toLocaleTimeString('de-DE', { 
          hour: '2-digit', 
          minute: '2-digit', 
          second: '2-digit' 
        })}
      </div>
    </div>
  )
} 