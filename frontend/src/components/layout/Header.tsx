'use client'

import { Sun, Moon } from 'lucide-react'
import { useTheme } from '@/context/ThemeContext'

export function Header() {
  const { theme, toggleTheme } = useTheme()
  
  const currentTime = new Date().toLocaleTimeString('de-DE', {
    hour: '2-digit',
    minute: '2-digit'
  })

  return (
    <header className="fixed top-0 left-0 right-0 h-16 bg-black border-b border-[#1a1a1a] z-50">
      <div className="max-w-7xl mx-auto px-6 h-full flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <h1 className="text-[#4285f4] text-xl font-medium">iGecko</h1>
          <span className="text-sm text-gray-400">| CxO</span>
        </div>
        
        <div className="flex items-center space-x-4">
          <span className="text-[#4285f4] text-sm">{currentTime}</span>
          <button
            onClick={toggleTheme}
            className="w-8 h-8 flex items-center justify-center rounded-full hover:bg-[#1a1a1a] transition-colors"
            aria-label="Toggle theme"
          >
            {theme === 'dark' ? (
              <Sun className="w-4 h-4 text-gray-400" />
            ) : (
              <Moon className="w-4 h-4 text-gray-400" />
            )}
          </button>
          {/* <button className="px-3 py-1 bg-[#4285f4]/20 text-[#4285f4] text-sm rounded-md">
            22M2fu
          </button> */}
        </div>
      </div>
    </header>
  )
} 