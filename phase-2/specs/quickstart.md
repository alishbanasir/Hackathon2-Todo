# Quickstart Guide: Todo Full-Stack Web Application

**Date**: 2026-01-07
**Feature**: 002-fullstack-web-app
**Target Audience**: Developers setting up local development environment

## Prerequisites

### Required Software
- **Python**: 3.11 or higher ([Download](https://www.python.org/downloads/))
- **Node.js**: 18.x or higher ([Download](https://nodejs.org/))
- **npm**: 9.x or higher (included with Node.js)
- **Git**: For version control
- **Code Editor**: VS Code recommended (with Python and TypeScript extensions)

### Required Accounts
- **Neon Database**: Free serverless PostgreSQL account ([Sign up](https://neon.tech/))

---

## Project Structure

```
phase-2/
├── backend/                    # FastAPI Python backend
│   ├── src/
│   │   ├── models/            # SQLModel entity definitions
│   │   ├── services/          # Business logic layer
│   │   ├── api/               # FastAPI route handlers
│   │   ├── middleware/        # JWT authentication middleware
│   │   └── main.py            # FastAPI application entry point
│   ├── tests/                 # Pytest test suite
│   ├── alembic/               # Database migration files
│   ├── requirements.txt       # Python dependencies
│   ├── .env.example           # Example environment variables
│   └── pyproject.toml         # Python project configuration
│
├── frontend/                  # Next.js TypeScript frontend
│   ├── app/                   # Next.js App Router pages
│   │   ├── (auth)/           # Auth-related pages (login, register)
│   │   ├── (dashboard)/      # Protected dashboard pages
│   │   └── layout.tsx        # Root layout with providers
│   ├── components/            # Reusable React components
│   ├── lib/                   # Utility functions and API client
│   ├── public/                # Static assets
│   ├── .env.local.example     # Example environment variables
│   ├── package.json           # Node dependencies
│   ├── tsconfig.json          # TypeScript configuration
│   └── tailwind.config.ts     # Tailwind CSS configuration
│
└── specs/                     # Feature specifications
    ├── spec.md                # Requirements specification
    ├── plan.md                # Implementation plan
    ├── data-model.md          # Database schema
    ├── quickstart.md          # This file
    └── contracts/             # API contracts
        └── openapi.yaml       # OpenAPI 3.1 spec
```

---

## Step 1: Clone Repository and Navigate to Phase 2

```bash
# Clone the repository (if not already done)
git clone <repository-url>
cd hackathon2-todo5phases

# Checkout Phase II branch
git checkout 002-fullstack-web-app

# Navigate to Phase 2 directory
cd phase-2
```

---

## Step 2: Backend Setup (FastAPI)

### 2.1 Create Virtual Environment

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 2.2 Install Dependencies

```bash
# Install Python packages
pip install -r requirements.txt

# Verify installation
python -c "import fastapi, sqlmodel, jose; print('Dependencies installed successfully')"
```

**Key Dependencies** (from `requirements.txt`):
```
fastapi==0.109.0
uvicorn[standard]==0.27.0
sqlmodel==0.0.14
psycopg2-binary==2.9.9          # PostgreSQL driver
python-jose[cryptography]==3.3.0  # JWT handling
argon2-cffi==23.1.0             # Password hashing
python-dotenv==1.0.0            # Environment variable loading
structlog==24.1.0               # Structured logging
alembic==1.13.0                 # Database migrations

# Development dependencies
pytest==7.4.4
pytest-asyncio==0.23.3
mypy==1.8.0
ruff==0.1.14
```

### 2.3 Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your values
# Windows:
notepad .env
# macOS/Linux:
nano .env
```

**Required Environment Variables** (`.env`):
```env
# Database
DATABASE_URL=postgresql://<user>:<password>@<neon-host>/<dbname>

# Authentication (generate 256-bit secret)
BETTER_AUTH_SECRET=<your-secret-key-here>

# CORS (allow frontend origin)
CORS_ORIGINS=http://localhost:3000

# Application
APP_ENV=development
LOG_LEVEL=INFO
```

**Generate BETTER_AUTH_SECRET**:
```bash
# Python method (recommended)
python -c "import secrets; print(secrets.token_urlsafe(32))"

# OpenSSL method
openssl rand -base64 32
```

### 2.4 Setup Neon PostgreSQL Database

1. **Create Neon Project**:
   - Go to [Neon Console](https://console.neon.tech/)
   - Click "Create Project"
   - Name: "todo-phase-2"
   - Region: Choose closest to you
   - Copy connection string

2. **Update DATABASE_URL**:
   - Format: `postgresql://[user]:[password]@[host]/[database]`
   - Example: `postgresql://user:pass@ep-cool-morning-123456.us-east-2.aws.neon.tech/todoapp`

3. **Test Connection**:
   ```bash
   python -c "from sqlmodel import create_engine; engine = create_engine('postgresql://...'); print('Connected!' if engine else 'Failed')"
   ```

### 2.5 Run Database Migrations

```bash
# Initialize Alembic (if not already initialized)
alembic init alembic

# Create initial migration
alembic revision --autogenerate -m "Create users and todos tables"

# Apply migrations
alembic upgrade head

# Verify tables created
python -c "from sqlmodel import create_engine, Session; engine = create_engine('postgresql://...'); print('Tables created successfully')"
```

### 2.6 Start Backend Server

```bash
# Development mode (with auto-reload)
uvicorn src.main:app --reload --port 8000

# Production mode
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

**Verify Backend Running**:
- Open browser: `http://localhost:8000/docs`
- You should see FastAPI's interactive API documentation (Swagger UI)

---

## Step 3: Frontend Setup (Next.js)

### 3.1 Navigate to Frontend Directory

```bash
# From repository root
cd phase-2/frontend
```

### 3.2 Install Dependencies

```bash
# Install Node packages
npm install

# Verify installation
npm list next react tailwindcss
```

**Key Dependencies** (from `package.json`):
```json
{
  "dependencies": {
    "next": "^16.0.0",
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "better-auth": "^1.0.0",
    "tailwindcss": "^3.4.0"
  },
  "devDependencies": {
    "typescript": "^5.3.0",
    "@types/node": "^20.10.0",
    "@types/react": "^19.0.0",
    "eslint": "^8.56.0",
    "eslint-config-next": "^16.0.0",
    "prettier": "^3.1.0",
    "vitest": "^1.1.0"
  }
}
```

### 3.3 Configure Environment Variables

```bash
# Copy example environment file
cp .env.local.example .env.local

# Edit .env.local with your values
# Windows:
notepad .env.local
# macOS/Linux:
nano .env.local
```

**Required Environment Variables** (`.env.local`):
```env
# Authentication (MUST match backend secret)
BETTER_AUTH_SECRET=<same-secret-as-backend>

# API URL
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

### 3.4 Start Frontend Development Server

```bash
# Development mode (with hot reload)
npm run dev

# Production build (for testing)
npm run build
npm run start
```

**Verify Frontend Running**:
- Open browser: `http://localhost:3000`
- You should see the todo application homepage

---

## Step 4: Verify Full Stack Integration

### 4.1 Test User Registration

1. Open browser: `http://localhost:3000/register`
2. Fill form:
   - Email: `test@example.com`
   - Password: `testpassword123`
3. Click "Register"
4. Should redirect to dashboard with empty todo list

### 4.2 Test Todo Creation

1. In dashboard, click "Create Todo"
2. Fill form:
   - Title: "My first todo"
   - Description: "Testing Phase II application"
3. Click "Save"
4. Todo should appear in list

### 4.3 Test Data Persistence

1. Logout from application
2. Login again with same credentials
3. Your todo should still be visible (database persistence verified)

### 4.4 Test User Isolation

1. Register second user: `test2@example.com`
2. Login as second user
3. Should see empty todo list (not `test@example.com`'s todos)

---

## Step 5: Run Tests

### Backend Tests

```bash
cd phase-2/backend

# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_auth.py

# Run type checking
mypy src --strict

# Run linting
ruff check src
```

### Frontend Tests

```bash
cd phase-2/frontend

# Run all tests
npm test

# Run with coverage
npm test -- --coverage

# Run type checking
npm run type-check

# Run linting
npm run lint
```

---

## Common Issues & Troubleshooting

### Issue: "ModuleNotFoundError" (Backend)

**Solution**: Ensure virtual environment is activated and dependencies installed
```bash
# Reactivate venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: "Database connection failed"

**Solution**: Verify Neon connection string
```bash
# Test connection
python -c "from sqlmodel import create_engine; engine = create_engine('YOUR_DATABASE_URL'); print('Success!')"

# Check .env file has correct DATABASE_URL
cat .env | grep DATABASE_URL
```

### Issue: "CORS error" when frontend calls backend

**Solution**: Ensure CORS_ORIGINS in backend .env matches frontend URL
```env
# Backend .env
CORS_ORIGINS=http://localhost:3000

# Restart backend server after changing .env
```

### Issue: "JWT verification failed"

**Solution**: Ensure BETTER_AUTH_SECRET is identical in frontend and backend
```bash
# Backend .env
BETTER_AUTH_SECRET=abc123...

# Frontend .env.local
BETTER_AUTH_SECRET=abc123...  # MUST be identical

# Restart both servers after changing
```

### Issue: "Port already in use"

**Solution**: Kill existing process or use different port
```bash
# Find process using port 8000 (backend)
# Windows:
netstat -ano | findstr :8000
# macOS/Linux:
lsof -i :8000

# Kill process (replace PID)
kill -9 <PID>

# Or use different port
uvicorn src.main:app --reload --port 8001
```

---

## Development Workflow

### Daily Development Flow

1. **Start both servers**:
   ```bash
   # Terminal 1 - Backend
   cd phase-2/backend
   source venv/bin/activate
   uvicorn src.main:app --reload

   # Terminal 2 - Frontend
   cd phase-2/frontend
   npm run dev
   ```

2. **Make code changes** in your editor

3. **Test changes** automatically reload in browser

4. **Run tests** before committing:
   ```bash
   # Backend tests
   cd backend && pytest

   # Frontend tests
   cd frontend && npm test
   ```

5. **Commit changes** following Conventional Commits:
   ```bash
   git add .
   git commit -m "feat: add todo deletion confirmation dialog"
   git push origin 002-fullstack-web-app
   ```

### Recommended VS Code Extensions

- **Python**: ms-python.python
- **Pylance**: ms-python.vscode-pylance
- **ESLint**: dbaeumer.vscode-eslint
- **Prettier**: esbenp.prettier-vscode
- **Tailwind CSS IntelliSense**: bradlc.vscode-tailwindcss
- **GitLens**: eamodio.gitlens

---

## Next Steps

After completing this quickstart:

1. **Read the Specification**: `specs/002-fullstack-web-app/spec.md`
2. **Review Implementation Plan**: `specs/002-fullstack-web-app/plan.md`
3. **Understand Data Model**: `specs/002-fullstack-web-app/data-model.md`
4. **Explore API Contracts**: `specs/002-fullstack-web-app/contracts/openapi.yaml`
5. **Review Tasks**: `specs/002-fullstack-web-app/tasks.md` (after running `/sp.tasks`)

---

## Additional Resources

- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **Next.js Documentation**: https://nextjs.org/docs
- **SQLModel Documentation**: https://sqlmodel.tiangolo.com/
- **Tailwind CSS Documentation**: https://tailwindcss.com/docs
- **Better Auth Documentation**: https://www.better-auth.com/
- **Neon PostgreSQL Guide**: https://neon.tech/docs/introduction

---

## Support

For issues or questions:
1. Check this quickstart guide and troubleshooting section
2. Review project documentation in `specs/` directory
3. Check project constitution: `.specify/memory/constitution.md`
4. Create issue in project repository with detailed error logs
