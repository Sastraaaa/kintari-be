from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.gemini_service import GeminiService
from app.services.organization_service import OrganizationService
from app.schemas.chat_schema import ChatQuerySchema, ChatResponseSchema

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("/query")
async def chat_query(request: ChatQuerySchema, db: Session = Depends(get_db)):
    """
    Chat retrieval endpoint berbasis konteks HIPMI
    """
    try:
        # Jika tidak ada context, ambil dari data organisasi terbaru
        context = request.context
        if not context:
            org = OrganizationService.get_latest_organization(db)
            if org and org.full_text:
                context = org.full_text[:3000]  # Limit context size
            else:
                raise HTTPException(
                    status_code=404, detail="No organization context available"
                )

        # Call Gemini untuk jawab pertanyaan
        gemini = GeminiService()
        response = gemini.answer_question(request.query, context)

        return {
            "status": "success",
            "query": request.query,
            "response": response,
            "source": "HIPMI Organization Data",
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


@router.get("/context")
async def get_chat_context(db: Session = Depends(get_db)):
    """
    Ambil konteks terbaru untuk chatbot
    """
    org = OrganizationService.get_latest_organization(db)

    if not org:
        raise HTTPException(status_code=404, detail="No context available")

    return {
        "status": "success",
        "context": (
            org.full_text[:2000] + "..."
            if org.full_text and len(org.full_text) > 2000
            else org.full_text
        ),
        "source": org.name,
        "extracted_at": org.extracted_at.isoformat() if org.extracted_at else None,
    }
