FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy application code
COPY . .

# Build the static site for production
RUN npm run build

EXPOSE 4321

# Serve the production build
CMD ["npm", "run", "preview", "--", "--host", "0.0.0.0"]
