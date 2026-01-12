from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from bool2cmos.backend.api.synthesize import router as synthesize_router

app = FastAPI(title="bool2cmos")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if synthesize_router is not None:
    app.include_router(synthesize_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
