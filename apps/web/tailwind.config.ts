import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        water: {
          50: "#eef9ff",
          100: "#d9f0ff",
          200: "#bce5fb",
          500: "#1689c7",
          600: "#1175aa",
          700: "#0f5f8c",
          800: "#114f72",
          900: "#123f5a",
        },
      },
      boxShadow: {
        card: "0 1px 2px rgba(15, 23, 42, 0.04), 0 10px 30px rgba(15, 23, 42, 0.04)",
        water: "0 16px 34px rgba(15, 95, 140, 0.2)",
      },
    },
  },
  plugins: [],
};

export default config;
