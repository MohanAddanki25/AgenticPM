/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#eef4ff", 100: "#dbe6fe", 500: "#4f6df5", 600: "#3a52d6", 700: "#2d40ab",
        },
      },
    },
  },
  plugins: [],
}
