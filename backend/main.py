from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routes.auth import router as auth_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],#["http://localhost:3000"],  # adjust
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)

@app.get("/health")
def health():
    return {"ok": True}
