/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",  // ← Very important!
  ],
  theme: {
    extend: {
      // If you don’t actually need a custom animation-delay, you can remove this.
      keyframes: {
        // Example of a “slow pulse” just to illustrate custom keyframes
        "slow-pulse": {
          "0%, 100%": { opacity: 0.7 },
          "50%": { opacity: 1 },
        },
      },
      animation: {
        "slow-pulse": "slow-pulse 4s ease-in-out infinite",
      },
    },
  },
  plugins: [require("@tailwindcss/forms"), require("@tailwindcss/typography")],
};
