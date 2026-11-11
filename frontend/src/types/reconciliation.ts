export type ReconciliationStatus =
  | 'NORMAL'
  | 'INVESTIGATION_REQUIRED'
  | 'FRAUD_SUSPECTED'
  | 'CONFIRMED_FRAUD'
  | 'DISMISSED_FALSE_ALARM';

export interface AIAnalysis {
  verdict: string;
  confidence: number;
  explanation: string;
  recommended_action: string;
}

export interface HumanReview {
  decision: 'CONFIRMED_FRAUD' | 'DISMISSED_FALSE_ALARM';
  notes: string;
  reviewed_by: string;
  reviewed_at: string;
}

export interface Reconciliation {
  id: string;
  dispatch_id: string;
  truck_plate: string;
  dispatched_volume: number;
  dispatched_temp_c: number;
  received_volume: number;
  received_temp_c: number;
  volume_variance_liters: number;
  volume_variance_percent: number;
  status: ReconciliationStatus;
  ai_analysis: AIAnalysis | null;
  human_review: HumanReview | null;
  created_at: string | null;
}

export interface ReconcileTripPayload {
  dispatch_id: string;
  truck_plate: string;
  dispatched_volume: number;
  dispatched_temp_c: number;
  received_volume: number;
  received_temp_c: number;
  valve_opened_in_transit: boolean;
  max_speed_kmh: number;
}

export interface HumanReviewPayload {
  decision: 'CONFIRMED_FRAUD' | 'DISMISSED_FALSE_ALARM';
  auditor_notes: string;
  reviewed_by: string;
}
