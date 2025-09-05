/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}", // adjust to your project structure
  ],
  theme: {
    extend: {
      colors: {
        "primary-bg": "#0f172a", // Deep dark blue background
        "gradient-start": "#3b82f6", // Vibrant blue gradient start
        "gradient-end": "#9333ea", // Bold purple gradient end
        "card-bg": "#1e293b", // Dark card background
        "card-border": "#475569", // Light blueish border for cards
        "button-hover": "#2563eb", // Hover effect for buttons
        "text-light": "#f9fafb", // Light text color for contrast
        "text-muted": "#9ca3af", // Muted gray text
      },
      keyframes: {
        blob: {
          "0%, 100%": { transform: "translateY(0) scale(1)" },
          "33%": { transform: "translate(-40px, -20px) scale(1.1)" },
          "66%": { transform: "translate(25px, 15px) scale(0.9)" },
        },
      },
      animation: {
        blob: "blob 12s infinite",
      },
    },
  },
  plugins: [],
};
