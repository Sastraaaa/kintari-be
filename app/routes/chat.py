from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.services.gemini_service import GeminiService
from app.services.universal_document_service import UniversalDocumentService
from app.schemas.chat_schema import ChatQuerySchema, ChatResponseSchema
from app.models.member import Member
from app.models.universal_document import UniversalDocument
import re

router = APIRouter(prefix="/api/chat", tags=["chat"])


def detect_and_answer_specific_query(query: str, db: Session) -> dict | None:
    """
    Deteksi dan jawab pertanyaan spesifik tentang pengurus HIPMI
    Sesuai dengan query dari update3.instructions.md

    Returns: dict dengan answer jika match, None jika tidak match
    """
    query_lower = query.lower()

    # 1. Statistik Anggota per Jabatan: "Ada berapa orang 'Ketua Bidang'?"
    if "berapa" in query_lower and (
        "jabatan" in query_lower
        or "ketua" in query_lower
        or "sekum" in query_lower
        or "bendum" in query_lower
    ):
        # Try to extract jabatan name
        jabatan_pattern = r"['\"]([^'\"]+)['\"]"
        jabatan_match = re.search(jabatan_pattern, query)

        if jabatan_match:
            jabatan_name = jabatan_match.group(1)
            count = (
                db.query(Member)
                .filter(func.lower(Member.jabatan).like(f"%{jabatan_name.lower()}%"))
                .count()
            )
            return {
                "type": "specific_query",
                "answer": f"Jumlah pengurus dengan jabatan '{jabatan_name}': **{count} orang**",
                "data": {"jabatan": jabatan_name, "count": count},
            }
        elif (
            "per jabatan" in query_lower or "jumlah pengurus per jabatan" in query_lower
        ):
            # Show all jabatan counts
            result = (
                db.query(Member.jabatan, func.count(Member.id).label("count"))
                .filter(Member.jabatan.isnot(None))
                .group_by(Member.jabatan)
                .order_by(func.count(Member.id).desc())
                .all()
            )

            if result:
                answer = "**Jumlah Pengurus per Jabatan:**\n"
                for row in result:
                    answer += f"- {row.jabatan}: {row.count} orang\n"

                return {
                    "type": "specific_query",
                    "answer": answer,
                    "data": {
                        "jabatan_counts": {row.jabatan: row.count for row in result}
                    },
                }

    # 2. Statistik Bidang Usaha: "Bidang usaha apa yang paling banyak?"
    if ("bidang usaha" in query_lower or "kategori bisnis" in query_lower) and (
        "paling banyak" in query_lower or "terbanyak" in query_lower
    ):
        result = (
            db.query(Member.kategori_bidang_usaha, func.count(Member.id).label("count"))
            .filter(Member.kategori_bidang_usaha.isnot(None))
            .group_by(Member.kategori_bidang_usaha)
            .order_by(func.count(Member.id).desc())
            .first()
        )

        if result:
            return {
                "type": "specific_query",
                "answer": f"Bidang usaha terbanyak di kepengurusan: **{result.kategori_bidang_usaha}** ({result.count} pengurus)",
                "data": {
                    "bidang_usaha": result.kategori_bidang_usaha,
                    "count": result.count,
                },
            }

    # Count bidang usaha specific: "Ada berapa pengurus di bidang 'Property & Konstruksi'?"
    if "bidang" in query_lower and "berapa" in query_lower:
        bidang_pattern = r"['\"]([^'\"]+)['\"]"
        bidang_match = re.search(bidang_pattern, query)

        if bidang_match:
            bidang_name = bidang_match.group(1)
            count = (
                db.query(Member)
                .filter(
                    func.lower(Member.kategori_bidang_usaha).like(
                        f"%{bidang_name.lower()}%"
                    )
                )
                .count()
            )
            return {
                "type": "specific_query",
                "answer": f"Jumlah pengurus di bidang '{bidang_name}': **{count} orang**",
                "data": {"bidang_usaha": bidang_name, "count": count},
            }

    # 3. Statistik Status KTA: "Berapa pengurus yang KTA-nya 'Hilang'?"
    if "kta" in query_lower and ("berapa" in query_lower or "jumlah" in query_lower):
        status_pattern = r"['\"]([^'\"]+)['\"]"
        status_match = re.search(status_pattern, query)

        if status_match:
            status_name = status_match.group(1)
            count = (
                db.query(Member)
                .filter(func.lower(Member.status_kta).like(f"%{status_name.lower()}%"))
                .count()
            )
            return {
                "type": "specific_query",
                "answer": f"Jumlah pengurus dengan status KTA '{status_name}': **{count} orang**",
                "data": {"status_kta": status_name, "count": count},
            }
        elif "tampilkan status kta" in query_lower:
            # Show all KTA status
            result = (
                db.query(Member.status_kta, func.count(Member.id).label("count"))
                .filter(Member.status_kta.isnot(None))
                .group_by(Member.status_kta)
                .all()
            )

            if result:
                answer = "**Status KTA Semua Pengurus:**\n"
                for row in result:
                    answer += f"- {row.status_kta}: {row.count} orang\n"

                return {
                    "type": "specific_query",
                    "answer": answer,
                    "data": {
                        "status_kta_counts": {
                            row.status_kta: row.count for row in result
                        }
                    },
                }

    # 4. Statistik Demografi (Gender): "Berapa rasio pengurus pria dan wanita?"
    if ("rasio" in query_lower or "perbandingan" in query_lower) and (
        "pria" in query_lower or "wanita" in query_lower or "gender" in query_lower
    ):
        male_count = db.query(Member).filter(Member.jenis_kelamin == "Male").count()
        female_count = db.query(Member).filter(Member.jenis_kelamin == "Female").count()
        total = male_count + female_count

        if total > 0:
            male_pct = (male_count / total) * 100
            female_pct = (female_count / total) * 100

            return {
                "type": "specific_query",
                "answer": f"**Rasio Gender Pengurus:**\n- Pria (Male): {male_count} orang ({male_pct:.1f}%)\n- Wanita (Female): {female_count} orang ({female_pct:.1f}%)",
                "data": {
                    "male": male_count,
                    "female": female_count,
                    "total": total,
                    "male_percentage": male_pct,
                    "female_percentage": female_pct,
                },
            }

    # 5. Pencarian Detail Anggota: "Cari info lengkap 'Rangga Gumilar Subagja'"
    if "cari" in query_lower or "info lengkap" in query_lower or "siapa" in query_lower:
        # Extract name dari query
        name_match = re.search(r"['\"]([^'\"]+)['\"]", query)
        if name_match:
            name = name_match.group(1)
            member = (
                db.query(Member)
                .filter(func.lower(Member.name).like(f"%{name.lower()}%"))
                .first()
            )

            if member:
                return {
                    "type": "specific_query",
                    "answer": f"""
**Informasi Lengkap Pengurus:**
- Nama: {member.name}
- Jabatan: {member.jabatan or 'Tidak tersedia'}
- Status KTA: {member.status_kta or 'Tidak tersedia'}
- Usia: {member.usia or 'Tidak tersedia'}
- Jenis Kelamin: {member.jenis_kelamin or 'Tidak tersedia'}
- WhatsApp: {member.phone or 'Tidak tersedia'}
- Email: {member.email or 'Tidak tersedia'}
- Instagram: {member.instagram or 'Tidak tersedia'}
- Perusahaan: {member.nama_perusahaan or 'Tidak tersedia'}
- Jabatan di Perusahaan: {member.jabatan_dlm_akta_perusahaan or 'Tidak tersedia'}
- Bidang Usaha: {member.kategori_bidang_usaha or 'Tidak tersedia'}
- Jumlah Karyawan: {member.jmlh_karyawan or 'Tidak tersedia'}
""",
                    "data": {
                        "name": member.name,
                        "jabatan": member.jabatan,
                        "status_kta": member.status_kta,
                        "usia": member.usia,
                        "jenis_kelamin": member.jenis_kelamin,
                        "whatsapp": member.phone,
                        "email": member.email,
                        "instagram": member.instagram,
                        "nama_perusahaan": member.nama_perusahaan,
                        "kategori_bidang_usaha": member.kategori_bidang_usaha,
                        "jmlh_karyawan": member.jmlh_karyawan,
                    },
                }

    # 6. Pencarian Kontak Anggota: "Minta nomor WA 'Mukti Widodo'"
    if (
        "nomor" in query_lower
        or "wa" in query_lower
        or "whatsapp" in query_lower
        or "email" in query_lower
        or "kontak" in query_lower
    ):
        name_match = re.search(r"['\"]([^'\"]+)['\"]", query)
        if name_match:
            name = name_match.group(1)
            member = (
                db.query(Member)
                .filter(func.lower(Member.name).like(f"%{name.lower()}%"))
                .first()
            )

            if member:
                return {
                    "type": "specific_query",
                    "answer": f"**Kontak {member.name}:**\n- WhatsApp: {member.phone or 'Tidak tersedia'}\n- Email: {member.email or 'Tidak tersedia'}",
                    "data": {
                        "name": member.name,
                        "whatsapp": member.phone,
                        "email": member.email,
                    },
                }

    # 7. Pencarian Perusahaan Anggota: "Apa nama perusahaan 'Archy Renaldy Pratama'?"
    if "perusahaan" in query_lower and "nama" in query_lower:
        name_match = re.search(r"['\"]([^'\"]+)['\"]", query)
        if name_match:
            name = name_match.group(1)
            member = (
                db.query(Member)
                .filter(func.lower(Member.name).like(f"%{name.lower()}%"))
                .first()
            )

            if member:
                return {
                    "type": "specific_query",
                    "answer": f"**Perusahaan {member.name}:**\n- Nama Perusahaan: {member.nama_perusahaan or 'Tidak tersedia'}\n- Jabatan: {member.jabatan_dlm_akta_perusahaan or 'Tidak tersedia'}\n- Bidang Usaha: {member.kategori_bidang_usaha or 'Tidak tersedia'}",
                    "data": {
                        "name": member.name,
                        "nama_perusahaan": member.nama_perusahaan,
                        "jabatan_perusahaan": member.jabatan_dlm_akta_perusahaan,
                        "bidang_usaha": member.kategori_bidang_usaha,
                    },
                }

    # 8. Statistik Total Karyawan: "Berapa total jumlah karyawan dari semua pengurus?"
    if "total" in query_lower and "karyawan" in query_lower:
        total_karyawan = db.query(func.sum(Member.jmlh_karyawan)).scalar() or 0
        pengurus_count = (
            db.query(Member).filter(Member.jmlh_karyawan.isnot(None)).count()
        )

        return {
            "type": "specific_query",
            "answer": f"**Total Jumlah Karyawan:**\n- Total karyawan dari semua perusahaan pengurus: **{total_karyawan:,} karyawan**\n- Dari {pengurus_count} pengurus yang memiliki data karyawan",
            "data": {
                "total_karyawan": total_karyawan,
                "pengurus_with_data": pengurus_count,
            },
        }

    return None

    # 7. Pembuatan Daftar: "Siapa saja anggota di divisi X?"
    if "siapa saja" in query_lower or "daftar anggota" in query_lower:
        divisi_match = re.search(r"(?:di |divisi |bagian )([^\?]+)", query_lower)
        if divisi_match:
            divisi_name = divisi_match.group(1).strip()
            members = (
                db.query(Member)
                .filter(func.lower(Member.organization).like(f"%{divisi_name}%"))
                .limit(20)
                .all()
            )

            if members:
                member_list = "\n".join(
                    [f"- {m.name} ({m.position or 'Anggota'})" for m in members]
                )
                return {
                    "type": "specific_query",
                    "answer": f"**Daftar Anggota {divisi_name.title()}:**\n{member_list}\n\n_(Menampilkan {len(members)} anggota)_",
                    "data": {"division": divisi_name, "count": len(members)},
                }

    # 8. Analisis Gabungan: "Divisi mana yang punya anggota non active paling banyak?"
    if "non active" in query_lower or "tidak aktif" in query_lower:
        if "divisi" in query_lower and "paling banyak" in query_lower:
            result = (
                db.query(Member.organization, func.count(Member.id).label("count"))
                .filter(Member.status != "active")
                .group_by(Member.organization)
                .order_by(func.count(Member.id).desc())
                .first()
            )

            if result:
                return {
                    "type": "specific_query",
                    "answer": f"Divisi dengan anggota non-aktif terbanyak: **{result.organization}** ({result.count} anggota non-aktif)",
                    "data": {"division": result.organization, "count": result.count},
                }

    return None


