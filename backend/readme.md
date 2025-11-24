# Vacation Planner - AI-Powered Travel Planning

## Problem Definition

Perusahaan meminta sebuah proof-of-concept (PoC) untuk membangun AI Vacation Planner yang mampu:

1. Menganalisis preferensi pengguna (lokasi, tanggal, budget).
2. Merencanakan itinerary liburan secara otomatis.
3. Memanggil tools untuk melakukan pencarian data (mock).
4. Melakukan booking jika pengguna memberikan izin.
5. Menggunakan teknologi GenAI open-source atau provider bebas biaya.
6. Menyediakan arsitektur, penjelasan, dan evaluasi risiko.

PoC tidak membutuhkan integrasi API pakah nyata, tetapi harus menunjukkan alur kerja yang realistis, tool-calling, dan autonomous planning menggunakan LLM.

## 2. High-Level Approach

Solusi yang dibangun menggunakan LangChain Agent (function-calling) sebagai central planner, dan Google Gemini sebagai penyedia LLM.
Semua data pencarian (hotel, destinasi, biaya) menggunakan mock dataset untuk menjaga stabilitas PoC.

LLM bertindak sebagai Planner Agent, kemudian memanggil tools untuk:

- Pencarian destinasi
- Validasi tanggal
- Analisis budget
- Pencarian hotel
- Booking

Agent menggunakan format function-calling sehingga LLM dapat memanggil fungsi Python secara otomatis berdasarkan kebutuhan.

## 3. 3. High-Level Architecture
```bash
──────────────────────────────────────────────
               User Interface  
──────────────────────────────────────────────
               (Web UI / CLI)
                        │
                        ▼
──────────────────────────────────────────────
            LangChain Agent Executor
──────────────────────────────────────────────
   - Planner Agent  
   - Function-calling logic  
   - Prompt orchestration  
                        │
                        ▼
──────────────────────────────────────────────
               Tools Layer (Mock)
──────────────────────────────────────────────
   search_destination()
   search_date_range()
   search_budget()
   search_hotels()
   booking_tool()
                        │
                        ▼
──────────────────────────────────────────────
         Gemini LLM (API Provider)
──────────────────────────────────────────────
   - Reasoning  
   - Itinerary generation  
   - Tool selection  
──────────────────────────────────────────────
```
## 4. Core Workflow
1. User Input

Pengguna memasukkan prompt seperti:

```bash
“Saya ingin liburan 3 hari ke Bali, budget 2 juta, tanggal 1–3 Februari.”
```

2. LangChain Agent menerima input

Agent membaca konteks dan memutuskan tool apa yang perlu dipanggil.

3. Agent melakukan tool-calling

Contoh urutan panggilan:

-  search_destination("beach")
- search_budget(2000000)
- search_date_range("1 Feb", "3 Feb")
- search_hotels("Bali")

4. LLM menyusun itinerary lengkap

Dengan mempertimbangkan:

- destinasi pilihan
- hotel yang tersedia
- estimasi biaya
- urutan aktivitas
- transportasi dasar

5. (Opsional) Booking Agent

Jika user menambahkan:

```bash
“Ya, lakukan booking.”
```

Maka agent memanggil booking_tool().

## 6. Example Output
Day 1:
- Tiba di Bandara Ngurah Rai (estimasi 10.00)
- Check-in: Amnaya Resort Kuta (Rp 850.000/malam)
- Kunjungan: Pantai Kuta (gratis)
- Makan siang: Warung Makan Adi (30k)
- Sunset: Uluwatu Temple (50k)
...

Estimasi total 3 hari: Rp 2.050.000  
Booking: Siap dilakukan.

## 7. Mock Data Structure

Mock data mencakup:

Destinasi

atraksi

harga tiket

cuaca per bulan

Hotel

harga

rating

fasilitas

Transport

harga pesawat

durasi

jarak hotel

Data ini digunakan agar alur PoC terlihat seperti API nyata.

## 8. Risks & Vulnerability Assessment
### Risk 1 — Model Hallucination

Attack scenario: LLM salah merekomendasikan harga/aktivitas.
Likelihood: Medium
Impact: Medium
Mitigation:
 - Gunakan mock data yang rigid
 - Batasi model agar tidak membuat fakta baru

Monitoring:
 - Logging output itinerary
 - Validasi struktur JSON

### Risk 2 — Tool Misuse

Scenario: Agent memanggil tool yang tidak relevan.
Likelihood: Low
Impact: Medium
Mitigation:
-  Function-calling dengan schema jelas

Monitoring:
-  Log setiap tool-call

### Risk 3 — API Abuse / Key Exposure

Scenario: Gemini API key bocor.
Likelihood: Low
Impact: High
Mitigation:
- Simpan key di environment variables
- Jangan commit .env ke Github
Monitoring:
- Rotasi key
- Audit log pada Gemini dashboard

