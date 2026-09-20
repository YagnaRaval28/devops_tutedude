# ---- Express frontend ----
FROM node:20-alpine

WORKDIR /app

# Copy the manifests first so this layer is cached: npm ci only re-runs
# when the dependencies actually change, not on every source edit.
COPY package*.json ./

# npm ci installs exactly what package-lock.json specifies, which makes
# the build reproducible. --omit=dev keeps devDependencies out of the image.
RUN npm ci --omit=dev

COPY . .

# node:alpine ships a 'node' user; run as it rather than root.
USER node

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:3000/health || exit 1

CMD ["node", "server.js"]
