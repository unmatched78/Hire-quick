# Hire Quick - Modern Recruitment Platform API

A comprehensive, high-performance recruitment platform built with **FastAPI** featuring async operations, AI-powered features, and modern API design.

## 🚀 Features

### 🔐 Authentication & Security
- **JWT-based authentication** with refresh tokens
- **Role-based access control** (Candidate, Recruiter, Admin)
- **Password security** with bcrypt hashing
- **Email verification** and password reset flows
- **Social authentication** support ready

### 👥 User Management
- **Dual user types**: Candidates and Recruiters
- **Profile management** with file upload support
- **Profile completion tracking**
- **Secure password management**

### 💼 Job Management
- **Job posting and management** for recruiters
- **Advanced search and filtering** capabilities
- **Job save/unsave** functionality for candidates
- **Custom application forms** per job
- **Job performance analytics**

### 📄 Application System
- **Dynamic application forms** with custom fields
- **File upload support** (resumes, portfolios, cover letters)
- **Application status tracking** with real-time updates
- **Interview scheduling** and management
- **Application analytics** and reporting

### 🤖 AI-Powered Features (Ready for Implementation)
- **Resume parsing and analysis**
- **Job-candidate matching algorithms**
- **Skill extraction and categorization**
- **AI interviewer** and mock interview sessions
- **Automated CV screening**
- **Background verification** automation

### 🏢 Company Management
- **Company profiles** and branding
- **Multi-company support** for enterprise
- **Company-specific job listings**
- **Team management** for recruiters

### 📊 Analytics & Reporting
- **Application analytics** and insights
- **Job performance metrics**
- **User engagement tracking**
- **Recruitment funnel analysis**

### 🔔 Real-time Features
- **WebSocket notifications** (ready for implementation)
- **Real-time application updates**
- **Chat functionality** between candidates and recruiters
- **Live interview scheduling**

## 🏗️ Technology Stack

- **Backend**: FastAPI (Python 3.8+)
- **Database**: SQLAlchemy with async support (SQLite for dev, PostgreSQL for production)
- **Authentication**: JWT with PyJWT
- **Validation**: Pydantic for request/response models
- **Documentation**: Automatic OpenAPI/Swagger generation
- **Testing**: Comprehensive API test suite
- **File Storage**: Local storage with cloud provider support ready

## 📁 Project Structure

```
Hire-quick/
├── fastapi_app/                 # Main FastAPI application
│   ├── app/
│   │   ├── api/v1/endpoints/   # API route handlers
│   │   ├── core/               # Core functionality (config, database, security)
│   │   ├── models/             # SQLAlchemy database models
│   │   └── schemas/            # Pydantic request/response schemas
│   ├── main.py                 # FastAPI application entry point
│   ├── requirements.txt        # Python dependencies
│   ├── migrate.py             # Database migration script
│   ├── test_api.py            # API testing suite
│   └── README.md              # Detailed setup instructions
├── CONVERSION_SUMMARY.md       # FastAPI features details
└── README.md                  # This file
```

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/unmatched78/Hire-quick.git
cd Hire-quick/fastapi_app
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Set Up Environment
```bash
cp .env.example .env
# Edit .env with your configuration
```

### 4. Initialize Database
```bash
python migrate.py
```

### 5. Run the Application
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 6. Access the API
- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 📚 API Documentation

The API provides comprehensive endpoints for:

### Authentication
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Refresh access token
- `POST /api/v1/auth/password-reset` - Request password reset
- `POST /api/v1/auth/verify-email` - Verify email address

### User Management
- `GET /api/v1/users/me` - Get current user profile
- `PUT /api/v1/users/candidate-profile` - Update candidate profile
- `PUT /api/v1/users/recruiter-profile` - Update recruiter profile
- `POST /api/v1/users/upload-profile-picture` - Upload profile picture

### Job Management
- `GET /api/v1/jobs` - List jobs with filtering and search
- `POST /api/v1/jobs/` - Create new job (recruiters only)
- `GET /api/v1/jobs/{job_id}` - Get job details
- `POST /api/v1/jobs/{job_id}/save` - Save job for later

### Applications
- `GET /api/v1/applications/` - List applications
- `POST /api/v1/applications/` - Submit job application
- `GET /api/v1/applications/{id}` - Get application details
- `PUT /api/v1/applications/{id}/status` - Update application status

### Companies
- `GET /api/v1/companies/` - List companies
- `POST /api/v1/companies/` - Create company profile
- `GET /api/v1/companies/{id}` - Get company details
- `GET /api/v1/companies/{id}/jobs` - Get company jobs

## 🧪 Testing

Run the comprehensive API test suite:

```bash
python test_api.py
```

## 🔧 Configuration

Key environment variables:

```env
# Database
DATABASE_URL=sqlite:///./hire_quick.db

# Security
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Email (for notifications)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

## 🚀 Deployment

### Docker Deployment (Recommended)
```bash
# Build and run with Docker
docker build -t hire-quick-api .
docker run -p 8000:8000 hire-quick-api
```

### Production Deployment
- Use PostgreSQL for production database
- Set up Redis for caching and background tasks
- Configure proper CORS settings
- Set up SSL/TLS certificates
- Use a reverse proxy (nginx)
- Set up monitoring and logging

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- **Email**: support@hirequick.com
- **Documentation**: [API Docs](https://your-domain.com/docs)
- **Issues**: [GitHub Issues](https://github.com/blodline57/Hire-quick/issues)

## 🎯 Roadmap

- [ ] AI-powered resume parsing
- [ ] Advanced job matching algorithms
- [ ] Real-time chat system
- [ ] Video interview integration
- [ ] Mobile app API support
- [ ] Advanced analytics dashboard
- [ ] Multi-language support
- [ ] Enterprise SSO integration

---

**Built with ❤️ using FastAPI and modern Python**
