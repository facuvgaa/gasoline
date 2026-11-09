package http

import (
	"encoding/json"
	"errors"
	"net/http"

	"telemetry-service/application/commands"
	usecases "telemetry-service/application/use_cases"
	"telemetry-service/domain/exceptions"
)

type TelemetryHandler struct {
	recordUC    *usecases.RecordTelemetryUseCase
	getLatestUC *usecases.GetLatestTelemetryUseCase
}

func NewTelemetryHandler(recordUC *usecases.RecordTelemetryUseCase, getLatestUC *usecases.GetLatestTelemetryUseCase) *TelemetryHandler {
	return &TelemetryHandler{
		recordUC:    recordUC,
		getLatestUC: getLatestUC,
	}
}

func (h *TelemetryHandler) RegisterRoutes(mux *http.ServeMux) {
	mux.HandleFunc("POST /telemetry", h.RecordTelemetry)
	mux.HandleFunc("GET /telemetry/trucks/{plate}/latest", h.GetLatestTelemetry)
}

func (h *TelemetryHandler) RecordTelemetry(w http.ResponseWriter, r *http.Request) {
	var cmd commands.RecordTelemetryCommand
	if err := json.NewDecoder(r.Body).Decode(&cmd); err != nil {
		h.respondError(w, http.StatusBadRequest, "cuerpo JSON inválido")
		return
	}

	response, err := h.recordUC.Execute(r.Context(), cmd)
	if err != nil {
		h.respondDomainError(w, err)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusCreated)
	json.NewEncoder(w).Encode(response)
}

func (h *TelemetryHandler) GetLatestTelemetry(w http.ResponseWriter, r *http.Request) {
	plate := r.PathValue("plate")
	if plate == "" {
		h.respondError(w, http.StatusBadRequest, "se requiere la patente del camión")
		return
	}

	response, err := h.getLatestUC.Execute(r.Context(), plate)
	if err != nil {
		h.respondDomainError(w, err)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

func (h *TelemetryHandler) respondDomainError(w http.ResponseWriter, err error) {
	status := http.StatusBadRequest
	if errors.Is(err, exceptions.ErrTelemetryNotFound) {
		status = http.StatusNotFound
	}
	h.respondError(w, status, err.Error())
}

func (h *TelemetryHandler) respondError(w http.ResponseWriter, statusCode int, message string) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(statusCode)
	json.NewEncoder(w).Encode(map[string]string{"error": message})
}
