from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.member import Member
from app.models.universal_document import UniversalDocument
from app.services.gemini_service import GeminiService
from datetime import datetime

router = APIRouter(prefix="/api", tags=["analytics"])


@router.get("/analytics/members")
async def analyze_members(db: Session = Depends(get_db)):
    """
    Analisis data anggota HIPMI dengan AI Gemini

    Returns:
        - summary: Ringkasan kondisi keanggotaan
        - total_members: Jumlah total anggota
        - key_insights: List insight penting
        - trends: Analisis tren pertumbuhan
        - recommendations: Rekomendasi untuk pengembangan
        - statistics: Data statistik mentah
    """
    try:
        # Get all members from database
        members = db.query(Member).all()

        if not members:
            return {
                "status": "success",
                "message": "Belum ada data anggota untuk dianalisis",
                "data": {
                    "summary": "Belum ada data anggota HIPMI yang tersimpan di sistem",
                    "total_members": 0,
                    "key_insights": [],
                    "trends": "Tidak ada data untuk analisis tren",
                    "recommendations": [
                        "Upload data anggota untuk mendapatkan analisis"
                    ],
                },
            }

        # Convert to dict for processing
        members_data = []
        jabatan_count = {}  # Untuk statistik per jabatan
        bidang_usaha_count = {}  # Untuk chart per bidang usaha
        status_kta_count = {}  # Untuk statistik status KTA
        gender_count = {"Male": 0, "Female": 0}  # Untuk pie chart gender
        age_distribution = {}  # Untuk histogram usia
        company_ownership_count = {
            "Memiliki Perusahaan": 0,
            "Tidak Memiliki Perusahaan": 0,
        }  # Untuk pie chart
        total_karyawan = 0  # Total karyawan dari semua pengurus

        for member in members:
            member_dict = {
                "name": member.name,
                "email": member.email,
                "jabatan": member.jabatan,
                "status_kta": member.status_kta,
                "usia": member.usia,
                "jenis_kelamin": member.jenis_kelamin,
                "kategori_bidang_usaha": member.kategori_bidang_usaha,
                "nama_perusahaan": member.nama_perusahaan,
                "jmlh_karyawan": member.jmlh_karyawan,
            }
            members_data.append(member_dict)

            # Count by jabatan
            jabatan = member.jabatan or "Tidak Diketahui"
            jabatan_count[jabatan] = jabatan_count.get(jabatan, 0) + 1

            # Count by kategori bidang usaha (untuk Bar Chart)
            bidang = member.kategori_bidang_usaha or "Tidak Diketahui"
            bidang_usaha_count[bidang] = bidang_usaha_count.get(bidang, 0) + 1

            # Count by status KTA
            status = member.status_kta or "Tidak Diketahui"
            status_kta_count[status] = status_kta_count.get(status, 0) + 1

            # Count by gender (untuk Pie Chart)
            if member.jenis_kelamin and member.jenis_kelamin.strip():
                gender = member.jenis_kelamin.strip()
                if gender == "Male":
                    gender_count["Male"] += 1
                elif gender == "Female":
                    gender_count["Female"] += 1

            # Count by age distribution (untuk Histogram)
            # Buat rentang usia: 20-25, 25-30, 30-35, 35-40, 40-45, 45+
            if member.usia and member.usia > 0:
                if member.usia < 25:
                    age_range = "20-25"
                elif member.usia < 30:
                    age_range = "25-30"
                elif member.usia < 35:
                    age_range = "30-35"
                elif member.usia < 40:
                    age_range = "35-40"
                elif member.usia < 45:
                    age_range = "40-45"
                else:
                    age_range = "45+"
                age_distribution[age_range] = age_distribution.get(age_range, 0) + 1

            # Count company ownership (untuk Pie Chart)
            if member.nama_perusahaan and member.nama_perusahaan.strip():
                company_ownership_count["Memiliki Perusahaan"] += 1
            else:
                company_ownership_count["Tidak Memiliki Perusahaan"] += 1

            # Sum total karyawan
            if member.jmlh_karyawan:
                total_karyawan += member.jmlh_karyawan

        # Call Gemini AI for analysis
        gemini = GeminiService()
        ai_analysis = gemini.analyze_members_data(members_data)

        # Combine with statistics
        result = {
            **ai_analysis,
            "statistics": {
                "total_pengurus": len(members),
                "by_jabatan": jabatan_count,
                "by_bidang_usaha": bidang_usaha_count,
                "by_status_kta": status_kta_count,
                "total_karyawan": total_karyawan,
            },
            # Data untuk 4 visualisasi utama (sesuai update3.instructions.md)
            "visualizations": {
                # 1. Distribusi Usia Pengurus (Histogram) - by usia
                "age_distribution": dict(
                    sorted(age_distribution.items(), key=lambda x: x[0])
                ),
                # 2. Proporsi Gender Pengurus (Pie Chart) - by jenis_kelamin
                "gender_proportion": gender_count,
                # 3. Jumlah Pengurus per Bidang Usaha (Bar Chart) - by kategori_bidang_usaha
                "by_business_category": dict(
                    sorted(bidang_usaha_count.items(), key=lambda x: x[1], reverse=True)
                ),
                # 4. Status Kepemilikan Perusahaan Pengurus (Pie Chart) - based on nama_perusahaan
                "company_ownership": company_ownership_count,
            },
            "last_updated": datetime.now().isoformat(),
        }

        return {"status": "success", "data": result}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to analyze members: {str(e)}"
        )


