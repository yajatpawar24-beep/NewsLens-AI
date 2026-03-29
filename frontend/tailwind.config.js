/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        'display': ['Fraunces', 'Georgia', 'serif'],
        'body': ['Instrument Sans', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
      },
      colors: {
        'ink': '#0a0a0a',
        'paper': '#fdfbf7',
        'cream': '#f5f1e8',
        'gold': {
          DEFAULT: '#d4af37',
          dark: '#b8941f',
          light: '#e8d898',
        },
        'red': {
          DEFAULT: '#dc2626',
          dark: '#991b1b',
          light: '#fca5a5',
        },
        'gray': {
          DEFAULT: '#525252',
          light: '#a3a3a3',
          dark: '#262626',
        },
      },
      animation: {
        'reveal-up': 'revealUp 0.8s cubic-bezier(0.4, 0, 0.2, 1) backwards',
        'reveal-left': 'revealLeft 0.8s cubic-bezier(0.4, 0, 0.2, 1) backwards',
        'reveal-scale': 'revealScale 0.8s cubic-bezier(0.4, 0, 0.2, 1) backwards',
        'shimmer': 'shimmer 3s ease-in-out infinite',
        'fade-in': 'fadeIn 0.6s ease-out',
        'pulse-soft': 'pulseSoft 2s ease-in-out infinite',
      },
      keyframes: {
        revealUp: {
          '0%': { opacity: '0', transform: 'translateY(32px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        revealLeft: {
          '0%': { opacity: '0', transform: 'translateX(-32px)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
        revealScale: {
          '0%': { opacity: '0', transform: 'scale(0.95)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-200% center' },
          '100%': { backgroundPosition: '200% center' },
        },
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        pulseSoft: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.7' },
        },
      },
      letterSpacing: {
        'editorial': '0.05em',
        'wide': '0.15em',
      },
      lineHeight: {
        'editorial': '1.4',
      },
    },
  },
  plugins: [],
}
