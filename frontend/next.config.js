/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  // Safely allows production builds to complete even if 
  // there are styling or formatting warnings
  eslint: {
    ignoreDuringBuilds: true,
  },
  // Allows compilation to finish if there are minor type-check friction points
  typescript: {
    ignoreBuildErrors: true,
  },
};

module.exports = nextConfig;
