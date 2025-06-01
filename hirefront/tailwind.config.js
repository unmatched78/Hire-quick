/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/**/*.{js,jsx,ts,tsx}', // Include all source files
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
    },
  },
  plugins: [], // Remove flowbite/plugin
};