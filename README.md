# 🚀 Kintari Backend - Universal Knowledge Base

Backend API untuk Kintari dengan **Universal Document Knowledge Base System** yang dapat memproses **ANY PDF document** sebagai knowledge base.

## ✨ Fitur Utama

- 📄 **Upload ANY PDF** - HIPMI, contracts, reports, manuals, presentations, etc.
- 🤖 **AI Chatbot** - Menggunakan SEMUA dokumen sebagai konteks (powered by Gemini AI)
- 🔍 **Smart Search** - Full-text search across all uploaded documents
- 📊 **Auto Extraction** - Text, tables, emails, dates, phone numbers, keywords
- 🎯 **Auto Detection** - Otomatis kategorisasi tipe dokumen (12 types)
- 📁 **Collections** - Kelompokkan dokumen yang berkaitan
- 📈 **Statistics** - Analytics dan insights dari semua dokumen

## 📋 Tech Stack

| Komponen       | Technology                              |
| -------------- | --------------------------------------- |
| Framework      | FastAPI 0.104.1                         |
| Database       | SQLite (dev) / PostgreSQL ready         |
| ORM            | SQLAlchemy 2.x                          |
| AI             | **google-genai (gemini-2.0-flash-exp)** |
| PDF Processing | pdfplumber + PyMuPDF                    |
| Python         | 3.11+                                   |

## ⚙️ Quick Start

### 1. Clone & Setup

```bash
git clone https://github.com/Sastraaaa/kintari-be.git
cd kintari-be

# Buat virtual environment
python -m venv venv

# Aktivasi (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Aktivasi (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

Buat file `.env`:

```env
DATABASE_URL=sqlite:///./kintari.db
GEMINI_API_KEY=your_gemini_api_key_here
ALLOWED_ORIGINS=http://localhost:3000
UPLOAD_DIR=./uploads
```

### 3. Initialize Database

```bash
python init_fresh_db.py
```

### 4. Run Server

```bash
uvicorn app.main:app --reload
```

Server berjalan di: **http://localhost:8000**

## 📚 API Documentation

- **Swagger UI**: http://localhost:8000/docs ✨ (Recommended)
- **ReDoc**: http://localhost:8000/redoc

## 🔌 API Endpoints

### 📄 Universal Documents (NEW!)

| Method | Endpoint                              | Deskripsi                           |
| ------ | ------------------------------------- | ----------------------------------- |
| POST   | `/api/documents/upload`               | Upload ANY PDF document             |
| GET    | `/api/documents/`                     | List all documents (with filters)   |
| GET    | `/api/documents/{id}`                 | Get document detail                 |
| DELETE | `/api/documents/{id}`                 | Delete document                     |
| GET    | `/api/documents/search/?q=query`      | Full-text search                    |
| GET    | `/api/documents/stats/overview`       | Statistics & analytics              |
| GET    | `/api/documents/types/list`           | List all document types with counts |
| GET    | `/api/documents/type/{type}`          | Filter by document type             |
| PUT    | `/api/documents/{id}/tags`            | Update document tags                |
| PUT    | `/api/documents/{id}/category`        | Update document category            |
| POST   | `/api/documents/collections/`         | Create document collection          |
| GET    | `/api/documents/collections/`         | List all collections                |
| POST   | `/api/documents/collections/{id}/add` | Add documents to collection         |
| GET    | `/api/documents/collections/{id}`     | Get documents in collection         |

### 🤖 AI Chatbot

| Method | Endpoint            | Deskripsi                                        |
| ------ | ------------------- | ------------------------------------------------ |
| POST   | `/api/chat/query`   | Ask AI (uses ALL uploaded documents as context)  |
| GET    | `/api/chat/context` | Get current chatbot context (all document texts) |

### 👥 Members

| Method | Endpoint                  | Deskripsi           |
| ------ | ------------------------- | ------------------- |
| POST   | `/api/members/upload-csv` | Upload CSV anggota  |
| GET    | `/api/members`            | List semua anggota  |
| GET    | `/api/members/{id}`       | Get anggota by ID   |
| PUT    | `/api/members/{id}`       | Update data anggota |
| DELETE | `/api/members/{id}`       | Hapus anggota       |

### 📊 Statistics

| Method | Endpoint              | Deskripsi       |
| ------ | --------------------- | --------------- |
| GET    | `/api/stats/overview` | Dashboard stats |

## 📝 Quick Examples

### 1. Upload ANY PDF Document

```bash
curl -X POST "http://localhost:8000/api/documents/upload" \
  -F "file=@document.pdf" \
  -F "category=Contracts" \
  -F "tags=important,2024"
