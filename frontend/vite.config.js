import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    host: "0.0.0.0",
    port: 5173,
    proxy: {
      "/restaurants": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
      "/orders": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
      "/consumers": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
      "/kitchen": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
      "/health": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
});
