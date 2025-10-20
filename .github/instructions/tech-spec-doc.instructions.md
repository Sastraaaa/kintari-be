---
applyTo: "**"
---

# ⚙️ Kintari Backend Technical Specification (FastAPI + SQLite + Gemini + HIPMI Extraction)

## 📘 Ringkasan

Backend Kintari dibangun menggunakan **FastAPI (Python)** sebagai REST API utama untuk mengelola data internal organisasi dan dokumen berbasis pengetahuan. Versi ini diperbarui untuk menambahkan kemampuan **ekstraksi data dari dokumen organisasi (contohnya PDF HIPMI)** serta mengintegrasikan hasil ekstraksi tersebut ke **AI Assistant berbasis Gemini API**.

Backend menyimpan semua hasil parsing PDF HIPMI ke database (SQLite) agar dapat digunakan dalam statistik dan menjawab pertanyaan AI tanpa memerlukan halaman khusus di Frontend.

---

## 🎯 Tujuan Utama

1. Menyediakan API CRUD untuk data anggota dan dokumen organisasi.
2. Memproses dan menyimpan hasil ekstraksi dokumen PDF organisasi (HIPMI, AD/ART, PO, SK, dll).
3. Menghasilkan ringkasan dan konteks AI dari hasil ekstraksi menggunakan **Gemini API**.
4. Menyediakan chatbot retrieval endpoint untuk menjawab pertanyaan berbasis dokumen HIPMI.
5. Menyajikan statistik organisasi ke Frontend.
6. Tetap kompatibel penuh dengan FE Kintari (Next.js App Router) tanpa perlu halaman tambahan.

---

## 🧭 Arsitektur Sistem

```
📄 PDF HIPMI (dokumen organisasi)
   ↓
🧠 Backend FastAPI
   ├── Ekstraksi teks & metadata (PDF Parser)
   ├── Simpan hasil ke DB SQLite
   ├── Summarize konteks → Gemini API
   ├── Sediakan data untuk dashboard & AI Chatbot
   ↓
💬 Frontend Next.js (Dashboard + Chatbot)
```

---

## ⚙️ Stack Teknologi

| Komponen     | Teknologi                          |
| ------------ | ---------------------------------- |
| Bahasa       | Python 3.11+                       |
| Framework    | FastAPI                            |
| Database     | SQLite (dev) / MySQL (future)      |
| ORM          | SQLAlchemy 2.x + Alembic           |
| AI           | Gemini API (Google Generative AI)  |
| File Parsing | PyMuPDF (fitz), pdfplumber, pandas |
| Environment  | venv (virtual environment)         |
| Docs         | Swagger & ReDoc (auto)             |

---

## 🧱 Struktur Folder (Best Practice)

```
backend/
├── app/
│   ├── main.py
│   ├── core/
│   │   ├── config.py
│   │   ├── database.py
│   │   └── utils.py
│   ├── models/
│   │   ├── member.py
│   │   ├── document.py
│   │   ├── organization.py      # ✅ baru: hasil ekstraksi HIPMI
│   │   └── embedding.py
│   ├── schemas/
│   │   ├── member_schema.py
│   │   ├── document_schema.py
│   │   ├── organization_schema.py # ✅ baru
│   │   └── chat_schema.py
│   ├── routes/
│   │   ├── members.py
│   │   ├── documents.py
│   │   ├── chat.py
│   │   ├── stats.py
│   │   └── organization.py      # ✅ baru: upload & ambil data hasil ekstraksi
│   ├── services/
│   │   ├── csv_parser.py
│   │   ├── pdf_extractor.py     # ✅ baru: ekstraksi teks & tabel dari PDF HIPMI
│   │   ├── summarizer.py
│   │   ├── retriever.py
│   │   └── embedding.py
│   └── __init__.py
├── tests/
│   ├── test_members.py
│   ├── test_documents.py
│   ├── test_chat.py
│   └── test_organization.py
├── requirements.txt
├── .env.example
└── README.md
```

---

## ⚡ Instalasi & Setup Lingkungan

```bash
python -m venv .env
source .env/bin/activate   # Linux/Mac
.env\\Scripts\\activate    # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

---

## 📦 Contoh `requirements.txt`

```
fastapi
uvicorn
sqlalchemy
alembic
pdfplumber
PyMuPDF
pandas
python-dotenv
requests
httpx
pytest
```

---

## ⚙️ Konfigurasi `.env`

```env
DATABASE_URL=sqlite:///./kintari.db
GEMINI_API_KEY=your_gemini_api_key_here
ALLOWED_ORIGINS=http://localhost:3000
```

---

## 🧩 Model Baru — `organization.py`

```python
from sqlalchemy import Column, Integer, String, Text
from app.core.database import Base

