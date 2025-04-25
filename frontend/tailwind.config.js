/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#4285f4',
        secondary: '#808080',
        background: '#121212',
        text: '#ffffff',
      },
      height: {
        header: '4rem',
      },
    },
  },
  plugins: [],
} 