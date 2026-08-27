/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#F0F4FA',
          100: '#D9E5F5',
          200: '#B8CEEB',
          300: '#8FB0DC',
          400: '#5F8FCC',
          500: '#2E5AA1',
          600: '#2447A8',
          700: '#1D3A8A',
          800: '#1E3A5F',
          900: '#162B47',
        },
        secondary: {
          500: '#F97316',
          600: '#EA580C',
        },
        success: {
          500: '#22C55E',
        },
        warning: {
          500: '#F59E0B',
        },
        danger: {
          500: '#EF4444',
        }
      }
    },
  },
  plugins: [],
}