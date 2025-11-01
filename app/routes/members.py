from fastapi import APIRouter, File, UploadFile, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.member import Member
from pathlib import Path
import csv
import io

router = APIRouter(prefix="/api/members", tags=["members"])


@router.post("/upload-csv")
async def upload_members_csv(
    file: UploadFile = File(...), db: Session = Depends(get_db)
):
    """
    Upload data pengurus HIPMI dari file CSV (pengurus.csv)

    Format CSV yang didukung:
    no,nama,jabatan,status_kta,no_kta,tanggal_lahir,usia,jenis_kelamin,whatsapp,email,instagram,
    nama_perusahaan,jabatan_dlm_akta_perusahaan,kategori_bidang_usaha,alamat_perusahaan,
    perusahaan_berdiri_sejak,jmlh_karyawan,website,twitter,facebook,youtube

    Detail Kolom:
    - nama: Nama lengkap pengurus (required)
    - jabatan: Jabatan dalam kepengurusan (Ketum, WKU, Sekum, Ketua Bidang, dll)
    - status_kta: Status KTA (KTA Fisik, KTA HIPMI NET, Hilang, SK Tum Ibam)
    - usia: Usia pengurus (untuk analisis distribusi usia)
    - jenis_kelamin: Gender (Male/Female)
    - whatsapp: Nomor WhatsApp
    - email: Email
    - kategori_bidang_usaha: Bidang usaha (IT, Property, F&B, Fashion, dll)
    - nama_perusahaan: Nama perusahaan
    - jmlh_karyawan: Jumlah karyawan

    Contoh CSV:
    ```csv
    no,nama,jabatan,status_kta,usia,jenis_kelamin,kategori_bidang_usaha,nama_perusahaan,jmlh_karyawan
    1,Ibrahim Imaduddin Islam,Ketum,KTA Fisik,35,Male,Industri Kreatif,PT. Mavens Studio Indonesia,
    ```
    """
    if file.filename is None or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")

    try:
        contents = await file.read()
        stream = io.StringIO(contents.decode("utf-8"))

        # Read and clean headers (trim spaces)
        reader = csv.DictReader(stream)
        # Clean the fieldnames
        reader.fieldnames = [
            field.strip() if field else field for field in reader.fieldnames
        ]

        imported_count = 0
        errors = []

        for row_num, row in enumerate(reader, 1):
            try:
                # Parse integer fields
                no = None
                if row.get("no"):
                    try:
                        no_val = row.get("no", "").strip()
                        if no_val and no_val.isdigit():
                            no = int(no_val)
                    except:
                        pass

                usia = None
                if row.get("usia"):
                    try:
                        usia_val = row.get("usia", "").strip()
                        if usia_val and usia_val.isdigit():
                            usia = int(usia_val)
                    except:
                        pass

                jmlh_karyawan = None
                if row.get("jmlh_karyawan"):
                    try:
                        jmlh_val = row.get("jmlh_karyawan", "").strip()
                        if jmlh_val and jmlh_val.isdigit():
                            jmlh_karyawan = int(jmlh_val)
                    except:
                        pass

                # Create member object with pengurus data
                member = Member(
                    no=no,
                    name=row.get("nama", "").strip(),  # nama -> name
                    jabatan=(
                        row.get("jabatan", "").strip() if row.get("jabatan") else None
                    ),
                    status_kta=(
                        row.get("status_kta", "").strip()
                        if row.get("status_kta")
                        else None
                    ),
                    no_kta=row.get("no_kta", "").strip() if row.get("no_kta") else None,
                    tanggal_lahir=(
                        row.get("tanggal_lahir", "").strip()
                        if row.get("tanggal_lahir")
                        else None
                    ),
                    usia=usia,
                    jenis_kelamin=(
                        row.get("jenis_kelamin", "").strip()
                        if row.get("jenis_kelamin")
                        else None
                    ),
                    phone=(
                        row.get("whatsapp", "").strip() if row.get("whatsapp") else None
                    ),  # whatsapp -> phone
                    email=row.get("email", "").strip() if row.get("email") else None,
                    instagram=(
                        row.get("instagram", "").strip()
                        if row.get("instagram")
                        else None
                    ),
                    nama_perusahaan=(
                        row.get("nama_perusahaan", "").strip()
                        if row.get("nama_perusahaan")
                        else None
                    ),
                    jabatan_dlm_akta_perusahaan=(
                        row.get("jabatan_dlm_akta_perusahaan", "").strip()
                        if row.get("jabatan_dlm_akta_perusahaan")
                        else None
                    ),
                    kategori_bidang_usaha=(
                        row.get("kategori_bidang_usaha", "").strip()
                        if row.get("kategori_bidang_usaha")
                        else None
                    ),
                    alamat_perusahaan=(
                        row.get("alamat_perusahaan", "").strip()
                        if row.get("alamat_perusahaan")
                        else None
                    ),
                    perusahaan_berdiri_sejak=(
                        row.get("perusahaan_berdiri_sejak", "").strip()
                        if row.get("perusahaan_berdiri_sejak")
                        else None
                    ),
                    jmlh_karyawan=jmlh_karyawan,
                    website=(
                        row.get("website", "").strip() if row.get("website") else None
                    ),
                    twitter=(
                        row.get("twitter", "").strip() if row.get("twitter") else None
                    ),
                    facebook=(
                        row.get("facebook", "").strip() if row.get("facebook") else None
                    ),
                    youtube=(
                        row.get("youtube", "").strip() if row.get("youtube") else None
                    ),
                    # Backward compatibility fields
                    position=(
                        row.get("jabatan", "").strip() if row.get("jabatan") else None
                    ),
                    organization=(
                        row.get("kategori_bidang_usaha", "").strip()
                        if row.get("kategori_bidang_usaha")
                        else None
                    ),
                )
                db.add(member)
                imported_count += 1
            except Exception as e:
                errors.append(f"Row {row_num}: {str(e)}")

        db.commit()

        return {
            "status": "success",
            "imported": imported_count,
            "errors": errors if errors else None,
            "message": f"Successfully imported {imported_count} pengurus from CSV",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


@router.get("/")
async def list_members(db: Session = Depends(get_db)):
    """
    List semua pengurus HIPMI dengan informasi lengkap
    """
    members = db.query(Member).all()

    return {
        "status": "success",
        "total": len(members),
        "data": [
            {
                "id": m.id,
                "no": m.no,
                "name": m.name,
                "email": m.email,
                "phone": m.phone,
                # Pengurus-specific fields
                "jabatan": m.jabatan,
                "status_kta": m.status_kta,
                "no_kta": m.no_kta,
                "tanggal_lahir": m.tanggal_lahir,
                "usia": m.usia,
                "jenis_kelamin": m.jenis_kelamin,
                "instagram": m.instagram,
                # Company/Business fields
                "nama_perusahaan": m.nama_perusahaan,
                "jabatan_dlm_akta_perusahaan": m.jabatan_dlm_akta_perusahaan,
                "kategori_bidang_usaha": m.kategori_bidang_usaha,
                "alamat_perusahaan": m.alamat_perusahaan,
                "perusahaan_berdiri_sejak": m.perusahaan_berdiri_sejak,
                "jmlh_karyawan": m.jmlh_karyawan,
                "website": m.website,
                "twitter": m.twitter,
                "facebook": m.facebook,
                "youtube": m.youtube,
                # Backward compatibility (optional)
                "position": m.position,
                "organization": m.organization,
                "status": m.status,
                "region": m.region,
                "entry_year": m.entry_year,
            }
            for m in members
        ],
    }
