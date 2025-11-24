# 🏖️ Vacation Planner - AI-Powered Travel Planning

PoC sistem vacation planner yang menggunakan LLM untuk generate itinerary dan melakukan booking otomatis.

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Gemini API
- Git

### 1. Clone & Setup Environment
```bash
git clone <repo-url>
cd vacation-planner

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
# Copy example env
cp .env.example .env

# Edit if needed (defaults work for local development)
```

### 3. Run the API
```bash
# From backend directory
uvicorn app.main:app --reload --port 8000

# Or directly
python -m app.main
```

### 4. Test the API
Open http://localhost:8000/docs for Swagger UI

## 📡 API Endpoints

### Create Itinerary
```bash
curl -X POST http://localhost:8000/api/v1/plan \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_1",
    "destination": "Yogyakarta",
    "start_date": "2025-12-20",
    "end_date": "2025-12-24",
    "budget_idr": 5000000,
    "travel_type": "culture",
    "travelers": 2,
    "preferences": "prefer homestay and local food"
  }'
```

### Get Plan
```bash
curl http://localhost:8000/api/v1/plan/{plan_id}
```

### Confirm & Book
```bash
curl -X POST http://localhost:8000/api/v1/plan/{plan_id}/confirm \
  -H "Content-Type: application/json" \
  -d '{
    "plan_id": "plan_xxx",
    "user_id": "user_1",
    "payment_token": "tok_valid_123",
    "confirmed": true
  }'
```

## 🔐 Payment Tokens (Mock)

For testing, use these payment tokens:
- `tok_valid_xxx` - Payment will succeed
- `tok_fail_xxx` - Payment will be declined
- Other tokens - Will fail with "invalid token"

## 🏗️ Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Frontend  │────▶│   FastAPI  │────▶│  LangChain  │
│  (Next.js)  │     │   Backend   │     │    Agent    │
└─────────────┘     └──────┬──────┘     └──────┬──────┘
                          │                    │
                    ┌─────▼─────┐        ┌─────▼─────┐
                    │  Postgre  │        │ Gemini API│
                    │    DB     │        │    LLM    │
                    └───────────┘        └───────────┘
```

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| LLM       | Gemini     |
| Agent     | LangChain  |
| Backend   | FastAPI + Uvicorn |
| Database  | Postgre    |
| Logging   | Loguru     |

## 📁 Project Structure

```
backend/
├── app/
│   ├── main.py           # FastAPI entry point
│   ├── config.py         # Settings
│   ├── database.py       # SQLAlchemy models
│   ├── models/
│   │   └── schemas.py    # Pydantic schemas
│   ├── agents/
│   │   └── planner.py    # LangChain agent
│   ├── tools/
│   │   ├── search.py     # Search tools (mock)
│   │   ├── calendar.py   # Calendar tools (mock)
│   │   └── booking.py    # Booking & payment tools
│   ├── routers/
│   │   ├── plans.py      # Plan endpoints
│   │   └── bookings.py   # Booking endpoints
│   └── utils/
│       └── logger.py     # Audit logging
├── logs/                 # Log files
├── requirements.txt
└── .env
```

## ⚠️ Security Considerations

See `docs/security.md` for full risk analysis. Key points:

1. **Payment tokens are never logged** - Sanitized before any logging
2. **Explicit confirmation required** - No booking without `confirmed: true`
3. **Audit trail** - All booking actions are logged
4. **Budget limits** - Max 50M IDR per transaction

## 🧪 Testing

```bash
# Run tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=app --cov-report=html
```

## 📝 Example Response

```json
{
  "plan_id": "plan_abc123",
  "status": "draft",
  "itinerary": {
    "trip_name": "Cultural Journey to Yogyakarta",
    "destination": "Yogyakarta",
    "start_date": "2025-12-20",
    "end_date": "2025-12-24",
    "days": [
      {
        "date": "2025-12-20",
        "activities": [
          {
            "time": "09:00",
            "name": "Arrival & Check-in",
            "estimated_cost": 0
          },
          {
            "time": "14:00",
            "name": "Malioboro Walking Tour",
            "estimated_cost": 0
          }
        ],
        "lodging": {"name": "Rumah Palagan Homestay", "price": 350000},
        "daily_cost": 400000
      }
    ],
    "total_estimated_cost": 4200000,
    "recommended_hotels": [...]
  }
}
```

## 📄 License

MIT License - See LICENSE file
