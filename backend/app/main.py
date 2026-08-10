from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import ALLOWED_ORIGINS
from .firebase_manager import FirebaseError
from .routers import auth, overview, results, students

app = FastAPI(
    title="Smart Result Analysis System API",
    description="Backend for the Smart Result Analysis System (React frontend).",
    version="1.0.0",
)


@app.exception_handler(FirebaseError)
async def firebase_error_handler(request: Request, exc: FirebaseError):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(results.router, prefix="/api")
app.include_router(students.router, prefix="/api")
app.include_router(overview.router, prefix="/api")


@app.get("/")
def root():
    return {
        "service": "Smart Result Analysis System API",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
def health():
    return {"status": "ok"}
