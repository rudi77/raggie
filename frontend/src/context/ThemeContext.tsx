'use client'

import { createContext, useContext, useEffect, useState } from 'react'
import { ThemeProvider as MUIThemeProvider, createTheme } from '@mui/material'

type Theme = 'dark' | 'light'

interface ThemeContextType {
  theme: Theme
  toggleTheme: () => void
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined)

// MUI theme configuration
const getTheme = (mode: Theme) => createTheme({
  palette: {
    mode,
    ...(mode === 'dark' ? {
      primary: {
        main: '#3B82F6',
      },
      background: {
        default: '#0F172A',
        paper: '#1E293B',
      },
      text: {
        primary: '#F8FAFC',
        secondary: '#94A3B8',
      },
      divider: '#1E293B',
      grey: {
        100: '#1E293B',
        200: '#334155',
        300: '#475569',
        400: '#64748B',
        500: '#94A3B8',
        600: '#CBD5E1',
        700: '#E2E8F0',
        800: '#F1F5F9',
        900: '#F8FAFC',
      },
    } : {
      primary: {
        main: '#3B82F6',
      },
      background: {
        default: '#F1F5F9',
        paper: '#FFFFFF',
      },
      text: {
        primary: '#0F172A',
        secondary: '#64748B',
      },
      divider: '#E2E8F0',
      grey: {
        100: '#F8FAFC',
        200: '#F1F5F9',
        300: '#E2E8F0',
        400: '#CBD5E1',
        500: '#94A3B8',
        600: '#64748B',
        700: '#475569',
        800: '#334155',
        900: '#1E293B',
      },
    }),
  },
  shape: {
    borderRadius: 8,
  },
  shadows: [
    'none',
    '0 1px 2px 0 rgb(0 0 0 / 0.05)',
    '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)',
    '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
    '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
    '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)',
    // ... rest of the default shadows
  ],
})

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setTheme] = useState<Theme>('dark')
  const muiTheme = getTheme(theme)

  useEffect(() => {
    // Check for saved theme preference or system preference
    const savedTheme = localStorage.getItem('theme') as Theme
    const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
    const initialTheme = savedTheme || systemTheme
    
    setTheme(initialTheme)
    document.documentElement.classList.toggle('dark', initialTheme === 'dark')
  }, [])

  const toggleTheme = () => {
    const newTheme = theme === 'dark' ? 'light' : 'dark'
    setTheme(newTheme)
    localStorage.setItem('theme', newTheme)
    document.documentElement.classList.toggle('dark', newTheme === 'dark')
  }

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      <MUIThemeProvider theme={muiTheme}>
        {children}
      </MUIThemeProvider>
    </ThemeContext.Provider>
  )
}

export function useTheme() {
  const context = useContext(ThemeContext)
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider')
  }
  return context
} 