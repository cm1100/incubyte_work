from fastapi import FastAPI

from salary.api.routes.employees import router as employees_router


def create_app() -> FastAPI:
    app = FastAPI(title="Salary Management API", version="0.1.0")
    app.include_router(employees_router)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
