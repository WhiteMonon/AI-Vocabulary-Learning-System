# AI Vocabulary Learning System - Backend

Backend API cho AI Vocabulary Learning System, xây dựng với FastAPI, PostgreSQL, SQLModel, và Alembic.

## 🚀 Features

- ✅ **FastAPI Framework** - Modern, fast web framework
- ✅ **PostgreSQL Database** - Production-ready relational database
- ✅ **SQLModel ORM** - Type-safe database models
- ✅ **Alembic Migrations** - Database schema versioning
- ✅ **Docker Ready** - Containerized deployment
- ✅ **JWT Authentication** - Secure authentication system
- ✅ **Structured Logging** - Comprehensive logging với rotation
- ✅ **Health Check Endpoint** - Monitoring và diagnostics
- ✅ **CORS Support** - Frontend integration ready
- ✅ **Clean Architecture** - Separation of concerns

## 📋 Prerequisites

- Docker & Docker Compose
- Python 3.11+ (cho local development)
- PostgreSQL 15+ (nếu không dùng Docker)

## 🛠️ Setup Instructions

### Option 1: Docker (Recommended)

1. **Clone repository và navigate to backend directory**
```bash
cd backend
```

2. **Tạo .env file từ template**
```bash
cp .env.example .env
```

3. **Chỉnh sửa .env file** với các giá trị phù hợp:
```env
# QUAN TRỌNG: Thay đổi SECRET_KEY trong production!
SECRET_KEY=your-super-secret-key-here

# Database credentials
POSTGRES_USER=vocab_user
POSTGRES_PASSWORD=your-secure-password
POSTGRES_DB=vocab_learning_db
```

4. **Build và start services**
```bash
docker-compose up -d
```

5. **Kiểm tra logs**
```bash
docker-compose logs -f backend
```

6. **Access API documentation**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health Check: http://localhost:8000/api/v1/health

### Option 2: Local Development

1. **Tạo virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# hoặc
venv\Scripts\activate  # Windows
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Setup PostgreSQL database** (nếu chưa có)

4. **Tạo .env file** và configure database connection

5. **Run migrations**
```bash
alembic upgrade head
```

6. **Start development server**
```bash
uvicorn app.main:app --reload
```

## 🗄️ Database Migrations

### Tạo migration mới
```bash
# Auto-generate migration từ model changes
alembic revision --autogenerate -m "Description of changes"

# Tạo empty migration
alembic revision -m "Description of changes"
```

### Apply migrations
```bash
# Upgrade to latest
alembic upgrade head

# Upgrade to specific revision
alembic upgrade <revision_id>

# Downgrade one revision
alembic downgrade -1

# Downgrade to specific revision
alembic downgrade <revision_id>
```

### Xem migration history
```bash
alembic history
alembic current
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run với coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/api/test_health.py

# Run với verbose output
pytest -v
```

## 📁 Project Structure

```
backend/
├── app/
│   ├── api/              # API routes
│   │   ├── deps.py       # Dependencies
│   │   └── v1/           # API version 1
│   │       ├── endpoints/
│   │       └── router.py
│   ├── core/             # Core configuration
│   │   ├── config.py     # Settings
│   │   ├── logging.py    # Logging config
│   │   └── security.py   # Security utils
│   ├── db/               # Database layer
│   │   ├── base.py       # Base models
│   │   ├── session.py    # Session management
│   │   └── init_db.py    # DB initialization
│   ├── models/           # SQLModel models
│   ├── schemas/          # Pydantic schemas
│   ├── services/         # Business logic
│   └── main.py           # FastAPI app
├── alembic/              # Database migrations
├── tests/                # Test suite
├── .env.example          # Environment template
├── docker-compose.yml    # Docker orchestration
├── Dockerfile            # Container definition
└── requirements.txt      # Python dependencies
```

## 🔐 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `POSTGRES_USER` | Database username | `vocab_user` |
| `POSTGRES_PASSWORD` | Database password | `vocab_password` |
| `POSTGRES_DB` | Database name | `vocab_learning_db` |
| `POSTGRES_HOST` | Database host | `postgres` |
| `POSTGRES_PORT` | Database port | `5432` |
| `SECRET_KEY` | JWT secret key | **REQUIRED** |
| `DEBUG` | Debug mode | `True` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `CORS_ORIGINS` | Allowed CORS origins | `http://localhost:3000` |

## 🔧 Development Workflow

1. **Tạo feature branch**
```bash
git checkout -b feature/your-feature-name
```

2. **Implement changes**
   - Tạo/modify models trong `app/models/`
   - Tạo schemas trong `app/schemas/`
   - Implement business logic trong `app/services/`
   - Tạo API endpoints trong `app/api/v1/endpoints/`

3. **Generate migration**
```bash
alembic revision --autogenerate -m "Add your feature"
```

4. **Test changes**
```bash
pytest
```

5. **Commit và push**
```bash
git add .
git commit -m "Add your feature"
git push origin feature/your-feature-name
```

## 📝 API Documentation

Sau khi start server, truy cập:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🐛 Troubleshooting

### Database connection failed
```bash
# Kiểm tra PostgreSQL đang chạy
docker-compose ps

# Restart database
docker-compose restart postgres

# Xem logs
docker-compose logs postgres
```

### Migration conflicts
```bash
# Reset database (CẢNH BÁO: Xóa tất cả data!)
docker-compose down -v
docker-compose up -d
```

### Port already in use
```bash
# Thay đổi port trong docker-compose.yml
ports:
  - "8001:8000"  # Thay vì 8000:8000
```

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

## 📄 License

This project is part of AI Vocabulary Learning System.
