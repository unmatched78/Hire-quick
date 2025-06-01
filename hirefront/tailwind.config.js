/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/**/*.{js,jsx,ts,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          500: '#7928CA', // Neon purple
          600: '#FF0080', // Neon pink
          700: '#00DDEB', // Neon cyan
        },
      },
      backgroundImage: {
        'gradient-to-br': 'linear-gradient(to bottom right, var(--tw-gradient-stops))',
      },
      gradientColorStops: (theme) => ({
        ...theme('colors'),
      }),
      fontFamily: {
        poppins: ['Poppins', 'sans-serif'], // Modern font for headings
        inter: ['Inter', 'sans-serif'], // Clean font for body
      },
      animation: {
        'pulse-glow': 'pulse-glow 3s ease-in-out infinite',
      },
      keyframes: {
        'pulse-glow': {
          '0%, 100%': { boxShadow: '0 0 15px rgba(121, 40, 202, 0.5)' },
          '50%': { boxShadow: '0 0 30px rgba(121, 40, 202, 0.8)' },
        },
      },
    },
  },
  plugins: [],
};