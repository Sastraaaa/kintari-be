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
        context: str = request.context or ""
        if not context:
            org = OrganizationService.get_latest_organization(db)
            if org is not None and org.full_text is not None:
                context = str(org.full_text)[:3000]  # Limit context size
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

    if org is None:
        raise HTTPException(status_code=404, detail="No context available")

    # Extract values safely
    full_text = str(org.full_text) if org.full_text is not None else ""
    context_preview = full_text[:2000] + "..." if len(full_text) > 2000 else full_text

    return {
        "status": "success",
        "context": context_preview,
        "source": str(org.name) if org.name is not None else "Unknown",
        "extracted_at": (
            org.extracted_at.isoformat() if org.extracted_at is not None else None
        ),
    }
