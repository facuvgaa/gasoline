package main

import (
	"context"
	"log"
	"net/http"
	"os"
	"time"

	usecases "telemetry-service/application/use_cases"
	apiHttp "telemetry-service/infrastructure/http"
	"telemetry-service/infrastructure/persistence"

	"github.com/jackc/pgx/v5/pgxpool"
)

func main() {
	ctx := context.Background()

	// 1. Configuración desde entorno
	dbURL := os.Getenv("DATABASE_URL")
	if dbURL == "" {
		dbURL = "postgres://postgres:postgrespassword@localhost:5432/gasoline_db?sslmode=disable"
	}

	port := os.Getenv("PORT")
	if port == "" {
		port = ":8081" // Puerto 8081 para no chocar con el 8080 de dispatch-service
	}

	// 2. Conexión a PostgreSQL
	log.Println("🔌 Conectando telemetry-service a PostgreSQL...")
	pool, err := pgxpool.New(ctx, dbURL)
	if err != nil {
		log.Fatalf("Error inicializando pool de PostgreSQL: %v", err)
	}
	defer pool.Close()

	if err := pool.Ping(ctx); err != nil {
		log.Fatalf("No se pudo conectar a PostgreSQL: %v", err)
	}
	log.Println("✅ Conexión a PostgreSQL exitosa")

	// 3. Composición Hexagonal (Inyección de dependencias)
	repo := persistence.NewPostgresTelemetryRepository(pool)
	recordUC := usecases.NewRecordTelemetryUseCase(repo)
	getLatestUC := usecases.NewGetLatestTelemetryUseCase(repo)
	handler := apiHttp.NewTelemetryHandler(recordUC, getLatestUC)

	// 4. Enrutador HTTP
	mux := http.NewServeMux()
	handler.RegisterRoutes(mux)

	// Health check
	mux.HandleFunc("GET /health", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.Write([]byte(`{"status":"ok","service":"telemetry-service"}`))
	})

	server := &http.Server{
		Addr:         port,
		Handler:      withCORS(mux),
		ReadTimeout:  5 * time.Second,
		WriteTimeout: 5 * time.Second,
	}

	log.Printf("🚀 Telemetry Service (Go) escuchando en http://localhost%s\n", port)
	if err := server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
		log.Fatalf("Error en servidor HTTP: %v", err)
	}
}

func withCORS(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Access-Control-Allow-Origin", "*")
		w.Header().Set("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
		w.Header().Set("Access-Control-Allow-Headers", "Content-Type")
		if r.Method == http.MethodOptions {
			w.WriteHeader(http.StatusNoContent)
			return
		}
		next.ServeHTTP(w, r)
	})
}
