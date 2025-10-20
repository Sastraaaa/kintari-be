from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import ALLOWED_ORIGINS
from app.core.database import Base, engine
from app.routes import members, documents, chat, stats, organization

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Kintari Backend API",
    description="Backend API untuk Kintari dengan ekstraksi dokumen HIPMI dan Gemini AI Integration",
    version="1.0.0",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Dapat diganti dengan ALLOWED_ORIGINS untuk production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(members.router)
app.include_router(documents.router)
app.include_router(stats.router)
app.include_router(chat.router)
app.include_router(organization.router)


@app.get("/")
async def root():
    return {
        "message": "Welcome to Kintari Backend API",
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
