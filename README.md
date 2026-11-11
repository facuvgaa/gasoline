# ⛽ Gasoline — Event-Driven Fuel Logistics & Fraud Detection

[🇪🇸 Español](#español) • [🇺🇸 English](#english)

---

<a name="español"></a>
## 🇪🇸 Español

Plataforma de microservicios **Event-Driven** con **Arquitectura Hexagonal (Ports & Adapters)**, **CQRS**, **IA Generativa (AWS Bedrock Mantle)** y flujo **Human-in-the-Loop (HITL)** para auditar despachos de combustible, detectar anomalías en ruta (apertura de válvulas / ordeñe) y diferenciar mermas físicas de variaciones térmicas.

### Arquitectura & Flujo de Eventos

```text
[1. Refinería]       [2. En Ruta IoT]       [3. Estación]
dispatch-service     telemetry-service     station-service
 (Python :8080)         (Go :8081)         (Python :8082)
       │                     │                    │
       └─────────────────────┼────────────────────┘
                             │                    ▼
                             │         [ Redpanda / Kafka :19092 ]
                             │           tópico: station.discharges
                             │                    │
                             ▼                    ▼
                     reconciliation-service (Python :8083)
                             │
              ┌──────────────┴──────────────┐
              ▼                             ▼
      AWS Bedrock Mantle           PostgreSQL 16 (:5432)
   (Peritaje Forense IA)                    │
                                            ▼
                                  hitl-dashboard (:3000)
                                 (React + Vite + Tailwind)
```

### Servicios del Sistema

| Servicio | Stack | Puerto | Responsabilidad |
|---|---|---|---|
| **dispatch-service** | Python / FastAPI | `8080` | Registro y consulta de órdenes de carga en refinería |
| **telemetry-service** | Go / `net/http` | `8081` | Ingesta concurrente de GPS y alertas de válvula abierta en movimiento |
| **station-service** | Python / FastAPI | `8082` | Registro de descargas en tanques + publicación de evento `DischargeRecorded` |
| **reconciliation-service** | Python / FastAPI | `8083` | Consumer de Redpanda + cálculo de varianza + análisis con **AWS Bedrock Mantle** + API HITL |
| **hitl-dashboard** | React / TypeScript / Vite | `3000` | Consola SOC en vivo (auto-refresh) para revisión y veredicto humano |
| **redpanda** | Kafka-compatible Broker | `19092` | Bus de eventos asíncrono |
| **postgres** | PostgreSQL 16 | `5432` | Base de datos relacional (`scripts/init.sql`) |

### Cómo ejecutar todo con Docker Compose

```bash
# 1. Crear archivo .env en la raíz con tu token de AWS Bedrock Mantle (opcional, degrada limpio si falta)
cp services/reconciliation-service/.env.example .env

# 2. Construir y levantar toda la arquitectura (7 contenedores)
docker compose up -d --build
```

* **Dashboard HITL (UI):** http://localhost:3000
* **Swagger APIs:** http://localhost:8080/docs • http://localhost:8082/docs • http://localhost:8083/docs

### Tests y CI/CD

El pipeline [`.github/workflows/ci.yml`](.github/workflows/ci.yml) corre en paralelo los tests unitarios de los 4 microservicios + build de React/TypeScript y, si todo pasa en verde, reconstruye todas las imágenes Docker.

```bash
# Tests locales
cd services/dispatch-service && pytest -v
cd services/station-service && pytest -v
cd services/reconciliation-service && pytest -v
cd services/telemetry-service && go test -v -race ./...
cd frontend && npm run build
```

---

<a name="english"></a>
## 🇺🇸 English

**Event-Driven** microservices platform built with **Hexagonal Architecture (Ports & Adapters)**, **CQRS**, **Generative AI (AWS Bedrock Mantle)**, and a **Human-in-the-Loop (HITL)** workflow to audit fuel dispatches, detect in-transit valve tampering/theft, and distinguish real physical losses from thermal volume expansion/contraction.

### Architecture & Event Flow

```text
[1. Refinery]        [2. In-Transit IoT]   [3. Gas Station]
dispatch-service     telemetry-service     station-service
 (Python :8080)         (Go :8081)         (Python :8082)
       │                     │                    │
       └─────────────────────┼────────────────────┘
                             │                    ▼
                             │         [ Redpanda / Kafka :19092 ]
                             │           topic: station.discharges
                             │                    │
                             ▼                    ▼
                     reconciliation-service (Python :8083)
                             │
              ┌──────────────┴──────────────┐
              ▼                             ▼
      AWS Bedrock Mantle           PostgreSQL 16 (:5432)
   (AI Forensic Analysis)                   │
                                            ▼
                                  hitl-dashboard (:3000)
                                 (React + Vite + Tailwind)
```

### Microservices & Infrastructure

| Service | Stack | Port | Responsibility |
|---|---|---|---|
| **dispatch-service** | Python / FastAPI | `8080` | Refinery loading order creation & queries |
| **telemetry-service** | Go / `net/http` | `8081` | High-throughput IoT GPS pings & moving-valve security alerts |
| **station-service** | Python / FastAPI | `8082` | Tank discharge registration + publishes `DischargeRecorded` events |
| **reconciliation-service** | Python / FastAPI | `8083` | Redpanda consumer + variance computation + **AWS Bedrock Mantle** analysis + HITL API |
| **hitl-dashboard** | React / TypeScript / Vite | `3000` | Live auto-refreshing SOC console for human auditor verdicts |
| **redpanda** | Kafka-compatible Broker | `19092` | Asynchronous event bus |
| **postgres** | PostgreSQL 16 | `5432` | Relational database (`scripts/init.sql`) |

### Quick Start with Docker Compose

```bash
# 1. Create a root .env file with your AWS Bedrock Mantle token (optional, falls back gracefully if omitted)
cp services/reconciliation-service/.env.example .env

# 2. Build and launch the full stack (7 containers)
docker compose up -d --build
```

* **HITL Dashboard (UI):** http://localhost:3000
* **API Docs (Swagger):** http://localhost:8080/docs • http://localhost:8082/docs • http://localhost:8083/docs

### Tests & CI/CD

[`.github/workflows/ci.yml`](.github/workflows/ci.yml) runs all 4 microservice unit test suites and the frontend TypeScript/Vite build in parallel, then rebuilds every Docker image (`docker compose build --no-cache`) once all checks pass.

```bash
# Run tests locally
cd services/dispatch-service && pytest -v
cd services/station-service && pytest -v
cd services/reconciliation-service && pytest -v
cd services/telemetry-service && go test -v -race ./...
cd frontend && npm run build
```

### Security Note

Never commit `.env` files containing credentials. Use `.env.example` as a template and rotate any exposed keys.