```

Response:

```json
{
  "id": 1,
  "filename": "document.pdf",
  "file_size": 8620000,
  "page_count": 323,
  "document_type": "HIPMI_PO",
  "extracted_entities": {
    "emails": ["hipmi@example.com"],
    "dates": ["10 Juni 1972"],
    "phones": ["+62 21 1234567"]
  },
  "keywords": ["HIPMI", "pengusaha", "organisasi"],
  "processed": true
}
```

### 2. AI Chatbot Query

```bash
curl -X POST "http://localhost:8000/api/chat/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Apa visi misi organisasi?"}'
```

Response:

```json
{
  "answer": "Berdasarkan dokumen yang tersedia...",
  "documents_used": 5,
  "context_size": 12450
}
```

### 3. Search Documents

```bash
curl "http://localhost:8000/api/documents/search/?q=contract"
```

### 4. Get Statistics

```bash
curl "http://localhost:8000/api/documents/stats/overview"
```

Response:

```json
{
  "total_documents": 15,
  "total_pages": 1234,
  "total_storage_mb": 45.6,
  "by_type": {
    "HIPMI_PO": 3,
    "CONTRACT": 5,
    "REPORT": 7
  }
}
```

## 🗂️ Project Structure

```
kintari-be/
├── app/
│   ├── main.py                           # FastAPI app entry point
│   ├── core/
│   │   ├── config.py                     # Environment & configuration
│   │   ├── database.py                   # SQLAlchemy setup
│   │   └── utils.py                      # Utility functions
│   ├── models/
│   │   ├── universal_document.py         # ⭐ NEW: Universal document models
│   │   ├── organization.py               # Organization models (legacy HIPMI)
│   │   └── member.py                     # Member model
│   ├── schemas/                          # Pydantic validation schemas
│   ├── routes/
│   │   ├── universal_documents.py        # ⭐ NEW: 16 endpoints for universal KB
│   │   ├── chat.py                       # ⭐ UPDATED: Multi-doc AI chatbot
│   │   ├── members.py                    # Members endpoints
│   │   ├── stats.py                      # Statistics endpoints
│   │   └── organization.py               # Legacy HIPMI endpoints
│   └── services/
│       ├── universal_document_processor.py # ⭐ NEW: Extract ANY PDF
│       ├── universal_document_service.py   # ⭐ NEW: Business logic
│       ├── pdf_extractor.py              # Legacy HIPMI extractor
│       └── gemini_service.py             # Gemini AI integration
├── init_fresh_db.py                      # Database initialization script
├── requirements.txt                      # Python dependencies
├── .env                                  # Environment variables (gitignored)
├── .env.example                          # Template .env
├── kintari.db                            # SQLite database (auto-created)
└── README.md                             # This file
```

## �️ Database Schema

### Main Tables (7 total):

| Table                    | Description                                  |
| ------------------------ | -------------------------------------------- |
| `universal_documents`    | ⭐ Stores ANY uploaded PDF with full content |
| `document_collections`   | ⭐ Groups related documents together         |
| `organization_info`      | HIPMI organization data (legacy)             |
| `organization_structure` | Organizational hierarchy                     |
| `membership_types`       | Membership categories                        |
| `members`                | Member information                           |
| `documents`              | Legacy document tracking                     |

### Universal Document Model (25+ fields):

```python
{
  "id": 1,
  "filename": "contract.pdf",
  "file_path": "uploads/contract.pdf",
  "file_size": 1024000,
  "page_count": 50,
  "full_text": "Extracted full text content...",
  "summary": "Auto-generated summary...",
  "extracted_entities": {
    "emails": [...],
    "dates": [...],
    "phones": [...]
  },
  "keywords": ["keyword1", "keyword2"],
  "tables_data": [...],
  "document_type": "CONTRACT",
  "category": "Legal",
  "tags": ["important", "2024"],
  "ai_summary": "AI-generated insights...",
  "processed": true,
  "uploaded_at": "2024-01-01T00:00:00"
}
```

## 🎯 Supported Document Types (12 total)

Auto-detected types:

- **HIPMI Documents**: `HIPMI_PO`, `HIPMI_AD`, `HIPMI_ART`, `HIPMI_SK`, `HIPMI_DOCUMENT`
- **Business**: `CONTRACT`, `REPORT`, `PROPOSAL`, `PRESENTATION`
- **General**: `REGULATION`, `MANUAL`, `OTHER` (fallback)

## 🤖 How It Works

```
1️⃣ Upload ANY PDF document
       ↓
