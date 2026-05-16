FROM node:18-alpine

WORKDIR /app

# Copy package.json and install dependencies
COPY package*.json ./
RUN npm install

# Copy the rest of the source code
COPY . .

# Expose the frontend port
EXPOSE 3300

# Run Vite with host flag to allow external access
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
