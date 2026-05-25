FROM node:22-alpine AS deps

WORKDIR /app

COPY package*.json ./
RUN npm ci --no-audit --no-fund

FROM node:22-alpine AS runner

WORKDIR /app

RUN apk add --no-cache bash

ENV NODE_ENV=development

COPY --from=deps /app/node_modules ./node_modules
COPY . .

RUN npx prisma generate

EXPOSE 8000

# Default command can be overridden by Render's Docker Command setting.
CMD ["npm", "run", "dev:all"]