class OrganizationInfo(Base):
    __tablename__ = "organization_info"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    founded = Column(String)
    ideology = Column(String)
    legal_basis = Column(Text)
    summary = Column(Text)

class MembershipType(Base):
    __tablename__ = "membership_types"
    id = Column(Integer, primary_key=True, index=True)
    type_name = Column(String)
    description = Column(Text)
    rights = Column(Text)

class OrgStructure(Base):
    __tablename__ = "organization_structure"
    id = Column(Integer, primary_key=True, index=True)
    level = Column(String)
    name = Column(String)
    parent_id = Column(Integer)
    leader_name = Column(String)
```

---

## 🚀 Endpoint API (Integrasi Baru)

| Endpoint               | Method | Fungsi                                       |
| ---------------------- | ------ | -------------------------------------------- |
| `/upload/members`      | POST   | Upload data CSV anggota                      |
| `/upload/docs`         | POST   | Upload dokumen organisasi (PDF)              |
| `/organization/upload` | POST   | Ekstrak teks & metadata dari PDF HIPMI       |
| `/organization/data`   | GET    | Ambil hasil ekstraksi (nama, asas, struktur) |
| `/chat/query`          | POST   | Chatbot retrieval berbasis data HIPMI        |

---

## 🧠 Integrasi Gemini API (Khusus Dokumen HIPMI)

File: `app/services/summarizer.py`

```python
import requests, os

def summarize_text(text: str) -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"
    payload = {"contents": [{"parts": [{"text": f"Summarize this organization document in short paragraphs:\n{text}"}]}]}
    res = requests.post(url, json=payload)
    if res.status_code == 200:
        return res.json()["candidates"][0]["content"]["parts"][0]["text"]
    return "Summary unavailable."
```

---

## 📄 Ekstraksi Dokumen PDF HIPMI

File: `app/services/pdf_extractor.py`

```python
import pdfplumber
from app.models.organization import OrganizationInfo, MembershipType, OrgStructure

def extract_hipmi_data(file_path: str, db):
    with pdfplumber.open(file_path) as pdf:
        text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])

    # Contoh sederhana: cari kata kunci utama
    if "HIPMI" in text:
        org = OrganizationInfo(
            name="Himpunan Pengusaha Muda Indonesia (HIPMI)",
            founded="10 Juni 1972",
            ideology="Pancasila",
            legal_basis="UUD 1945 dan UU No. 1 Tahun 1987",
            summary=text[:500]
        )
        db.add(org)
        db.commit()
        return org

    return None
```

---

## 🔐 App Entry

File: `app/main.py`

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import members, documents, chat, stats, organization
from app.core.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Kintari Backend API (with HIPMI Extraction)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", "http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(members.router)
app.include_router(documents.router)
app.include_router(stats.router)
app.include_router(chat.router)
app.include_router(organization.router)
```

---

## 🧠 Chatbot dengan Konteks HIPMI

File: `app/services/retriever.py`

```python
import requests, os
from app.core.database import SessionLocal
from app.models.organization import OrganizationInfo

def chatbot_answer(query: str):
    db = SessionLocal()
    context_data = db.query(OrganizationInfo).first()
    context = context_data.summary if context_data else "HIPMI organization info unavailable."

    payload = {"contents": [{"parts": [{"text": f"Answer the question based on this context:\n{context}\nQuestion: {query}"}]}]}
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={os.getenv('GEMINI_API_KEY')}"
    res = requests.post(url, json=payload)
    if res.status_code == 200:
        return res.json()["candidates"][0]["content"]["parts"][0]["text"]
    return "I'm sorry, I could not generate a response."
```

---

## 📈 Roadmap Backend

| Tahap       | Fitur                                   | Output                         |
| ----------- | --------------------------------------- | ------------------------------ |
| **Batch 1** | CRUD anggota & dokumen + SQLite         | API dasar siap                 |
| **Batch 2** | PDF HIPMI ekstraksi + Summarizer Gemini | Data HIPMI tersimpan di DB     |
| **Batch 3** | Chatbot retrieval berbasis HIPMI        | AI menjawab dari konteks HIPMI |

---

## 🧠 Catatan Akhir

- Backend kini mendukung ekstraksi dokumen organisasi (HIPMI PDF) dan menyimpannya dalam database.
- Chatbot otomatis menggunakan konteks HIPMI dari hasil ekstraksi.
- Tidak memerlukan halaman tambahan di FE, semua interaksi via **Chatbot dan Dashboard**.
- SQLite tetap digunakan untuk local dev, mudah migrasi ke PostgreSQL nanti.

---
