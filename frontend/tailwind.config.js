/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        cosmic: {
          900: '#0f0f23',
          800: '#1a0f3a',
          700: '#2d1b5f',
          600: '#4a2c85',
          500: '#8b5cf6',
          400: '#a78bfa',
          300: '#c4b5fd',
        }
      }
    },
  },
  plugins: [],
}