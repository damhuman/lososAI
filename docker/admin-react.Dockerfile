# Multi-stage build for React Admin Panel
FROM node:18-alpine as build

# Set working directory
WORKDIR /app

# Copy package files
COPY admin-panel/package*.json ./

# Install dependencies
RUN npm ci --legacy-peer-deps

# Copy source code
COPY admin-panel/ ./

# Build the app
RUN npm run build

# Production stage with nginx
FROM nginx:alpine

# Copy built app to nginx
COPY --from=build /app/build /usr/share/nginx/html

# Copy nginx configuration
COPY docker/nginx/admin.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]