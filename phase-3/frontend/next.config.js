/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // swcMinify is now default in Next.js 15 - removed deprecated option
  poweredByHeader: false,
  compress: true,
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
    NEXT_PUBLIC_PHASE_2_API_URL: process.env.NEXT_PUBLIC_PHASE_2_API_URL,
  },
}

module.exports = nextConfig
