# Multi-stage build: deps → builder → runtime.
# 'node:22-alpine' ships multi-arch (amd64 + arm64) so the same Dockerfile
# builds on a Mac and on the t4g.nano (Graviton ARM) on EC2.

# ----- deps -----------------------------------------------------------------
FROM node:22-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci --no-audit --no-fund

# ----- builder --------------------------------------------------------------
FROM node:22-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
# When the frontend and backend share an origin (via Caddy on the EC2),
# all API calls go to /api/* — no NEXT_PUBLIC_API_URL needed at build time.
ENV NEXT_PUBLIC_API_URL=
ENV NEXT_TELEMETRY_DISABLED=1
RUN npm run build

# ----- runtime --------------------------------------------------------------
FROM node:22-alpine AS runtime
WORKDIR /app
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
ENV PORT=3000
ENV HOSTNAME=0.0.0.0

# 'standalone' output ships its own minimal node_modules; copy that and
# the public + static assets next to it.
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public

EXPOSE 3000

CMD ["node", "server.js"]
