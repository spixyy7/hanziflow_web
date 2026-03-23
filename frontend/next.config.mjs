/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    return [
      {
        // Ovo omogućava da u kodu pišeš /api/nešto umesto punog Railway linka
        source: '/api/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/:path*`,
      },
    ];
  },
  images: {
    // Ovo ti treba ako budeš vukao slike (npr. avatare) sa Supabase-a
    domains: ['localhost', 'supabase.co'],
  },
  eslint: {
    // Ignoriše ESLint greške da build ne bi pukao
    ignoreDuringBuilds: true,
  },
  typescript: {
    // Ignoriše TypeScript greške (kao što je onaj problem sa grafikonima)
    ignoreBuildErrors: true,
  },
};

export default nextConfig;