from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from salary.api.routes.employees import router as employees_router
from salary.api.routes.insights import router as insights_router


def create_app() -> FastAPI:
    app = FastAPI(title="Salary Management API", version="0.1.0")

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
