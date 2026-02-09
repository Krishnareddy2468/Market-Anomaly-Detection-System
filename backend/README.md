# Market Anomaly Detection System - Backend

A robust, scalable FastAPI backend for fraud detection and market anomaly monitoring.

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                      Frontend (Next.js)                         │
└──────────────────────────┬──────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    REST API Layer (FastAPI)                     │
│  • Route handling         • Input validation                    │
│  • Authentication         • Error formatting                    │
└──────────────────────────┬──────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                 Service Layer (Business Logic)                  │
│  • Alert management       • Risk interpretation                 │
│  • Investigation flow     • Status transitions                  │
└──────────────────────────┬──────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│               Detection & Scoring Engine                        │
│  ┌───────────────┐ ┌───────────────┐ ┌───────────────┐         │
│  │ Statistical   │ │ Behavioral    │ │ ML Detector   │         │
│  │ Detector      │ │ Detector      │ │               │         │
│  └───────┬───────┘ └───────┬───────┘ └───────┬───────┘         │
│          └─────────────┬───────────────────────┘                │
│                        ▼                                        │
│               ┌───────────────┐                                 │
│               │ Risk Scorer   │                                 │
│               └───────────────┘                                 │
└──────────────────────────┬──────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Persistence Layer (Database)                   │
│  • Transactions          • Alerts                               │
│  • Investigations        • Feedback                             │
└─────────────────────────────────────────────────────────────────┘
```

## 📁 Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry
│   ├── config.py               # Configuration management
│   │
│   ├── api/                    # API Layer (Controllers)
│   │   ├── routes/
│   │   │   ├── alerts.py       # Alert endpoints
│   │   │   ├── analytics.py    # Analytics endpoints
│   │   │   ├── dashboard.py    # Dashboard endpoints
│   │   │   ├── feedback.py     # Feedback endpoints
│   │   │   └── investigations.py
│   │   ├── dependencies.py     # Dependency injection
│   │   └── middleware.py       # CORS, logging, observability
│   │
│   ├── services/               # Business Logic Layer
│   │   ├── alert_service.py
│   │   ├── analytics_service.py
│   │   ├── dashboard_service.py
│   │   ├── feedback_service.py
│   │   └── investigation_service.py
│   │
│   ├── detection/              # Detection & Scoring Engine
│   │   ├── engine.py           # Main detection orchestrator
│   │   ├── detectors/
│   │   │   ├── base.py         # Abstract detector interface
│   │   │   ├── statistical.py  # Rule-based detector
│   │   │   ├── behavioral.py   # Pattern analysis detector
│   │   │   └── ml_detector.py  # ML-based detector
│   │   ├── scoring/
│   │   │   ├── risk_scorer.py  # Score aggregation
│   │   │   └── normalizer.py   # Score normalization
│   │   └── features/
│   │       └── feature_engineer.py
│   │
│   ├── models/                 # Data Models
│   │   ├── schemas.py          # Pydantic schemas (API contracts)
│   │   ├── enums.py            # Enumerations
│   │   └── database.py         # SQLAlchemy models
│   │
│   ├── db/                     # Database Layer
│   │   ├── session.py          # Async session management
│   │   ├── models.py           # SQLAlchemy ORM models
│   │   └── repositories/
│   │       ├── alert_repository.py
│   │       ├── feedback_repository.py
│   │       └── transaction_repository.py
│   │
│   └── core/                   # Core Utilities
│       ├── errors.py           # Exception handling
│       ├── logging.py          # Structured logging
│       └── observability.py    # Metrics collection
│
├── tests/                      # Test suite
├── requirements.txt            # Python dependencies
├── .env.example               # Environment template
└── README.md                  # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- pip or uv package manager

### Installation

1. **Create virtual environment:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your settings
```

4. **Run the server:**
```bash
# Development mode (with auto-reload)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or using Python directly
python -m app.main
```

5. **Access the API:**
- API: http://localhost:8000
- Docs: http://localhost:8000/docs (Swagger UI)
- ReDoc: http://localhost:8000/redoc

## 📚 API Endpoints

### Dashboard
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/dashboard/metrics` | Get KPI metrics |
| GET | `/api/dashboard/alerts-trend` | Get alerts trend data |
| GET | `/api/dashboard/severity-distribution` | Get severity breakdown |

### Alerts
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/alerts` | List alerts with filtering |
| GET | `/api/alerts/{id}` | Get alert details |
| PATCH | `/api/alerts/{id}/status` | Update alert status |

### Investigations
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/investigations/{id}` | Get investigation context |
| POST | `/api/investigations/{id}/decision` | Submit decision |
| POST | `/api/investigations/{id}/notes` | Add investigation note |

### Analytics
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/analytics/metrics` | Get model performance |
| GET | `/api/analytics/alert-volume` | Get volume statistics |
| GET | `/api/analytics/confusion-matrix` | Get confusion matrix |

### Feedback
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/feedback` | Get resolution history |
| GET | `/api/feedback/summary` | Get feedback statistics |

## 🔧 Configuration

All configuration is managed through environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `DEBUG` | Enable debug mode | `false` |
| `DATABASE_URL` | Database connection string | SQLite |
| `CORS_ORIGINS` | Allowed CORS origins | localhost:3000 |
| `LOG_LEVEL` | Logging level | `INFO` |
| `RISK_THRESHOLD_HIGH` | High risk threshold | `80.0` |

## 🧪 Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=app --cov-report=html

# Specific test file
pytest tests/test_alert_service.py
```

## 📊 Observability

- **Metrics**: Available at `/metrics` (Prometheus format)
- **Health Check**: GET `/health`
- **Structured Logging**: JSON format in production

## 🔐 Security

- Input validation with Pydantic
- Rate limiting (configurable)
- CORS configuration
- Error messages sanitized (no stack traces in production)

## 🏭 Production Deployment

For production:

1. Set `DEBUG=false`
2. Use PostgreSQL: `DATABASE_URL=postgresql+asyncpg://...`
3. Set a secure `SECRET_KEY`
4. Configure proper `CORS_ORIGINS`
5. Set `LOG_FORMAT=json` for structured logging
6. Use multiple workers: `WORKERS=4`

## 📝 License

MIT License
