import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
      },
      colors: {
        surface: {
          DEFAULT: "#0a0a0f",
          raised: "#111118",
          overlay: "#16161f",
        },
        accent: {
          blue: "#6366f1",
          purple: "#a855f7",
          teal: "#2dd4bf",
        },
      },
      backgroundImage: {
        "gradient-accent":
          "linear-gradient(135deg, #6366f1 0%, #a855f7 50%, #2dd4bf 100%)",
        "gradient-accent-hover":
          "linear-gradient(135deg, #818cf8 0%, #c084fc 50%, #5eead4 100%)",
        "gradient-subtle":
          "linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(168, 85, 247, 0.15) 50%, rgba(45, 212, 191, 0.05) 100%)",
        "gradient-card":
          "linear-gradient(145deg, rgba(255, 255, 255, 0.03) 0%, rgba(255, 255, 255, 0.01) 100%)",
      },
      boxShadow: {
        glow: "0 0 20px rgba(99, 102, 241, 0.15), 0 0 40px rgba(168, 85, 247, 0.05)",
        "glow-lg":
          "0 0 30px rgba(99, 102, 241, 0.2), 0 0 60px rgba(168, 85, 247, 0.1)",
      },
      animation: {
        "pulse-slow": "pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite",
      },
    },
  },
  plugins: [],
};

export default config;
