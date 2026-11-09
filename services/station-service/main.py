import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from psycopg_pool import ConnectionPool

from domain.exceptions.exceptions import DischargeNotFoundException
from application.use_cases.record_discharge_use_case import RecordDischargeUseCase
from application.use_cases.get_discharge_use_case import GetDischargeUseCase
from infrastructure.persistence.postgres_repository import PostgresDischargeRepository
from infrastructure.http.routes import create_discharge_router

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
    title="Station Service",
    description="Microservicio de Recepción y Descarga en Estación de Servicio (Arquitectura Hexagonal)",
    version="1.0.0",
    lifespan=lifespan,
)

@app.exception_handler(DischargeNotFoundException)
async def not_found_handler(request: Request, exc: DischargeNotFoundException):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"error": str(exc)},
    )

# Composición e Inyección de Dependencias
repository = PostgresDischargeRepository(db_pool)
record_use_case = RecordDischargeUseCase(repository)
get_use_case = GetDischargeUseCase(repository)

# Registrar rutas
app.include_router(create_discharge_router(record_use_case, get_use_case))

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "service": "station-service"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8082")) # Puerto 8082
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
