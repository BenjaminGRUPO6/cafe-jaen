/// <reference types="vitest/config" />
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";
import { VitePWA } from "vite-plugin-pwa";

// PWA: la app se puede instalar y muestra el último precio sin conexión (HU09)
export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: "autoUpdate",
      manifest: {
        name: "Café Jaén — precio del café",
        short_name: "Café Jaén",
        lang: "es",
        start_url: "/",
        display: "standalone",
        background_color: "#f4f4ef",
        theme_color: "#f4f4ef",
        icons: [
          { src: "/icons/icon-192.png", sizes: "192x192", type: "image/png" },
          { src: "/icons/icon-512.png", sizes: "512x512", type: "image/png" },
        ],
      },
      workbox: {
        // La letra viaja dentro de la app: se ve igual aunque no haya señal
        globPatterns: ["**/*.{js,css,html,png,svg,webmanifest,woff2}"],
        runtimeCaching: [
          {
            // Primero la red; si no hay señal, la última respuesta guardada.
            // El flujo en vivo (/prices/stream) no se guarda: nunca termina.
            urlPattern: ({ url }) =>
              url.pathname.startsWith("/api/prices") && !url.pathname.endsWith("/stream"),
            handler: "NetworkFirst",
            options: { cacheName: "prices", networkTimeoutSeconds: 5 },
          },
        ],
      },
    }),
  ],
  server: {
    // En desarrollo, /api se redirige al backend
    proxy: { "/api": "http://localhost:8000" },
  },
  test: {
    environment: "jsdom",
    setupFiles: ["./src/test-setup.ts"],
  },
});
