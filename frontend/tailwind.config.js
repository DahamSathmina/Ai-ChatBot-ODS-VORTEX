
/** @type {import('tailwindcss').Config} */
export default {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        bg: "#0b0f14",
        card: "#0f1720",
        primary: "#4f9cff",
        accent: "#9b7bff",
      },
    },
  },
  plugins: [],
}
