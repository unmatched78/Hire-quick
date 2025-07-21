# Hire Quick - FastAPI Recruitment Platform

A modern, high-performance recruitment platform built with FastAPI, featuring async operations, comprehensive API documentation, and AI-powered features.

## 🚀 Features

### Core Features
- **User Management**: Registration, authentication, profile management
- **Job Management**: Job posting, searching, filtering, and application tracking
- **Company Profiles**: Company information and job listings
- **Application System**: Job applications with status tracking
- **Background Verification**: Automated verification processes
- **Talent Pool**: AI-powered candidate matching and recommendations

### Technical Features
- **Async/Await**: Full async support for high performance
- **JWT Authentication**: Secure token-based authentication
- **SQLite Database**: Fast, embedded database (easily replaceable)
- **Pydantic Models**: Type-safe request/response validation
- **OpenAPI/Swagger**: Comprehensive API documentation
- **CORS Support**: Cross-origin resource sharing
- **File Upload**: Resume and document handling
- **Background Tasks**: Async task processing
- **Error Handling**: Comprehensive exception handling
- **Logging**: Structured logging with configurable levels

## 🏗️ Architecture

```
fastapi_app/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/          # API endpoints
│   │       │   ├── auth.py         # Authentication
│   │       │   ├── users.py        # User management
│   │       │   ├── jobs.py         # Job management
│   │       │   ├── applications.py # Application handling
│   │       │   └── companies.py    # Company management
│   │       └── api.py              # API router
│   ├── core/
│   │   ├── config.py               # Configuration settings
│   │   ├── database.py             # Database setup
│   │   ├── security.py             # Authentication & security
│   │   └── exceptions.py           # Custom exceptions
│   ├── models/                     # SQLAlchemy models
│   │   ├── user.py
│   │   ├── job.py
│   │   ├── application.py
│   │   ├── company.py
│   │   ├── talent_pool.py
│   │   └── background_verification.py
│   └── schemas/                    # Pydantic schemas
│       └── user.py
├── main.py                         # FastAPI application
├── requirements.txt                # Dependencies
├── .env                           # Environment variables
└── README.md                      # This file
```

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- pip or poetry

### Quick Start

1. **Clone and navigate to the FastAPI app**:
   ```bash
   cd fastapi_app
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Run the application**:
   ```bash
   python main.py
   ```

5. **Access the API**:
   - API: http://localhost:12000
   - Documentation: http://localhost:12000/docs
   - Alternative docs: http://localhost:12000/redoc
   - Health check: http://localhost:12000/health

## 📖 API Documentation

### Authentication Endpoints

#### Register User
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "username",
  "password": "securepassword",
  "user_type": "candidate",
  "phone": "+1234567890"
}
```

#### Login
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword"
}
```

#### Refresh Token
```http
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "your_refresh_token"
}
```

### User Management Endpoints

#### Get Current User Profile
```http
GET /api/v1/users/me
Authorization: Bearer <access_token>
```

#### Update Candidate Profile
```http
PUT /api/v1/users/candidate-profile
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "first_name": "John",
  "last_name": "Doe",
  "location": "New York, NY",
  "current_title": "Software Engineer",
  "summary": "Experienced developer...",
  "skills": ["Python", "FastAPI", "React"],
  "experience_years": 5
}
```

### Job Management Endpoints

#### List Jobs
```http
GET /api/v1/jobs?search=python&location=remote&job_type=full_time&skip=0&limit=20
```

#### Get Job Details
```http
GET /api/v1/jobs/{job_id}
```

#### Create Job (Recruiter only)
```http
POST /api/v1/jobs
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "title": "Senior Python Developer",
  "description": "We are looking for...",
  "location": "Remote",
  "job_type": "full_time",
  "salary_min": 80000,
  "salary_max": 120000,
  "requirements": ["Python", "FastAPI", "PostgreSQL"]
}
```

### Application Endpoints

#### Apply for Job
```http
POST /api/v1/applications
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "job_id": 1,
  "cover_letter": "I am interested in this position...",
  "form_responses": {}
}
```

#### List Applications
```http
GET /api/v1/applications?status=submitted&skip=0&limit=20
Authorization: Bearer <access_token>
```

## 🔧 Configuration

### Environment Variables

```bash
# Application
DEBUG=true
APP_NAME="Hire Quick - Recruitment Platform"
HOST=0.0.0.0
PORT=12000

