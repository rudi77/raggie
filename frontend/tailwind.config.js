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
        // Dark theme colors (default)
        dark: {
          primary: '#4285f4',
          accent: '#4285f4',
          background: '#1a1f2e',
          'background-light': '#1e2538',
          'background-lighter': '#2a2f3e',
          text: '#ffffff',
          'text-secondary': '#808080',
          border: '#2a2f3e',
        },
        // Light Grey theme colors
        light: {
          primary: '#4285f4',
          accent: '#4285f4',
          background: '#e0e0e0',
          'background-light': '#ffffff',
          'background-lighter': '#e8e8e8',
          text: '#2c3e50',
          'text-secondary': '#718096',
          border: '#e2e8f0',
        }
      },
      height: {
        header: '4rem',
      },
    },
  },
  plugins: [],
} 