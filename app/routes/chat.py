from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.gemini_service import GeminiService
from app.services.universal_document_service import UniversalDocumentService
from app.schemas.chat_schema import ChatQuerySchema, ChatResponseSchema

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("/query")
async def chat_query(request: ChatQuerySchema, db: Session = Depends(get_db)):
    """
    🤖 AI CHATBOT WITH UNIVERSAL KNOWLEDGE BASE

    The chatbot now uses ALL uploaded documents as context!
    It will search through:
    - HIPMI documents (PO, AD, ART, SK)
    - Contracts, reports, proposals
    - Presentations, manuals
    - ANY document you've uploaded

    The more documents you upload, the smarter the chatbot becomes!
    """
    try:
        # Build context from universal knowledge base
        context: str = request.context or ""

        if not context:
            # Get all processed documents from universal knowledge base
            all_docs = UniversalDocumentService.get_all_documents(
                db=db, limit=10  # Get latest 10 documents
            )

            if not all_docs:
                raise HTTPException(
                    status_code=404,
                    detail="No documents in knowledge base. Please upload documents first.",
                )

            # Combine context from multiple documents
            context_parts = []
            sources = []

            for doc in all_docs:
                doc_text = doc.full_text
                if doc_text is not None:
                    # Add document info to context
                    context_parts.append(
                        f"[Document: {doc.filename} | Type: {doc.document_type}]\n"
                        f"{doc_text[:2000]}\n"
                    )
                    sources.append(doc.filename)

            context = "\n\n---\n\n".join(context_parts)

            # Limit total context size
            if len(context) > 15000:
                context = context[:15000] + "\n\n[Context truncated...]"

        # Call Gemini AI
        gemini = GeminiService()

        # Enhanced prompt with instruction
        enhanced_query = f"""
Based on the provided documents in the knowledge base, please answer the following question:

Question: {request.query}

Instructions:
- Use information from ALL provided documents
- If answer is not in documents, say "I don't have that information in the knowledge base"
- Cite which document(s) you're referencing when possible
- Be specific and accurate
"""

        response = gemini.answer_question(enhanced_query, context)

        return {
            "status": "success",
            "query": request.query,
            "response": response,
            "source": "Universal Knowledge Base",
            "documents_used": len(all_docs) if "all_docs" in locals() else 1,
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