@router.get("/analytics/documents")
async def analyze_documents(db: Session = Depends(get_db)):
    """
    Analisis data dokumen HIPMI dengan AI Gemini

    Returns:
        - summary: Ringkasan kondisi dokumentasi
        - total_documents: Jumlah total dokumen
        - total_pages: Total halaman semua dokumen
        - key_insights: List insight penting
        - document_health: Status kelengkapan dokumentasi
        - recommendations: Rekomendasi untuk perbaikan
        - statistics: Data statistik mentah
    """
    try:
        # Get all documents from database
        documents = db.query(UniversalDocument).all()

        if not documents:
            return {
                "status": "success",
                "message": "Belum ada dokumen untuk dianalisis",
                "data": {
                    "summary": "Belum ada dokumen HIPMI yang tersimpan di sistem",
                    "total_documents": 0,
                    "total_pages": 0,
                    "key_insights": [],
                    "document_health": "Belum ada data",
                    "recommendations": [
                        "Upload dokumen HIPMI untuk mendapatkan analisis"
                    ],
                },
            }

        # Convert to dict for processing
        documents_data = []
        doc_types_count = {}
        categories_count = {}
        total_pages = 0
        total_size = 0

        for doc in documents:
            doc_dict = {
                "filename": doc.filename,
                "document_type": doc.document_type,
                "category": doc.category,
                "page_count": doc.page_count,
                "file_size_mb": doc.file_size_mb,
            }
            documents_data.append(doc_dict)

            # Count statistics
            dtype = doc.document_type or "Unknown"
            doc_types_count[dtype] = doc_types_count.get(dtype, 0) + 1

            cat = doc.category or "Tidak Dikategorikan"
            categories_count[cat] = categories_count.get(cat, 0) + 1

            if doc.page_count:
                total_pages += doc.page_count

            if doc.file_size_mb:
                total_size += doc.file_size_mb

        # Call Gemini AI for analysis
        gemini = GeminiService()
        ai_analysis = gemini.analyze_documents_data(documents_data)

        # Combine with statistics
        result = {
            **ai_analysis,
            "statistics": {
                "total_documents": len(documents),
                "total_pages": total_pages,
                "total_size_mb": round(total_size, 2),
                "by_type": doc_types_count,
                "by_category": categories_count,
                "avg_pages_per_doc": (
                    round(total_pages / len(documents), 1) if documents else 0
                ),
                "avg_size_mb": (
                    round(total_size / len(documents), 2) if documents else 0
                ),
            },
            "last_updated": datetime.now().isoformat(),
        }

        return {"status": "success", "data": result}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to analyze documents: {str(e)}"
        )


@router.get("/analytics/overview")
async def get_overview_analytics(db: Session = Depends(get_db)):
    """
    Get combined analytics overview untuk dashboard Statistics

    Returns insight gabungan dari data anggota dan dokumen
    """
    try:
        # Get both analytics
        members_count = db.query(Member).count()
        documents_count = db.query(UniversalDocument).count()

        # Prepare overview data
        overview = {
            "total_members": members_count,
            "total_documents": documents_count,
            "has_data": members_count > 0 or documents_count > 0,
        }

        # If there's data, generate AI insights
        if overview["has_data"]:
            gemini = GeminiService()

            prompt = f"""Sebagai AI analyst untuk HIPMI, berikan ringkasan singkat kondisi organisasi:

Total Anggota: {members_count}
Total Dokumen: {documents_count}

Berikan 3 poin insight singkat dalam format JSON:
{{
    "health_status": "Excellent/Good/Fair/Needs Improvement",
    "key_points": [
        "Poin 1",
        "Poin 2", 
        "Poin 3"
    ],
    "next_actions": "Rekomendasi prioritas"
}}"""

            try:
                response = gemini._call_api(prompt)
                import json

                ai_overview = json.loads(response)
                overview.update(ai_overview)
            except:
                overview["message"] = (
                    "AI analysis tidak tersedia, menampilkan data statistik"
                )

        return {"status": "success", "data": overview}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get overview: {str(e)}")
