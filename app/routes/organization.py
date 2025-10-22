from fastapi import APIRouter, File, UploadFile, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.pdf_extractor import PDFExtractor
from app.services.gemini_service import GeminiService
from app.services.organization_service import OrganizationService
from app.schemas.organization_schema import OrganizationInfoSchema
from pathlib import Path
import os

router = APIRouter(prefix="/api/organization", tags=["organization"])


@router.post("/upload")
async def upload_organization_document(
    file: UploadFile = File(...), db: Session = Depends(get_db)
):
    """
    Upload dan ekstrak dokumen organisasi (HIPMI PDF)
    """
    if file.filename is None or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    try:
        # Simpan file ke directory uploads
        upload_dir = Path("./uploads")
        upload_dir.mkdir(exist_ok=True)

        file_path = upload_dir / file.filename

        # Tulis file
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)

        # Ekstrak data dari PDF
        extracted_data = PDFExtractor.extract_hipmi_data(str(file_path))

        # Simpan ke database
        org = OrganizationService.save_extracted_organization(
            db=db,
            file_path=str(file_path),
            filename=file.filename,
            extracted_data=extracted_data,
            document_type="HIPMI_PO",
        )

        return {
            "status": "success",
            "message": "Document uploaded and processed successfully",
            "organization_id": org.id,
            "data": {
                "name": str(org.name) if org.name is not None else "Unknown",
                "founded_date": (
                    str(org.founded_date) if org.founded_date is not None else "Unknown"
                ),
                "ideology": (
                    str(org.ideology) if org.ideology is not None else "Unknown"
                ),
            },
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


@router.get("/data/{org_id}")
async def get_organization_data(org_id: int, db: Session = Depends(get_db)):
    """
    Ambil data organisasi yang sudah diekstrak
    """
    org = OrganizationService.get_organization_by_id(db, org_id)

    if org is None:
        raise HTTPException(status_code=404, detail="Organization not found")

    return {
        "status": "success",
        "data": {
            "id": org.id,
            "name": str(org.name) if org.name is not None else "Unknown",
            "founded_date": (
                str(org.founded_date) if org.founded_date is not None else "Unknown"
            ),
            "ideology": str(org.ideology) if org.ideology is not None else "Unknown",
            "legal_basis": (
                str(org.legal_basis) if org.legal_basis is not None else "Unknown"
            ),
            "objectives": (
                str(org.objectives) if org.objectives is not None else "Unknown"
            ),
            "summary": str(org.summary) if org.summary is not None else "",
            "extracted_at": (
                org.extracted_at.isoformat() if org.extracted_at is not None else None
            ),
        },
    }


@router.get("/latest")
async def get_latest_organization(db: Session = Depends(get_db)):
    """
    Ambil data organisasi terbaru yang sudah diekstrak
    """
    org = OrganizationService.get_latest_organization(db)

    if org is None:
        raise HTTPException(status_code=404, detail="No organization data found")

    return {
        "status": "success",
        "data": {
            "id": org.id,
            "name": str(org.name) if org.name is not None else "Unknown",
            "founded_date": (
                str(org.founded_date) if org.founded_date is not None else "Unknown"
            ),
            "ideology": str(org.ideology) if org.ideology is not None else "Unknown",
            "legal_basis": (
                str(org.legal_basis) if org.legal_basis is not None else "Unknown"
            ),
            "objectives": (
                str(org.objectives) if org.objectives is not None else "Unknown"
            ),
            "summary": str(org.summary) if org.summary is not None else "",
            "extracted_at": (
                org.extracted_at.isoformat() if org.extracted_at is not None else None
            ),
        },
    }


@router.get("/all")
async def get_all_organizations(db: Session = Depends(get_db)):
    """
    Ambil semua data organisasi
    """
    orgs = OrganizationService.get_all_organizations(db)

    return {
        "status": "success",
        "total": len(orgs),
        "data": [
            {
                "id": org.id,
                "name": str(org.name) if org.name is not None else "Unknown",
                "founded_date": (
                    str(org.founded_date) if org.founded_date is not None else "Unknown"
                ),
                "ideology": (
                    str(org.ideology) if org.ideology is not None else "Unknown"
                ),
                "extracted_at": (
                    org.extracted_at.isoformat()
                    if org.extracted_at is not None
                    else None
                ),
            }
            for org in orgs
        ],
    }


@router.post("/summarize")
async def summarize_organization_context(org_id: int, db: Session = Depends(get_db)):
    """
    Buat ringkasan dari konteks organisasi menggunakan Gemini API
    """
    org = OrganizationService.get_organization_by_id(db, org_id)

    if org is None:
        raise HTTPException(status_code=404, detail="Organization not found")

    gemini = GeminiService()
    full_text = str(org.full_text) if org.full_text is not None else ""
    summary = gemini.summarize_text(full_text)

    return {"status": "success", "organization_id": org_id, "summary": summary}