### Risk 4 — Infinite Reasoning Loop

Scenario: Agent stuck dalam analisis.
Likelihood: Low
Impact: Medium
Mitigation:
- Batasi tokens
- Atur max steps LangChain
Monitoring:
- Timeout per task

## 🚀 Quick Start

### Option 1: Docker (Recommended) 🐳

```bash
# Clone repository
git clone <repo-url>
cd vacation-planner

# Copy environment file
cp .env.docker .env

# Edit .env and add your Gemini API Key
# GEMINI_API_KEY=your_api_key_here

# Start all services
make dev

# Check health
make health
```

Open http://localhost:8000/docs for Swagger UI

### Option 2: Local Development

#### Prerequisites
- Python 3.10+
- Gemini API Key
- Git

#### Setup
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

# Copy environment
cp .env.example .env
# Edit .env and add your Gemini API Key

# Run API
uvicorn app.main:app --reload --port 8000

# or Docker
docker compose up --build 
```

Open http://localhost:8000/docs for Swagger UI

---

## 🐳 Docker Commands

| Command | Description |
|---------|-------------|
| `make dev` | Start development environment |
| `make prod` | Start production environment |
| `make down` | Stop all services |
| `make logs` | View logs (follow mode) |
| `make logs-api` | View API logs only |
| `make shell` | Open shell in API container |
| `make test` | Run tests in container |
| `make clean` | Remove containers & volumes |
| `make status` | Show container status |
| `make health` | Check health of all services |

See `docs/docker-setup.md` for detailed Docker documentation.

---

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

### List Bookings
```bash
curl http://localhost:8000/api/v1/bookings?user_id=user_1
```

---

## 🔐 Payment Tokens (Mock)

For testing, use these payment tokens:
- `tok_valid_xxx` - Payment will succeed ✅
- `tok_fail_xxx` - Payment will be declined ❌
- Other tokens - Will fail with "invalid token" ⚠️

---

## 🏗️ Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Frontend  │────▶│   FastAPI   │────▶│  LangChain  │
│  (Next.js)  │     │   Backend   │     │    Agent    │
└─────────────┘     └──────┬──────┘     └──────┬──────┘
                          │                    │
                    ┌─────▼─────┐        ┌─────▼─────┐
                    │ PostgreSQL│        │ Gemini API│
                    │    DB     │        │    LLM    │
                    └───────────┘        └───────────┘
```

### Docker Architecture

```
┌─────────────────────────────────────────────┐
│                 Host Machine                 │
├─────────────────────────────────────────────┤
│  ┌─────────────┐      ┌─────────────┐       │
│  │  API (8000) │      │ PostgreSQL  │       │
│  │  FastAPI    │◄────►│   (5432)    │       │
│  └──────┬──────┘      └─────────────┘       │
│         │                                    │
│         ▼                                    │
│  Gemini API (External)                      │
│                                              │
│  Volumes:                                    │
│  - api-data (database)                      │
│  - api-logs (logs)                          │
│  - postgres-data (database files)           │
└─────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| LLM | Google Gemini API |
| Agent | LangChain |
| Backend | FastAPI + Uvicorn |
| Database | PostgreSQL (Production) / SQLite (Dev) |
| Logging | Loguru |
| Containerization | Docker + Docker Compose |

---

## 📁 Project Structure

```
vacation-planner/
├── backend/
│   ├── Dockerfile           # Production
│   ├── Dockerfile.dev       # Development
│   ├── .dockerignore
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI entry point
│   │   ├── config.py            # Configuration & env vars
│   │   ├── database.py          # SQLAlchemy models & DB setup
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── schemas.py       # Pydantic schemas
│   │   ├── agents/
│   │   │   ├── __init__.py
│   │   │   └── planner.py       # LangChain agent
│   │   ├── tools/
│   │   │   ├── __init__.py
│   │   │   ├── search.py        # Search tools (mock)
│   │   │   ├── calendar.py      # Calendar tools (mock)
│   │   │   └── booking.py       # Booking & payment tools
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   ├── plans.py         # Plan endpoints
│   │   │   └── bookings.py      # Booking endpoints
│   │   └── utils/
│   │       ├── __init__.py
│   │       └── logger.py        # Audit logging
│   ├── data/
│   │   └── calendar_mock.json   # Mock calendar data
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py          # Pytest fixtures
│   │   ├── test_api.py          # API endpoint tests
│   │   └── test_tools.py        # Tool unit tests
│   ├── .env.example
│   ├── pytest.ini
│   └── requirements.txt
├── docs/
│   ├── security.md              # Security analysis
│   └── docker-setup.md          # Docker documentation
├── docker-compose.yml           # Production compose
├── docker-compose.dev.yml       # Development compose
├── Makefile                     # Command shortcuts
├── .env.docker                  # Docker env template
├── .gitignore
└── README.md
```

---

## ⚙️ Configuration

### Environment Variables

Create `.env` file from template:

```bash
cp .env.docker .env
```

Key variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_NAME` | Vacation Planner API | Application name |
| `DEBUG` | false | Enable debug mode |
| `GEMINI_API_KEY` | - | **Required**: Your Gemini API key |
| `DATABASE_URL` | sqlite:///./vacation_planner.db | Database connection |
| `MAX_BUDGET_IDR` | 50000000 | Max booking amount (50M IDR) |

