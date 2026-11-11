import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from psycopg_pool import ConnectionPool

from domain.exceptions.exceptions import DischargeNotFoundException
from application.use_cases.record_discharge_use_case import RecordDischargeUseCase
from application.use_cases.get_discharge_use_case import GetDischargeUseCase
from infrastructure.persistence.postgres_repository import PostgresDischargeRepository
from infrastructure.messaging.kafka_publisher import KafkaEventPublisher
from infrastructure.http.routes import create_discharge_router

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgrespassword@localhost:5432/gasoline_db",
)
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "")

db_pool = ConnectionPool(DATABASE_URL, min_size=1, max_size=10, open=False)
event_publisher = (
    KafkaEventPublisher(KAFKA_BOOTSTRAP_SERVERS) if KAFKA_BOOTSTRAP_SERVERS else None
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    db_pool.open()
    yield
    if event_publisher is not None:
        event_publisher.close()
    db_pool.close()


app = FastAPI(
    title="Station Service",
    description="Microservicio de Recepción y Descarga en Estación de Servicio (Arquitectura Hexagonal)",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(DischargeNotFoundException)
async def not_found_handler(request: Request, exc: DischargeNotFoundException):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"error": str(exc)},
    )


# Composición e Inyección de Dependencias
repository = PostgresDischargeRepository(db_pool)
record_use_case = RecordDischargeUseCase(repository, event_publisher=event_publisher)
get_use_case = GetDischargeUseCase(repository)

# Registrar rutas
app.include_router(create_discharge_router(record_use_case, get_use_case))


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "service": "station-service"}


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8082"))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