@router.post("/query")
async def chat_query(request: ChatQuerySchema, db: Session = Depends(get_db)):
    """
    🤖 AI CHATBOT WITH ENHANCED QUERY DETECTION + UNIVERSAL KNOWLEDGE BASE

    The chatbot can now handle:
    1. Specific member queries (8 types) - Fast direct database queries
    2. Document-based questions - Uses uploaded HIPMI documents
    3. General analytics - Overall statistics and trends

    Specific Query Examples (Direct Answer):
    - "Berapa jumlah anggota di divisi KSWB?"
    - "Berapa persen anggota yang active?"
    - "Angkatan 2023 ada berapa orang?"
    - "Anggota paling banyak dari wilayah mana?"
    - "Cari info lengkap 'Mutia Suryatmi'"
    - "Apa email dan nomor HP 'Kariman Santosos'?"
    - "Siapa saja anggota di divisi Teknologi?"
    - "Divisi mana yang punya anggota non active paling banyak?"

    Document-based Examples (AI-powered):
    - "Kapan HIPMI didirikan?" (from sejarah.pdf)
    - "Apa visi misi HIPMI?" (from visimisi.pdf)
    - "Berapa batas usia anggota?" (from ART.pdf)
    - "Apa tugas Sekretaris Jenderal?" (from PO6.pdf)
    """
    try:
        # === STEP 1: Check for Specific Queries (Fast Path) ===
        specific_result = detect_and_answer_specific_query(request.query, db)

        if specific_result:
            return {
                "status": "success",
                "query": request.query,
                "response": specific_result["answer"],
                "source": "Direct Database Query",
                "query_type": "specific",
                "data": specific_result.get("data", {}),
            }

        # === STEP 2: Build Context for AI (General Query) ===
        context: str = request.context or ""

        if not context:
            # Get Document Context
            all_docs = UniversalDocumentService.get_all_documents(
                db=db, limit=10  # Get latest 10 documents
            )

            # Get Member Analytics
            members = db.query(Member).all()
            members_count = len(members)

            # Quick stats
            members_stats = {
                "total": members_count,
                "organizations": {},
                "positions": {},
                "regions": {},
                "status": {"active": 0, "non_active": 0},
            }

            for member in members:
                org = member.organization or "Tidak Diketahui"
                members_stats["organizations"][org] = (
                    members_stats["organizations"].get(org, 0) + 1
                )

                pos = member.position or "Tidak Diketahui"
                members_stats["positions"][pos] = (
                    members_stats["positions"].get(pos, 0) + 1
                )

                region = member.region or "Tidak Diketahui"
                members_stats["regions"][region] = (
                    members_stats["regions"].get(region, 0) + 1
                )

                if member.status == "active":
                    members_stats["status"]["active"] += 1
                else:
                    members_stats["status"]["non_active"] += 1

            # Get Document Analytics
            documents = db.query(UniversalDocument).all()
            docs_count = len(documents)

            docs_stats = {
                "total": docs_count,
                "types": {},
                "categories": {},
            }

            for doc in documents:
                dtype = doc.document_type or "Unknown"
                docs_stats["types"][dtype] = docs_stats["types"].get(dtype, 0) + 1

                cat = doc.category or "Tidak Dikategorikan"
                docs_stats["categories"][cat] = docs_stats["categories"].get(cat, 0) + 1

            # Build Combined Context
            context_parts = []

            # Add analytics context first
            analytics_context = f"""
=== DATA HIPMI ANALYTICS ===

ANGGOTA HIPMI:
- Total Anggota: {members_stats['total']}
- Status: {members_stats['status']['active']} aktif, {members_stats['status']['non_active']} non-aktif
- Distribusi Organisasi: {members_stats['organizations']}
- Distribusi Jabatan: {members_stats['positions']}
- Distribusi Wilayah: {members_stats['regions']}

DOKUMEN HIPMI:
- Total Dokumen: {docs_stats['total']}
- Tipe Dokumen: {docs_stats['types']}
- Kategori: {docs_stats['categories']}

===========================
"""
            context_parts.append(analytics_context)

            # Add document contents with classification
            sources = []
            if all_docs:
                for doc in all_docs:
                    doc_text = doc.full_text
                    if doc_text is not None:
                        # Classify document type for better context
                        doc_category = ""
                        filename_lower = doc.filename.lower()

                        if "sejarah" in filename_lower:
                            doc_category = "Sejarah HIPMI"
                        elif "visimisi" in filename_lower or "visi" in filename_lower:
                            doc_category = "Visi & Misi"
                        elif "motto" in filename_lower:
                            doc_category = "Motto HIPMI"
                        elif (
                            filename_lower == "ad.pdf"
                            or "anggaran dasar" in filename_lower
                        ):
                            doc_category = "Anggaran Dasar (AD)"
                        elif (
                            filename_lower == "art.pdf"
                            or "anggaran rumah tangga" in filename_lower
                        ):
                            doc_category = "Anggaran Rumah Tangga (ART)"
                        elif "po" in filename_lower:
                            # Extract PO number
                            po_num = re.search(r"po[_\-\s]?(\d+)", filename_lower)
                            if po_num:
                                doc_category = (
                                    f"Peraturan Organisasi (PO{po_num.group(1)})"
                                )
                            else:
                                doc_category = "Peraturan Organisasi (PO)"
                        else:
                            doc_category = doc.document_type or "Dokumen"

                        context_parts.append(
                            f"[{doc_category}: {doc.filename}]\n" f"{doc_text[:3000]}\n"
                        )
                        sources.append(f"{doc.filename} ({doc_category})")

            context = "\n\n---\n\n".join(context_parts)

            # Limit total context size
            if len(context) > 25000:
                context = context[:25000] + "\n\n[Context truncated...]"

        # === STEP 3: Call Gemini AI ===
        gemini = GeminiService()

        # Enhanced prompt with instruction
        enhanced_query = f"""
Berdasarkan data HIPMI (anggota, dokumen organisasi, dan peraturan) yang tersedia, jawab pertanyaan berikut:

Pertanyaan: {request.query}

Instruksi:
- Gunakan data analytics untuk pertanyaan tentang statistik/angka
- Gunakan isi dokumen untuk pertanyaan tentang peraturan, sejarah, visi/misi, dll
- Jika informasi tidak tersedia, katakan "Saya tidak memiliki informasi tersebut"
- Sebutkan sumber data jika memungkinkan (nama file/dokumen)
- Jawab dalam Bahasa Indonesia yang profesional
- Untuk pertanyaan tentang PO (Peraturan Organisasi), sebutkan nomor PO-nya
"""

        response = gemini.answer_question(enhanced_query, context)

        return {
            "status": "success",
            "query": request.query,
            "response": response,
            "source": "HIPMI Knowledge Base + AI Analytics",
            "query_type": "general",
            "members_count": members_count if "members_count" in locals() else 0,
            "documents_count": docs_count if "docs_count" in locals() else 0,
            "context_size": len(context),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


@router.get("/context")
async def get_chat_context(db: Session = Depends(get_db)):
    """
    📚 GET CHAT CONTEXT

    Get current context from universal knowledge base
    Returns preview of all documents used by chatbot
    """
    # Get all documents from universal knowledge base
    all_docs = UniversalDocumentService.get_all_documents(db=db, limit=10)

    if not all_docs:
        raise HTTPException(
            status_code=404,
            detail="No documents in knowledge base. Please upload documents first.",
        )

    # Build context preview
    context_parts = []
    for doc in all_docs:
        doc_text = doc.full_text
        if doc_text is not None:
            preview = (
                str(doc_text)[:500] + "..."
                if len(str(doc_text)) > 500
                else str(doc_text)
            )
            context_parts.append(
                {
                    "filename": doc.filename,
                    "document_type": doc.document_type,
                    "preview": preview,
                    "uploaded_at": doc.uploaded_at.isoformat() if doc.uploaded_at is not None else None,  # type: ignore
                }
            )

    return {
        "status": "success",
        "total_documents": len(all_docs),
        "documents": context_parts,
        "source": "Universal Knowledge Base",
    }
