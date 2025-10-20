from app.services.pdf_extractor import PDFExtractor
from app.models.organization import OrganizationInfo, Document
from app.schemas.organization_schema import OrganizationInfoSchema
from sqlalchemy.orm import Session
from datetime import datetime


class OrganizationService:
    """Service untuk mengelola data organisasi"""

    @staticmethod
    def save_extracted_organization(
        db: Session,
        file_path: str,
        filename: str,
        extracted_data: dict,
        document_type: str = "HIPMI_PO",
    ) -> OrganizationInfo:
        """Simpan data organisasi yang sudah diekstrak"""

        org_data = OrganizationInfo(
            name=extracted_data.get("organization_name", "Unknown"),
            founded_date=extracted_data.get("founded_date"),
            ideology=extracted_data.get("ideology"),
            legal_basis=extracted_data.get("legal_basis"),
            objectives=extracted_data.get("objectives"),
            summary=extracted_data.get("full_text", "")[:1000],
            full_text=extracted_data.get("full_text"),
            extracted_at=datetime.utcnow(),
        )

        db.add(org_data)
        db.commit()
        db.refresh(org_data)

        # Simpan juga record document
        file_size = 0
        try:
            import os

            file_size = os.path.getsize(file_path)
        except:
            pass

        document = Document(
            filename=filename,
            file_path=file_path,
            document_type=document_type,
            organization_id=org_data.id,
            file_size=file_size,
            extracted_text=extracted_data.get("full_text"),
            processed=2,  # 2 = completed
            processed_at=datetime.utcnow(),
        )

        db.add(document)
        db.commit()

        return org_data

    @staticmethod
    def get_organization_by_id(db: Session, org_id: int) -> OrganizationInfo:
        """Ambil data organisasi berdasarkan ID"""
        return db.query(OrganizationInfo).filter(OrganizationInfo.id == org_id).first()

    @staticmethod
    def get_latest_organization(db: Session) -> OrganizationInfo:
        """Ambil data organisasi terbaru"""
        return (
            db.query(OrganizationInfo)
            .order_by(OrganizationInfo.extracted_at.desc())
            .first()
        )

    @staticmethod
    def get_all_organizations(db: Session):
        """Ambil semua data organisasi"""
        return (
            db.query(OrganizationInfo)
            .order_by(OrganizationInfo.extracted_at.desc())
            .all()
        )
