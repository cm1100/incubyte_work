import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // 'standalone' bundles a minimal Node server + only the deps it needs
  // into .next/standalone — turns the production image into a few hundred MB
  // instead of pulling in the full node_modules tree.
  output: "standalone",
};

export default nextConfig;
