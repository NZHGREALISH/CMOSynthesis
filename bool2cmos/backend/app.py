from __future__ import annotations

from typing import Any, Dict

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .api.synthesize import SynthesisError, synthesize


class SynthesizeRequest(BaseModel):
    expr: str


def create_app() -> FastAPI:
    app = FastAPI(title="bool2cmos", version="0.1.0")

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

    @app.get("/health")
    def health() -> Dict[str, str]:
        return {"status": "ok"}

    @app.post("/synthesize")
    def synthesize_route(payload: SynthesizeRequest) -> Dict[str, Any]:
        try:
            return synthesize(payload.expr)
        except SynthesisError as e:
            raise HTTPException(status_code=400, detail=str(e))

    return app


app = create_app()