2️⃣ Auto Extract Content:
   • Full text (all pages)
   • Tables with structure
   • Emails, dates, phones, URLs
   • Keywords (top 20)
       ↓
3️⃣ Auto Detect Type (12 types)
       ↓
4️⃣ Save to Database (with rich metadata)
       ↓
5️⃣ AI Chatbot uses ALL documents as knowledge base
       ↓
6️⃣ Ask questions → Get intelligent answers!
```

**Example Extraction Result:**

- **Input**: 8.62 MB PDF (323 pages)
- **Extracted**: 497,634 characters
- **Found**: 160 dates, 35 emails, 62 phone numbers, 50 tables
- **Keywords**: 20 auto-generated
- **Processing Time**: ~15 seconds

## 🐛 Troubleshooting

| Issue                      | Solution                                           |
| -------------------------- | -------------------------------------------------- |
| `ModuleNotFoundError`      | Pastikan venv aktif: `.\venv\Scripts\Activate.ps1` |
| `Database locked`          | Hapus `kintari.db`, run `python init_fresh_db.py`  |
| `GEMINI_API_KEY not found` | Set di `.env`: `GEMINI_API_KEY=your_key`           |
| Port 8000 sudah terpakai   | Gunakan: `uvicorn app.main:app --port 8001`        |
| Upload gagal               | Cek folder `uploads/` exists & permissions         |

## � Production Deployment

```bash
# Install production server
pip install gunicorn

# Run with gunicorn (4 workers)
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

**Production Checklist:**

- ✅ Migrate to PostgreSQL
- ✅ Setup HTTPS/SSL
- ✅ Configure CORS properly
- ✅ Setup monitoring (logs, metrics)
- ✅ Backup database regularly
- ✅ Rate limiting for API endpoints

## 🤝 Integration dengan Frontend

Frontend Next.js dapat mengakses backend di:

- **Development**: `http://localhost:8000`
- **Production**: Configure `ALLOWED_ORIGINS` di `.env`

**Example Frontend Integration:**

```typescript
// Upload document
const formData = new FormData();
formData.append("file", file);
formData.append("category", "Contracts");

const response = await fetch("http://localhost:8000/api/documents/upload", {
  method: "POST",
  body: formData,
});

// AI Chatbot query
const chatResponse = await fetch("http://localhost:8000/api/chat/query", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ query: "What is HIPMI vision?" }),
});
```

## � Features Comparison

| Feature                 | Old System (HIPMI-only) | New System (Universal KB)      |
| ----------------------- | ----------------------- | ------------------------------ |
| Supported Documents     | HIPMI only              | **ANY PDF** ✅                 |
| Auto Content Extraction | Basic                   | **Rich (25+ fields)** ✅       |
| Entity Detection        | ❌                      | **✅ (emails, dates, phones)** |
| Document Type Detection | Manual                  | **Auto (12 types)** ✅         |
| AI Chatbot Context      | Single document         | **Multi-document** ✅          |
| Full-text Search        | ❌                      | **✅**                         |
| Document Collections    | ❌                      | **✅**                         |
| Analytics & Statistics  | Basic                   | **Advanced** ✅                |

---

**🎉 Ready to use! Upload any document and start asking AI questions!**

**Last Updated**: January 2025 | **Version**: 2.0.0 (Universal KB)
