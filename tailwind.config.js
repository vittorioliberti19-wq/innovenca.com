/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./index.html"],
  theme: {
    extend: {
      colors: {
        ink: {
          950: "#000000",
          900: "#070707",
          800: "#101010",
          700: "#161616",
          600: "#1c1c1c",
          500: "#27272a",
          400: "#3f3f46",
        },
        brand: { DEFAULT: "#D4202A", dark: "#A0151D", light: "#E63946" },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        display: ["Space Grotesk", "Inter", "sans-serif"],
      },
    },
  },
  plugins: [],
};
