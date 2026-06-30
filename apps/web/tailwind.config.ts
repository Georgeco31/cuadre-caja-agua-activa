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
          500: "#1689c7",
          700: "#0f5f8c",
        },
      },
    },
  },
  plugins: [],
};

export default config;
