# 🚀 Kintari Backend API

Backend FastAPI untuk Kintari dengan kemampuan ekstraksi dokumen HIPMI dan integrasi Gemini AI chatbot.

## ✨ Fitur Utama

- ✅ Upload & ekstraksi dokumen PDF (HIPMI, AD/ART, PO, SK)
- ✅ Integrasi Gemini API untuk AI chatbot & summarization
- ✅ CRUD untuk data anggota, dokumen, organisasi
- ✅ Auto-generated API docs (Swagger & ReDoc)
- ✅ SQLite database dengan SQLAlchemy ORM
- ✅ CLI commands untuk easy development (`kintari dev`, `kintari start`)

## 📋 Prerequisites

- Python 3.11+
- pip (Python package manager)

## ⚙️ Quick Start

### 1. Setup Environment

```bash
# Buat virtual environment
python -m venv venv

# Aktivasi (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Aktivasi (Windows CMD)
venv\Scripts\activate.bat

# Aktivasi (Linux/Mac)
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

Buat file `.env`:

```env
DATABASE_URL=sqlite:///./kintari.db
GEMINI_API_KEY=your_gemini_api_key_here
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
UPLOAD_DIR=./uploads
```

### 4. Run Server

**Option A: Manual (Recommended)**

```bash
uvicorn app.main:app --reload
```

**Option B: Using CLI**

```bash
# Development mode (dengan auto-reload)
kintari dev

# Production mode (tanpa reload)
kintari start

# Lihat bantuan
kintari help
```

Server berjalan di `http://localhost:8000`

## 📚 API Documentation

Setelah aplikasi berjalan, akses dokumentasi interaktif:

- **Swagger UI**: http://localhost:8000/docs (Recommended)
- **ReDoc**: http://localhost:8000/redoc

## 🔌 API Endpoints

| Method                            | Endpoint                      | Deskripsi                          |
| --------------------------------- | ----------------------------- | ---------------------------------- |
| **Organization (PDF Extraction)** |
| POST                              | `/api/organization/upload`    | Upload & ekstrak dokumen PDF HIPMI |
| GET                               | `/api/organization/latest`    | Ambil data organisasi terbaru      |
| GET                               | `/api/organization/all`       | Ambil semua data organisasi        |
| GET                               | `/api/organization/data/{id}` | Ambil data organisasi by ID        |
| POST                              | `/api/organization/summarize` | Ringkas konteks organisasi         |
| **Chat (Chatbot)**                |
| POST                              | `/api/chat/query`             | Tanya jawab berbasis konteks HIPMI |
| GET                               | `/api/chat/context`           | Ambil konteks chatbot              |
| **Members**                       |
| POST                              | `/api/members/upload-csv`     | Upload data anggota dari CSV       |
| GET                               | `/api/members`                | List semua anggota                 |
| **Documents**                     |
| POST                              | `/api/documents/upload`       | Upload dokumen                     |
| GET                               | `/api/documents`              | List semua dokumen                 |
| **Statistics**                    |
| GET                               | `/api/stats/overview`         | Overview statistik organisasi      |

📌 **Semua endpoint lengkap tersedia di Swagger UI** (`/docs`)

## 📝 Quick Examples

### Upload Dokumen HIPMI

```bash
curl -X POST "http://localhost:8000/api/organization/upload" \
  -F "file=@document.pdf"
```

### Tanya Jawab (Chatbot)

```bash
curl -X POST "http://localhost:8000/api/chat/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Apa tujuan HIPMI?"}'
```

### Lihat Statistik

```bash
curl -X GET "http://localhost:8000/api/stats/overview"
```

## 🗂️ Project Structure

```
kintari-be/
├── app/
│   ├── main.py              # Entry point FastAPI
│   ├── cli.py               # CLI commands (kintari dev/start)
│   ├── core/
│   │   ├── config.py        # Environment & configuration
│   │   ├── database.py      # SQLAlchemy setup
│   │   └── utils.py         # Utility functions
│   ├── models/
│   │   ├── organization.py  # Organization, MembershipType, OrgStructure
│   │   └── member.py        # Member model
│   ├── schemas/             # Pydantic validation schemas
│   ├── routes/              # API endpoints (organization, chat, members, etc)
│   └── services/            # Business logic (pdf_extractor, gemini_service, etc)
├── tests/                   # Unit & integration tests
├── uploads/                 # Folder untuk file uploads
├── venv/                    # Virtual environment
├── requirements.txt         # Python dependencies
├── pyproject.toml           # CLI entry points
├── setup.py                 # Setup script
├── .env                     # Environment variables (gitignored)
├── .env.example             # Template .env
├── kintari.db               # SQLite database (auto-created)
└── README.md                # File ini
```

## 🐛 Troubleshooting

| Issue                      | Solution                                           |
| -------------------------- | -------------------------------------------------- |
| `ModuleNotFoundError`      | Pastikan venv aktif: `.\venv\Scripts\Activate.ps1` |
| `Database locked`          | Hapus `kintari.db`, jalankan ulang server          |
| `GEMINI_API_KEY not found` | Set di `.env`: `GEMINI_API_KEY=your_key`           |
| Port 8000 sudah terpakai   | Gunakan: `uvicorn app.main:app --port 8001`        |

## 📦 Roadmap

- [x] Batch 1: Setup CRUD + SQLite
- [x] Batch 2: PDF Extraction + Gemini Summarizer
- [x] Batch 3: Chatbot Retrieval + CLI
- [ ] Batch 4: Frontend Integration
- [ ] Batch 5: PostgreSQL Migration

## � Security

- 🚫 Jangan commit `.env` (sudah di `.gitignore`)
- 🔑 Gunakan valid GEMINI_API_KEY
- 🌐 Batasi ALLOWED_ORIGINS untuk production
- 🔒 Setup HTTPS untuk production deployment

## 📄 Tech Stack

| Layer     | Technology                              |
| --------- | --------------------------------------- |
| Framework | FastAPI 0.104.1                         |
| Server    | Uvicorn 0.24.0                          |
| Database  | SQLite + SQLAlchemy                     |
| ORM       | SQLAlchemy 2.x + Alembic                |
| PDF       | pdfplumber + PyMuPDF                    |
| AI        | **google-genai (gemini-2.0-flash-exp)** |
| Testing   | pytest + pytest-asyncio                 |

## 🤝 Integration dengan Frontend

Frontend Next.js dapat mengakses backend di:

- Development: `http://localhost:8000`
- Production: Configure di `ALLOWED_ORIGINS` di `.env`

## 📞 Support

Untuk bantuan atau pertanyaan:

1. Cek Swagger UI di `/docs`
2. Cek console log server untuk error details
3. Baca `.env.example` untuk konfigurasi yang tepat

---

**Last Updated**: October 20, 2025 | **Version**: 1.0.0
