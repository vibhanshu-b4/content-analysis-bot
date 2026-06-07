import type { Config } from "tailwindcss";

export default {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        base: "#050816",
        navy: "#0A0F2D",
        cyan: "#00D4FF",
        purple: "#7C3AED",
        indigo: "#6366F1",
        pink: "#EC4899",
      },
      fontFamily: {
        sans: ["Inter", "sans-serif"],
        display: ["Poppins", "sans-serif"],
      },
      borderRadius: {
        "2xl": "20px",
        "3xl": "24px",
      },
    },
  },
  plugins: [],
} satisfies Config;