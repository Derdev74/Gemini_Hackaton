/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      // Neo-brutalist color palette
      colors: {
        'brutal': {
          'black': '#000000',
          'white': '#FFFFFF',
          'yellow': '#FFE135',
          'pink': '#FF6B9D',
          'blue': '#00D4FF',
          'green': '#00FF85',
          'purple': '#B967FF',
          'orange': '#FF9F43',
          'red': '#FF4757',
        },
        'background': '#F5F5DC', // Beige background
      },
      // Neo-brutalist box shadows (hard shadows, no blur)
      boxShadow: {
        'brutal': '4px 4px 0px 0px #000000',
        'brutal-lg': '8px 8px 0px 0px #000000',
        'brutal-xl': '12px 12px 0px 0px #000000',
        'brutal-hover': '2px 2px 0px 0px #000000',
      },
      // Border widths for brutalist design
      borderWidth: {
        '3': '3px',
        '4': '4px',
      },
      // Custom fonts
      fontFamily: {
        'mono': ['Space Mono', 'Courier New', 'monospace'],
        'sans': ['Space Grotesk', 'Arial', 'sans-serif'],
      },
      // Animation for interactions
      animation: {
        'bounce-brutal': 'bounce-brutal 0.3s ease-in-out',
      },
      keyframes: {
        'bounce-brutal': {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-4px)' },
        },
      },
    },
  },
  plugins: [],
}