# Database
DATABASE_URL=sqlite:///./hire_quick.db
DATABASE_ECHO=false

# Security
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
ALLOWED_HOSTS=*

# File Upload
MAX_FILE_SIZE=10485760
UPLOAD_DIR=media/uploads

# AI Features (optional)
OPENAI_API_KEY=your-openai-api-key
AI_ENABLED=false

# Email (optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@hirequick.com

# Logging
LOG_LEVEL=INFO
```

## 🗄️ Database

### SQLite (Default)
The application uses SQLite by default for easy setup and development. The database file is created automatically at `hire_quick.db`.

### Database Models

#### User Model
- Basic user information (email, username, password)
- User types: candidate, recruiter, admin
- Profile relationships

#### Job Model
- Job postings with full details
- Status tracking (draft, active, closed)
- Application counting and view tracking

#### Application Model
- Job applications with status tracking
- Cover letters and form responses
- Recruiter notes and feedback

#### Company Model
- Company profiles and information
- Industry and size categorization
- Verification status

### Switching to PostgreSQL (Production)

1. Install PostgreSQL driver:
   ```bash
   pip install asyncpg
   ```

2. Update DATABASE_URL:
   ```bash
   DATABASE_URL=postgresql+asyncpg://user:password@localhost/hirequick
   ```

## 🚀 Deployment

### Using Uvicorn (Development)
```bash
uvicorn main:app --host 0.0.0.0 --port 12000 --reload
```

### Using Gunicorn (Production)
```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:12000
```

### Docker Deployment
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 12000

CMD ["gunicorn", "main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:12000"]
```

## 🧪 Testing

### Run Tests
```bash
pytest
```

### Test Coverage
```bash
pytest --cov=app
```

### API Testing
Use the interactive documentation at `/docs` or tools like:
- Postman
- Insomnia
- curl
- httpx (Python)

## 🔒 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: bcrypt for secure password storage
- **Input Validation**: Pydantic models for request validation
- **CORS Protection**: Configurable cross-origin policies
- **Rate Limiting**: (Can be added with slowapi)
- **SQL Injection Protection**: SQLAlchemy ORM prevents SQL injection

## 🎯 Performance Features

- **Async/Await**: Non-blocking I/O operations
- **Connection Pooling**: Efficient database connections
- **Response Caching**: (Can be added with Redis)
- **Background Tasks**: Async task processing
- **Pagination**: Efficient data loading
- **Database Indexing**: Optimized queries

## 🔮 Future Enhancements

### AI Features
- Resume parsing and analysis
- Job matching algorithms
- Candidate scoring and ranking
- Automated screening questions

### Advanced Features
- Real-time notifications (WebSocket)
- Video interview scheduling
- Advanced analytics and reporting
- Multi-tenant support
- API rate limiting
- Caching layer (Redis)
- Message queues (Celery/RQ)

### Integrations
- Email service providers
- Calendar integrations
- Social media login
- Payment processing
- Third-party job boards

## 📝 API Response Format

### Success Response
```json
{
  "data": {...},
  "message": "Success",
  "status_code": 200
}
```

### Error Response
```json
{
  "detail": "Error message",
  "error_code": "VALIDATION_ERROR",
  "status_code": 422
}
```

### Pagination Response
```json
{
  "items": [...],
  "total": 100,
  "skip": 0,
  "limit": 20,
  "has_more": true
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
- Check the API documentation at `/docs`
- Review the code examples in this README
- Open an issue on GitHub

---

**Built with ❤️ using FastAPI, SQLAlchemy, and modern Python async features.**