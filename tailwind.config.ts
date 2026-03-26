import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        slate: {
          750: "#273044",
          850: "#172033",
          950: "#0a0e1a",
        },
      },
    },
  },
  plugins: [],
  darkMode: "class",
};

export default config;
