import type {
  HumanReviewPayload,
  ReconcileTripPayload,
  Reconciliation,
} from '../types/reconciliation';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8083';

export async function fetchReconciliations(status?: string): Promise<Reconciliation[]> {
  const url = status
    ? `${API_URL}/reconciliations?status=${encodeURIComponent(status)}`
    : `${API_URL}/reconciliations`;
  const res = await fetch(url);
  if (!res.ok) {
    throw new Error(`Error al obtener reconciliaciones (${res.status})`);
  }
  return res.json();
}

export async function submitHumanReview(
  id: string,
  payload: HumanReviewPayload,
): Promise<Reconciliation> {
  const res = await fetch(`${API_URL}/reconciliations/${id}/review`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const errBody = await res.json().catch(() => ({}));
    throw new Error(errBody.detail?.[0]?.msg || errBody.error || 'Error enviando revisión');
  }
  return res.json();
}

export async function simulateReconciliation(
  payload: ReconcileTripPayload,
): Promise<Reconciliation> {
  const res = await fetch(`${API_URL}/reconciliations`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    throw new Error(`Error creando reconciliación (${res.status})`);
  }
  return res.json();
}

export async function checkApiHealth(): Promise<boolean> {
  try {
    const res = await fetch(`${API_URL}/health`);
    return res.ok;
  } catch {
    return false;
  }
}
