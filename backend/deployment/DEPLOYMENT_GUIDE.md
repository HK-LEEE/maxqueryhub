# MAX Query Hub - Deployment Guide

## Overview

This guide covers the deployment of MAX Query Hub with public API access. The system is designed to allow authenticated users to manage queries through the web interface, while providing public API endpoints for executing published queries.

## Architecture

- **Management Plane**: Web UI for query management (requires authentication)
- **Data Plane**: Public API for query execution (no authentication required)
- **UUID-based IDs**: All resources use UUIDs for better security and uniqueness

## Prerequisites

- Ubuntu 20.04 or later (or compatible Linux distribution)
- Python 3.11+
- PostgreSQL 12+
- Nginx
- SSL certificate (Let's Encrypt recommended)
- Domain name

## Deployment Steps

### 1. System Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3.11 python3.11-venv python3-pip postgresql nginx certbot python3-certbot-nginx git

# Create application user
sudo useradd -m -s /bin/bash maxqueryhub
sudo usermod -aG www-data maxqueryhub
```

### 2. Database Setup

```bash
# Connect to PostgreSQL
sudo -u postgres psql

# Create database and user
CREATE DATABASE max_queryhub;
CREATE USER queryhub_user WITH ENCRYPTED PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE max_queryhub TO queryhub_user;

# Enable UUID extension
\c max_queryhub
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
\q
```

### 3. Application Setup

```bash
# Create application directory
sudo mkdir -p /opt/max-queryhub
sudo chown maxqueryhub:www-data /opt/max-queryhub
cd /opt/max-queryhub

# Clone repository (as maxqueryhub user)
sudo -u maxqueryhub git clone https://github.com/yourusername/max-queryhub.git .

# Setup Python environment
cd backend
sudo -u maxqueryhub python3.11 -m venv venv
sudo -u maxqueryhub ./venv/bin/pip install --upgrade pip
sudo -u maxqueryhub ./venv/bin/pip install -r requirements.txt

# Create .env file
sudo -u maxqueryhub nano .env
```

### 4. Environment Configuration

Create `.env` file with:

```env
# Database
DATABASE_URL=postgresql+asyncpg://queryhub_user:your_secure_password@localhost:5432/max_queryhub

# Security
SECRET_KEY=your-secret-key-generate-with-openssl-rand-hex-32
JWT_SECRET_KEY=your-jwt-secret-same-as-maxplatform

# Server
HOST=0.0.0.0
PORT=8006
ENVIRONMENT=production

# CORS
BACKEND_CORS_ORIGINS=["https://queryhub.yourdomain.com"]

# External API
MAXPLATFORM_API_URL=http://localhost:8000
```

### 5. Database Migration

```bash
# Run Alembic migrations
cd /opt/max-queryhub/backend
sudo -u maxqueryhub ./venv/bin/alembic upgrade head

# If you have existing data, run UUID migration
sudo -u maxqueryhub ./venv/bin/python app/scripts/migrate_to_uuid.py
```

### 6. Frontend Build

```bash
cd /opt/max-queryhub/frontend

# Install dependencies
sudo npm install

# Update API URL in environment
echo "VITE_API_URL=https://queryhub.yourdomain.com" > .env.production

# Build frontend
sudo npm run build

# Copy to web directory
sudo mkdir -p /var/www/queryhub
sudo cp -r dist/* /var/www/queryhub/
sudo chown -R www-data:www-data /var/www/queryhub
```

### 7. Gunicorn Setup

```bash
# Copy Gunicorn config
sudo cp /opt/max-queryhub/backend/deployment/gunicorn_config.py /opt/max-queryhub/backend/

# Test Gunicorn
cd /opt/max-queryhub/backend
sudo -u maxqueryhub ./venv/bin/gunicorn --config gunicorn_config.py app.main:app
```

### 8. Systemd Service

```bash
# Copy systemd service file
sudo cp /opt/max-queryhub/backend/deployment/systemd/max-queryhub.service /etc/systemd/system/

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable max-queryhub
sudo systemctl start max-queryhub
sudo systemctl status max-queryhub
```

### 9. Nginx Configuration

```bash
# Copy Nginx config
sudo cp /opt/max-queryhub/backend/deployment/nginx.conf /etc/nginx/sites-available/queryhub
sudo ln -s /etc/nginx/sites-available/queryhub /etc/nginx/sites-enabled/

# Update domain name in config
sudo nano /etc/nginx/sites-available/queryhub
# Replace queryhub.yourdomain.com with your actual domain

# Test Nginx config
sudo nginx -t

# Get SSL certificate
sudo certbot --nginx -d queryhub.yourdomain.com

# Reload Nginx
sudo systemctl reload nginx
```

## Public API Usage

Once deployed, the public API endpoints are available at:

### Execute Query (No Authentication Required)
```bash
POST https://queryhub.yourdomain.com/execute/{query_uuid}

# Example with cURL
curl -X POST https://queryhub.yourdomain.com/execute/123e4567-e89b-12d3-a456-426614174000 \
  -H "Content-Type: application/json" \
  -d '{
    "params": {
      "start_date": "2024-01-01",
      "end_date": "2024-12-31"
    }
  }'
```

### Rate Limits
- Public Execute API: 100 requests/minute per IP
- Management API: 300 requests/minute per IP

## Security Considerations

1. **UUID Migration**: All IDs are UUIDs to prevent enumeration attacks
2. **Rate Limiting**: Built-in rate limiting for all endpoints
3. **HTTPS Only**: All traffic is encrypted with SSL
4. **CORS**: Configured for specific origins only
5. **SQL Injection**: Parameterized queries prevent SQL injection

## Monitoring

### Check service status
```bash
sudo systemctl status max-queryhub
```

### View logs
```bash
# Application logs
sudo journalctl -u max-queryhub -f

# Nginx access logs
sudo tail -f /var/log/nginx/queryhub_access.log

# Nginx error logs
sudo tail -f /var/log/nginx/queryhub_error.log
```

### Health check
```bash
curl https://queryhub.yourdomain.com/health
```

## Backup

Regular backups should include:
1. PostgreSQL database
2. Application `.env` file
3. Nginx configuration

```bash
# Database backup
pg_dump -U queryhub_user max_queryhub > backup_$(date +%Y%m%d).sql
```

## Troubleshooting

### Service won't start
- Check logs: `sudo journalctl -u max-queryhub -n 100`
- Verify database connection
- Check file permissions

### 502 Bad Gateway
- Ensure Gunicorn is running
- Check if port 8006 is listening: `sudo netstat -tlnp | grep 8006`

### Rate limit issues
- Adjust limits in `app/core/rate_limit.py`
- Update Nginx rate limit zones if needed

## Updates

To update the application:

```bash
cd /opt/max-queryhub
sudo -u maxqueryhub git pull
cd backend
sudo -u maxqueryhub ./venv/bin/pip install -r requirements.txt
sudo -u maxqueryhub ./venv/bin/alembic upgrade head
cd ../frontend
sudo npm install
sudo npm run build
sudo cp -r dist/* /var/www/queryhub/
sudo systemctl restart max-queryhub
sudo systemctl reload nginx
```