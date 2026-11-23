/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        sans: ['"Plus Jakarta Sans"', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
      colors: {
        brand: {
          50: '#ecfeff',
          100: '#cffafe',
          400: '#22d3ee',
          500: '#06b6d4',
          600: '#0891b2',
        },
        crowd: {
          low: '#10B981',
          moderate: '#F59E0B',
          high: '#F97316',
          crush: '#EF4444',
        },
        navy: {
          800: '#1E293B',
          850: '#131D31',
          900: '#0F172A',
          950: '#090D16',
        }
      }
    },
  },
  plugins: [],
}
