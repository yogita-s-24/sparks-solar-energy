/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./templates/**/*.html", "./static/js/**/*.js"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        forest: {
          950: "#0A2A1D",
          900: "#103D2B",
          800: "#15503A",
          700: "#1C6447",
          600: "#257A55",
        },
        solar: {
          200: "#C9EEBF",
          300: "#A1DE90",
          400: "#7FD26B",
          500: "#63C74D",
          600: "#4EA83A",
        },
        sun: {
          100: "#FFF4D6",
          200: "#FFE7A8",
          300: "#FFDC85",
          400: "#FFD166",
          500: "#F5BC3A",
        },
        cream: "#F7F8F2",
        charcoal: "#17211C",
      },
      fontFamily: {
        display: ["Manrope", "Mukta", "ui-sans-serif", "system-ui", "sans-serif"],
        sans: ["Inter", "Mukta", "ui-sans-serif", "system-ui", "sans-serif"],
      },
      maxWidth: {
        site: "80rem",
      },
      boxShadow: {
        soft: "0 20px 60px -24px rgba(16, 61, 43, 0.28)",
        glow: "0 0 0 1px rgba(255, 209, 102, 0.35), 0 18px 50px -12px rgba(255, 209, 102, 0.45)",
      },
      keyframes: {
        float: {
          "0%, 100%": { transform: "translate3d(0, 0, 0)" },
          "50%": { transform: "translate3d(0, -12px, 0)" },
        },
        "scroll-dot": {
          "0%": { opacity: "0", transform: "translateY(0)" },
          "30%": { opacity: "1" },
          "100%": { opacity: "0", transform: "translateY(14px)" },
        },
      },
      animation: {
        float: "float 7s ease-in-out infinite",
        "float-slow": "float 9s ease-in-out infinite",
        "scroll-dot": "scroll-dot 1.8s ease-in-out infinite",
      },
    },
  },
  plugins: [],
};
