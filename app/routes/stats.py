from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.organization_service import OrganizationService

router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("/overview")
async def get_stats_overview(db: Session = Depends(get_db)):
    """
    Statistik overview dari data organisasi
    """
    orgs = OrganizationService.get_all_organizations(db)
    latest_org = OrganizationService.get_latest_organization(db)

    return {
        "status": "success",
        "stats": {
            "total_organizations": len(orgs),
            "latest_organization": (
                str(latest_org.name)
                if latest_org and latest_org.name is not None
                else None
            ),
            "last_updated": (
                latest_org.extracted_at.isoformat()
                if latest_org and latest_org.extracted_at is not None
                else None
            ),
        },
    }
