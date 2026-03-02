# Use Node.js 22 LTS
FROM node:22-slim

# Install procps, systemd, systemd-sysv, and curl for dependencies
RUN apt-get update && apt-get install -y procps systemd systemd-sysv curl git && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy the entire workspace to the container
COPY . .

# Set up openclaw globally
RUN npm install -g openclaw@latest

# Copy configuration to root level or correct expected place if needed
# In this case we provide openclaw.json via volume or root, but since we pushed everything:
RUN mkdir -p /root/.openclaw && cp openclaw.json /root/.openclaw/openclaw.json || true

# Set environment variables for Render (PORT 10000 is required by Render)
ENV PORT=10000
EXPOSE 10000

# Run openclaw gateway in foreground so the container stays alive without systemd
CMD ["openclaw", "gateway", "run"]