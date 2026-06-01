FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy application code
COPY . .

EXPOSE 4321

# Development server with host binding for Docker
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
