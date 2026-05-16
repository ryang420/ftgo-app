/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#111111",
        ember: "#c2410c",
        sand: "#f6f0e8",
      },
      fontFamily: {
        display: ["Avenir Next", "ui-sans-serif", "system-ui", "sans-serif"],
        body: ["ui-sans-serif", "system-ui", "sans-serif"],
      },
      boxShadow: {
        card: "0 24px 80px rgba(15, 23, 42, 0.28)",
      },
    },
  },
  plugins: [],
};
