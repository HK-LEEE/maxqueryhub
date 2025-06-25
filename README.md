# Query Hub API Gateway

Query Hub is an enterprise-grade API gateway for managing and executing SQL queries with a two-plane architecture:
- **Management Plane**: Secure web UI for query registration and management (authentication required)
- **Data Plane**: Public API for query execution (no authentication required)

## Architecture

### System Components
1. **Authentication Server (maxplatform)**: `http://localhost:8000`
   - Handles user authentication and JWT token issuance
   
2. **Resource Server (max_queryhub)**: 
   - Backend: `http://localhost:8006`
   - Frontend: `http://localhost:3006`
   - Validates JWT tokens and handles core business logic

## Technology Stack

### Backend
- Python 3.11
- FastAPI (async)
- SQLAlchemy (async ORM)
- MySQL/PostgreSQL
- JWT Authentication
- APScheduler

### Frontend
- React 18 with TypeScript
- Vite (build tool)
- Tailwind CSS (monochrome theme)
- React Query (server state)
- Zustand (client state)

## Setup Instructions

### Prerequisites
- Python 3.11+
- Node.js 22.x+
- MySQL or PostgreSQL database
- Running maxplatform authentication server on port 8000

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment:
```bash
cp .env.example .env
# Edit .env file with your configuration
# IMPORTANT: JWT_SECRET_KEY must match maxplatform's key
```

5. Create database:
```sql
CREATE DATABASE max_queryhub;
```

6. Run migrations:
```bash
alembic upgrade head
```

7. Start server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8006
```

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Configure environment:
```bash
cp .env.example .env
# Edit .env file if needed
```

4. Start development server:
```bash
npm run dev
```

### Quick Start

Use the provided scripts for easy startup:

```bash
# Start all services
./start_all_services.sh

# Or start individually
./start_backend.sh
./start_frontend.sh
```

## API Documentation

### Management Plane APIs (Authentication Required)

All management APIs require a valid JWT token in the `Authorization: Bearer <token>` header.

#### Workspaces
- `GET /api/v1/workspaces` - List accessible workspaces
- `POST /api/v1/workspaces` - Create workspace (admin only)
- `GET /api/v1/workspaces/{id}` - Get workspace details

#### Queries
- `GET /api/v1/workspaces/{workspace_id}/queries` - List queries
- `POST /api/v1/workspaces/{workspace_id}/queries` - Create query
- `GET /api/v1/queries/{id}` - Get query details
- `PATCH /api/v1/queries/{id}/status` - Update query status

#### Permissions
- `GET /api/v1/workspaces/{workspace_id}/permissions` - List permissions
- `POST /api/v1/workspaces/{workspace_id}/permissions` - Set permissions

#### Testing
- `POST /api/v1/internal/execute/{query_id}` - Test query execution

### Data Plane API (Public)

No authentication required for published queries:

- `POST /api/v1/execute/{query_id}` - Execute published query

Example:
```bash
curl -X POST "http://localhost:8006/api/v1/execute/1" \
  -H "Content-Type: application/json" \
  -d '{"params": {"start_date": "2024-01-01", "end_date": "2024-12-31"}}'
```

## Features

### Query Management
- Create and manage SQL query templates with parameters
- Dynamic parameter validation based on type (string, integer, date, etc.)
- Query versioning and access control

### Security
- JWT-based authentication (integrated with maxplatform)
- Workspace-based access control
- User and group permissions
- SQL injection prevention through parameterized queries

### Publishing Workflow
1. Create query in UNAVAILABLE (private) state
2. Test query execution through UI
3. Publish query to make it publicly accessible
4. Monitor query usage and performance

### Automatic Maintenance
- Configurable auto-close for inactive queries
- Background scheduler runs daily cleanup tasks
- Query execution tracking and analytics

## Development

### Code Style
- Backend: PEP 8 (enforced with Black formatter)
- Frontend: ESLint + Prettier
- Type safety: Python type hints + TypeScript

### Testing
```bash
# Backend tests
cd backend
pytest

# Frontend tests (if configured)
cd frontend
npm test
```

### Database Migrations
```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Design Principles

### Monochrome UI Theme
- Pure black & white color scheme
- Typography-based hierarchy
- Clean, minimalist interface
- Consistent 4px spacing grid

### Architecture Patterns
- Separation of concerns (routers, services, CRUD, models)
- Async-first design
- Type-safe APIs
- Stateless authentication

## License

Proprietary - All rights reserved