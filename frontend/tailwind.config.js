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
        // Light theme colors (based on screenshot)
        light: {
          primary: '#8BC34A',
          accent: '#8BC34A',
          background: '#f5f5f5',
          'background-light': '#ffffff',
          'background-lighter': '#e0e0e0',
          text: '#333333',
          'text-secondary': '#666666',
          border: '#e0e0e0',
        }
      },
      height: {
        header: '4rem',
      },
    },
  },
  plugins: [],
} 