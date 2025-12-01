/** @type {import('next').NextConfig} */
const nextConfig = {
  turbopack: {
    root: __dirname, // Force correct workspace when multiple lockfiles exist
  },
  // Configuración de imágenes para RAWG API
  images: {
    // Dominios permitidos para <Image> de Next.js
    remotePatterns: [
      {
        protocol: "https",
        hostname: "media.rawg.io", // Imágenes de RAWG API
      },
      {
        protocol: "https",
        hostname: "images.unsplash.com", // Mock images used in tests
      },
    ],
  },

  // Variables de entorno públicas (accesibles desde browser)
  env: {
    NEXT_PUBLIC_API_URL:
      process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
  },
};

module.exports = nextConfig;
