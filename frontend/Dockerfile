# frontend/Dockerfile

FROM node:20-alpine AS build-vue

# Set the working directory inside the container
WORKDIR /app

# Copy the package.json file and install dependencies
COPY package.json ./
RUN npm install -g npm@latest
RUN npm install

# Copy the entire application code into the container
COPY . .

# Build the Vue.js application
RUN npm run build

# Install serve to serve the built application
RUN npm install -g serve

# Expose the port
EXPOSE 5000

# Command to serve the Vue.js application
CMD ["serve", "-s", "dist", "-l", "5000"]