### Get Gemini API Key

1. Go to https://makersuite.google.com/app/apikey
2. Create new API key
3. Copy and paste to `.env`:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```

---

## ⚠️ Security Considerations

See `docs/security.md` for full risk analysis. Key points:

1. **Payment tokens are never logged** - Sanitized before any logging
2. **Explicit confirmation required** - No booking without `confirmed: true`
3. **Audit trail** - All booking actions are logged
4. **Budget limits** - Max 50M IDR per transaction
5. **Input validation** - Pydantic schemas validate all inputs
6. **Non-root container** - Docker runs as unprivileged user

---

## 🧪 Testing

### Local Testing
```bash
# Run tests
cd backend
pytest tests/ -v

# With coverage
pytest tests/ --cov=app --cov-report=html
```

### Docker Testing
```bash
# Run tests in container
make test

# With coverage
make test-cov
```

---

## 📝 Example Response

### Plan Creation Response
```json
{
  "plan_id": "plan_abc123",
  "status": "draft",
  "user_id": "user_1",
  "created_at": "2025-12-15T10:30:00",
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
            "name": "Arrival & Hotel Check-in",
            "description": "Arrive at Yogyakarta and check into hotel",
            "estimated_cost": 0
          },
          {
            "time": "14:00",
            "name": "Malioboro Street Walking Tour",
            "description": "Explore the famous shopping street",
            "estimated_cost": 0
          },
          {
            "time": "18:00",
            "name": "Traditional Javanese Dinner",
            "description": "Enjoy local cuisine at Gudeg Yu Djum",
            "estimated_cost": 150000
          }
        ],
        "lodging": {
          "name": "Rumah Palagan Homestay",
          "price": 350000
        },
        "transport": {
          "type": "Airport transfer + local transport",
          "estimated_cost": 100000
        },
        "daily_cost": 600000
      }
    ],
    "total_estimated_cost": 4200000,
    "recommended_hotels": [
      {
        "id": "htl_003",
        "name": "Rumah Palagan Homestay",
        "type": "homestay",
        "price_per_night": 350000,
        "rating": 4.8,
        "amenities": ["wifi", "local breakfast", "garden"]
      }
    ],
    "notes": "Budget-friendly cultural experience with authentic local stays"
  }
}
```

### Booking Confirmation Response
```json
{
  "success": true,
  "plan_id": "plan_abc123",
  "bookings": [
    {
      "booking_id": "bkg_def456",
      "plan_id": "plan_abc123",
      "booking_type": "hotel",
      "provider_ref": "HTL-A1B2C3D4",
      "status": "confirmed",
      "amount_idr": 1400000,
      "created_at": "2025-12-15T10:35:00"
    }
  ],
  "total_charged": 4200000,
  "message": "Booking confirmed! Transaction ID: txn_xyz789"
}
```

---

## 🔧 Troubleshooting

### API not starting
```bash
# Check logs
make logs-api

# Verify Gemini API key is set
docker-compose exec api printenv | grep GEMINI

# Restart services
make down && make dev
```

### Database issues
```bash
# Reset database
make db-reset

# Or manually
docker-compose exec api rm -f vacation_planner.db
docker-compose restart api
```

### Port already in use
```bash
# Check what's using port 8000
sudo lsof -i :8000

# Change port in docker-compose.yml if needed
```

---

## 📚 Documentation

- **API Documentation**: http://localhost:8000/docs (Swagger UI)
- **Security Analysis**: [docs/security.md](docs/security.md)
- **Docker Setup Guide**: [docs/docker-setup.md](docs/docker-setup.md)
- **Architecture Document**: [docs/architecture.md](docs/architecture.md) *(coming soon)*

---

## 🚀 Deployment

### Development
```bash
make dev
```

### Production
```bash
make prod
```

### Cloud Deployment

The application can be deployed to:
- **Railway**: Direct GitHub integration
- **Render**: Docker-based deployment
- **AWS ECS**: Container orchestration
- **Google Cloud Run**: Serverless containers

See deployment guides in `docs/deployment/` *(coming soon)*

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

## 📄 License

MIT License - See LICENSE file