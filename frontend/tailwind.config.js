/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"],
      },
      colors: {
        brand: {
          50: "#eefbf9",
          100: "#d7f5ef",
          200: "#b4e8de",
          300: "#83d4c6",
          400: "#52bea9",
          500: "#2ca28e",
          600: "#208273",
          700: "#1b685d",
          800: "#16524a",
          900: "#103d38",
        },
        medical: {
          50: "#f2f9ff",
          100: "#dceefd",
          200: "#beddf8",
          300: "#8cc6f3",
          400: "#57acec",
          500: "#2e91df",
          600: "#2276bf",
          700: "#1f5f99",
          800: "#1e4f7d",
          900: "#1c4568",
        },
        emerald: {
          50: "#ecfdf5",
          100: "#d1fae5",
          200: "#a7f3d0",
          300: "#6ee7b7",
          400: "#34d399",
          500: "#10b981",
          600: "#059669",
          700: "#047857",
          800: "#065f46",
          900: "#064e3b",
        },
        ink: {
          50: "#f7faf9",
          100: "#edf4f2",
          200: "#d7e5e1",
          300: "#b7c9c3",
          400: "#889f99",
          500: "#647670",
          600: "#4a5b57",
          700: "#33423f",
          800: "#23312f",
          900: "#13201e",
        },
      },
      boxShadow: {
        soft: "0 24px 72px rgba(19, 32, 30, 0.08)",
        glow: "0 0 0 1px rgba(255,255,255,0.7), 0 18px 48px rgba(19, 32, 30, 0.10)",
      },
      backgroundImage: {
        "hero-radial":
          "radial-gradient(circle at top left, rgba(44, 162, 142, 0.16), transparent 26%), radial-gradient(circle at top right, rgba(46, 145, 223, 0.12), transparent 24%), radial-gradient(circle at bottom left, rgba(83, 190, 169, 0.12), transparent 28%)",
      },
      keyframes: {
        float: {
          "0%, 100%": { transform: "translateY(0px)" },
          "50%": { transform: "translateY(-10px)" },
        },
        fadeUp: {
          "0%": { opacity: "0", transform: "translateY(10px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
      },
      animation: {
        float: "float 8s ease-in-out infinite",
        fadeUp: "fadeUp 0.5s ease-out both",
      },
    },
  },
  plugins: [],
};
