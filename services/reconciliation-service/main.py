import os
import logging
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from psycopg_pool import ConnectionPool

load_dotenv()
logging.basicConfig(level=logging.INFO)

from domain.exceptions.exceptions import ReconciliationNotFoundException
from application.use_cases.reconcile_trip_use_case import ReconcileTripUseCase
from application.use_cases.get_reconciliation_use_case import GetReconciliationUseCase
from application.use_cases.list_reconciliations_use_case import ListReconciliationsUseCase
from application.use_cases.submit_human_review_use_case import SubmitHumanReviewUseCase
from infrastructure.persistence.postgres_repository import PostgresReconciliationRepository
from infrastructure.adapters.llm_adapters.bedrock_adapter import BedrockAIAnalystAdapter
from infrastructure.messaging.kafka_consumer import DischargeEventConsumer
from infrastructure.http.routes import create_reconciliation_router

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgrespassword@localhost:5432/gasoline_db",
)
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "")

db_pool = ConnectionPool(DATABASE_URL, min_size=1, max_size=10, open=False)
repository = PostgresReconciliationRepository(db_pool)
ai_analyst = BedrockAIAnalystAdapter()
reconcile_use_case = ReconcileTripUseCase(repository, ai_analyst)
get_use_case = GetReconciliationUseCase(repository)
list_use_case = ListReconciliationsUseCase(repository)
review_use_case = SubmitHumanReviewUseCase(repository)

kafka_consumer = (
    DischargeEventConsumer(KAFKA_BOOTSTRAP_SERVERS, reconcile_use_case, repository)
    if KAFKA_BOOTSTRAP_SERVERS
    else None
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    db_pool.open()
    repository.ensure_schema()
    if kafka_consumer is not None:
        kafka_consumer.start()
    yield
    if kafka_consumer is not None:
        kafka_consumer.stop()
    db_pool.close()


app = FastAPI(
    title="Reconciliation Service",
    description="Microservicio de Reconciliación y Auditoría (Hexagonal + IA Bedrock + HITL)",
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


@app.exception_handler(ReconciliationNotFoundException)
async def not_found_handler(request: Request, exc: ReconciliationNotFoundException):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"error": str(exc)},
    )


app.include_router(
    create_reconciliation_router(
        reconcile_use_case,
        get_use_case,
        list_use_case,
        review_use_case,
    )
)


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "service": "reconciliation-service"}


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8083"))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
