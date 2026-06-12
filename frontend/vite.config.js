import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  build: {
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes("node_modules")) {
            if (id.includes("react-chartjs-2") || id.includes("chart.js")) return "charts";
            if (id.includes("lucide-react")) return "icons";
            if (id.includes("react-router-dom")) return "router";
            if (id.includes("axios")) return "api";
            return "vendor";
          }
        },
      },
    },
  },
});
