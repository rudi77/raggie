/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Dark theme colors (navy blue theme)
        dark: {
          primary: '#3B82F6', // Bright blue for primary elements
          accent: '#3B82F6',
          background: '#0F172A', // Deep navy blue
          'background-light': '#1E293B', // Lighter navy blue
          'background-lighter': '#334155', // Even lighter navy blue for hover states
          text: '#F8FAFC', // Almost white text
          'text-secondary': '#94A3B8', // Muted text
          border: '#1E293B', // Same as background-light for subtle borders
          chart: {
            background: '#1E293B',
            grid: '#334155',
            text: '#94A3B8'
          }
        },
        // Light theme colors
        light: {
          primary: '#3B82F6',
          accent: '#3B82F6',
          background: '#F1F5F9',
          'background-light': '#FFFFFF',
          'background-lighter': '#F8FAFC',
          text: '#0F172A',
          'text-secondary': '#64748B',
          border: '#E2E8F0',
          chart: {
            background: '#FFFFFF',
            grid: '#E2E8F0',
            text: '#64748B'
          }
        }
      },
      height: {
        header: '4rem',
      },
    },
  },
  plugins: [],
} 