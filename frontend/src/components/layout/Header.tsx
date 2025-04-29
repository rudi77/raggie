'use client'

import { Sun, Moon } from 'lucide-react'
import { useTheme } from '../../context/ThemeContext'

export function Header() {
  const { theme, toggleTheme } = useTheme()
  
  const currentTime = new Date().toLocaleTimeString('de-DE', {
    hour: '2-digit',
    minute: '2-digit'
  })

  return (
    <header className="fixed top-0 left-0 right-0 h-16 bg-light-background-light dark:bg-dark-background border-b border-light-border dark:border-dark-border z-50">
      <div className="max-w-7xl mx-auto px-6 h-full flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <h1 className="text-light-primary dark:text-dark-primary text-xl font-medium">iGecko</h1>
          <span className="text-light-text-secondary dark:text-dark-text-secondary font-bold font-large">| CXO-Dashboard</span>
        </div>
        
        <div className="flex items-center space-x-4">
          <span className="text-light-primary dark:text-dark-primary text-sm">{currentTime}</span>
          <button
            onClick={toggleTheme}
            className="w-8 h-8 flex items-center justify-center rounded-full hover:bg-light-background-lighter dark:hover:bg-dark-background-lighter transition-colors"
            aria-label="Toggle theme"
          >
            {theme === 'dark' ? (
              <Sun className="w-4 h-4 text-light-text-secondary dark:text-dark-text-secondary" />
            ) : (
              <Moon className="w-4 h-4 text-light-text-secondary dark:text-dark-text-secondary" />
            )}
          </button>
          <div className="px-3 py-1 bg-light-primary/20 dark:bg-dark-primary/20 text-light-primary dark:text-dark-primary text-sm rounded-md">
            Version 1.0
          </div>
        </div>
      </div>
    </header>
  )
} 