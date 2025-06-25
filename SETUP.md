# Query Hub Setup Guide

## Prerequisites

1. **Python 3.11** or higher
2. **Node.js 22.x** or higher
3. **MySQL** or **PostgreSQL** database server
4. **maxplatform** authentication server running on port 8000

## Step 1: Database Setup

### Option A: MySQL
```sql
CREATE DATABASE max_queryhub CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### Option B: PostgreSQL
```sql
CREATE DATABASE max_queryhub;
```

## Step 2: Backend Configuration

1. Navigate to backend directory:
```bash
cd backend
```

2. Copy the example environment file:
```bash
cp .env.example .env
```

3. Edit `.env` file with your configuration:
```env
# For MySQL:
DATABASE_URL=mysql+aiomysql://root:YOUR_PASSWORD@localhost:3306/max_queryhub

# For PostgreSQL:
# DATABASE_URL=postgresql+asyncpg://postgres:YOUR_PASSWORD@localhost:5432/max_queryhub

# IMPORTANT: This must match your maxplatform JWT secret!
JWT_SECRET_KEY=your-maxplatform-jwt-secret-key

SECRET_KEY=generate-a-random-secret-key-here
```

4. Generate a secret key (optional):
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Step 3: Frontend Configuration

1. Navigate to frontend directory:
```bash
cd ../frontend
```

2. Copy the example environment file:
```bash
cp .env.example .env
```

3. Edit `.env` if your servers are on different hosts:
```env
VITE_API_BASE_URL=http://localhost:8006
VITE_AUTH_API_URL=http://localhost:8000
```

## Step 4: First-Time Setup

From the project root directory, run:

```bash
# Make scripts executable
chmod +x *.sh

# For first-time setup, run backend and frontend setup separately:

# Terminal 1 - Backend
./start_backend.sh
# This will:
# - Create virtual environment
# - Install Python dependencies
# - Prompt you to configure .env
# - Run database migrations
# - Start the backend server

# Terminal 2 - Frontend (after backend is configured)
./start_frontend.sh
# This will:
# - Install Node dependencies
# - Start the frontend development server
```

## Step 5: Verify Setup

1. **Backend Health Check**: http://localhost:8006/health
2. **API Documentation**: http://localhost:8006/docs
3. **Frontend**: http://localhost:3006

## Common Issues

### Issue: Database connection failed
- Ensure database server is running
- Verify database name and credentials in `.env`
- Check if database user has proper permissions

### Issue: JWT validation errors
- Ensure `JWT_SECRET_KEY` in backend `.env` matches maxplatform's key exactly
- Verify maxplatform is running on port 8000

### Issue: CORS errors
- Check that frontend URL is included in `BACKEND_CORS_ORIGINS` in backend config
- Ensure backend is running on port 8006

### Issue: Module import errors
- Make sure virtual environment is activated
- Re-run `pip install -r requirements.txt`
- For frontend, delete `node_modules` and run `npm install`

## Next Steps

1. **Create Admin User**: Use maxplatform to create an admin user
2. **Login**: Access http://localhost:3006 and login
3. **Create Workspace**: Admin users can create workspaces
4. **Add Queries**: Create SQL query templates
5. **Publish Queries**: Make queries publicly accessible via API

## Development Tips

- Backend logs are in the terminal running `./start_backend.sh`
- Frontend hot-reloads on code changes
- API documentation auto-updates at `/docs`
- Use `alembic` for database schema changes