import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from psycopg_pool import ConnectionPool

from domain.exceptions.exceptions import DispatchNotFoundException
from application.use_cases.create_dispatch_use_case import CreateDispatchUseCase
from application.use_cases.get_dispatch_use_case import GetDispatchUseCase
from infrastructure.persistence.postgres_repository import PostgresDispatchRepository
from infrastructure.http.routes import create_dispatch_router

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgrespassword@localhost:5432/gasoline_db"
)

db_pool = ConnectionPool(DATABASE_URL, min_size=1, max_size=10, open=False)

@asynccontextmanager
async def lifespan(app: FastAPI):
    db_pool.open()
    yield
    db_pool.close()

app = FastAPI(
    title="Dispatch Service",
    description="Microservicio de Despacho (Clean / Hexagonal Architecture con CQRS Commands)",
    version="1.0.0",
    lifespan=lifespan,
)

@app.exception_handler(DispatchNotFoundException)
async def not_found_handler(request: Request, exc: DispatchNotFoundException):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"error": str(exc)},
    )

repository = PostgresDispatchRepository(db_pool)
create_use_case = CreateDispatchUseCase(repository)
get_use_case = GetDispatchUseCase(repository)

app.include_router(create_dispatch_router(create_use_case, get_use_case))

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "service": "dispatch-service"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8080"))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
