/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/**/*.{js,jsx,ts,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          500: '#7928CA',
          600: '#FF0080',
          700: '#00DDEB',
        },
      },
      backgroundImage: {
        'gradient-to-br': 'linear-gradient(to bottom right, var(--tw-gradient-stops))',
      },
      gradientColorStops: (theme) => ({
        ...theme('colors'),
      }),
    },
  },
  plugins: [],
};