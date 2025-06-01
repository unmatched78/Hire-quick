/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/**/*.{js,jsx,ts,tsx}', // Scan all source files
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
        'gradient-to-br': 'linear-gradient(to bottom right, var(--tw-gradient-stops))', // Enable gradient direction
      },
      gradientColorStops: (theme) => ({
        ...theme('colors'), // Include all colors (e.g., gray-900, gray-800)
      }),
    },
  },
  plugins: [],
};