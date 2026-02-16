# Use Node.js as the base image
FROM node:18-slim

# Install Python, FFmpeg, and build dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    ffmpeg \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy package files and install Node dependencies
COPY package.json pnpm-lock.yaml* ./
RUN npm install -g pnpm && pnpm install

# Install Python dependencies
RUN pip3 install ffsubsync --break-system-packages

# Copy the rest of the application code
COPY . .

# Expose the port
EXPOSE 10000

# Start the application
CMD ["node", "server.js"]
