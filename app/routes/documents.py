from fastapi import APIRouter, File, UploadFile, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.organization import Document
from pathlib import Path

router = APIRouter(prefix="/api/documents", tags=["documents"])


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...), doc_type: str = "OTHER", db: Session = Depends(get_db)
):
    """
    Upload dokumen organisasi
    """
    try:
        upload_dir = Path("./uploads")
        upload_dir.mkdir(exist_ok=True)

        file_path = upload_dir / file.filename

        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)

        doc = Document(
            filename=file.filename,
            file_path=str(file_path),
            document_type=doc_type,
            file_size=len(contents),
            processed=0,
        )

        db.add(doc)
        db.commit()
        db.refresh(doc)

        return {
            "status": "success",
            "document_id": doc.id,
            "filename": doc.filename,
            "file_size": doc.file_size,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")


@router.get("/")
async def list_documents(db: Session = Depends(get_db)):
    """
    List semua dokumen
    """
    docs = db.query(Document).all()

    return {
        "status": "success",
        "total": len(docs),
        "data": [
            {
                "id": d.id,
                "filename": d.filename,
                "document_type": d.document_type,
                "file_size": d.file_size,
                "processed": d.processed,
                "upload_date": d.upload_date.isoformat() if d.upload_date else None,
            }
            for d in docs
        ],
    }
