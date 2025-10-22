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
    Upload data anggota dari file CSV
    """
    if file.filename is None or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")

    try:
        contents = await file.read()
        stream = io.StringIO(contents.decode("utf-8"))
        reader = csv.DictReader(stream)

        imported_count = 0
        errors = []

        for row_num, row in enumerate(reader, 1):
            try:
                member = Member(
                    name=row.get("name", ""),
                    email=row.get("email", ""),
                    phone=row.get("phone"),
                    position=row.get("position"),
                    organization=row.get("organization"),
                    membership_type=row.get("membership_type"),
                    status=row.get("status", "active"),
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
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


@router.get("/")
async def list_members(db: Session = Depends(get_db)):
    """
    List semua anggota
    """
    members = db.query(Member).all()

    return {
        "status": "success",
        "total": len(members),
        "data": [
            {
                "id": m.id,
                "name": m.name,
                "email": m.email,
                "phone": m.phone,
                "position": m.position,
                "organization": m.organization,
                "status": m.status,
            }
            for m in members
        ],
    }
