import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from salary.api.routes.employees import router as employees_router
from salary.api.routes.insights import router as insights_router


def create_app() -> FastAPI:
    app = FastAPI(title="Salary Management API", version="0.1.0")

    # Browser CORS — frontend lives on a different origin in dev (3000)
    # and in prod (Amplify subdomain). Comma-sep env var overrides.
    cors_origins = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000",
    ).split(",")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[o.strip() for o in cors_origins if o.strip()],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(IntegrityError)
    async def _integrity_handler(_: Request, __: IntegrityError) -> JSONResponse:
        # Uniqueness, FK, and check-constraint failures all surface as
        # IntegrityError. 409 is the right shape for every one of them —
        # the client is conflicting with existing state. Specific messages
        # would require driver-specific error parsing; not worth the
        # fragility.
        return JSONResponse(
            status_code=409,
            content={"detail": "request conflicts with existing record"},
        )

    app.include_router(employees_router)
    app.include_router(insights_router)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
