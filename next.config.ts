import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  webpack: (config, { dev }) => {
    // Windows + Webpack filesystem cache can occasionally corrupt pack files,
    // producing missing chunk modules like `./611.js` at runtime.
    // Disabling persistent webpack caching in dev avoids that class of failures.
    if (dev) {
      config.cache = false;
    }
    return config;
  },
};

export default nextConfig;
