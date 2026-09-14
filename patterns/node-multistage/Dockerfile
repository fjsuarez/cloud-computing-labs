# syntax=docker/dockerfile:1

# Multi-stage build for a Node service.
# The pattern to learn: the toolchain that builds your app never ships with it.

# ---------- build stage ----------
FROM node:22-bookworm AS build

WORKDIR /src

# Dependency manifests first, so `npm ci` is cached until they actually change.
COPY package.json package-lock.json ./
RUN npm ci

# Source last, because it changes on every commit.
COPY . .
RUN npm run build


# ---------- runtime stage ----------
FROM node:22-bookworm-slim AS runtime

ENV NODE_ENV=production

# A dedicated unprivileged user. Numeric UID so it still works if /etc/passwd is absent.
RUN useradd --create-home --uid 10001 appuser

WORKDIR /app

# Production dependencies only — dev dependencies stayed in the build stage.
COPY package.json package-lock.json ./
RUN npm ci --omit=dev && npm cache clean --force

# Only the compiled output crosses the stage boundary.
COPY --from=build /src/dist ./dist

USER appuser

EXPOSE 3000
CMD ["node", "dist/server.js"]
