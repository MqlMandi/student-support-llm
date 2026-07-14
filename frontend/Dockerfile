FROM node:20-alpine as build

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm install

# Copy source code
COPY . .

# Pass the API URL as a build argument
ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL

# Build the app
RUN npm run build

# Serve with Nginx
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html

# Expose port 80
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
