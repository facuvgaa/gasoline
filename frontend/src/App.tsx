import { useEffect, useMemo, useState } from 'react';
import {
  Activity,
  AlertTriangle,
  CheckCircle2,
  Droplets,
  Flame,
  Plus,
  RefreshCw,
  ShieldAlert,
  ShieldCheck,
  Sparkles,
  Thermometer,
  Truck,
  UserCheck,
  XCircle,
} from 'lucide-react';
import {
  checkApiHealth,
  fetchReconciliations,
  simulateReconciliation,
  submitHumanReview,
} from './services/api';
import type { Reconciliation, ReconciliationStatus } from './types/reconciliation';

type FilterTab = 'PENDING' | 'ALL' | 'CONFIRMED' | 'DISMISSED';

const STATUS_META: Record<
  ReconciliationStatus,
  { label: string; badgeClass: string }
> = {
  NORMAL: {
    label: 'Normal',
    badgeClass: 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30',
  },
  INVESTIGATION_REQUIRED: {
    label: 'Revisión Requerida',
    badgeClass: 'bg-amber-500/15 text-amber-300 border-amber-500/30',
  },
  FRAUD_SUSPECTED: {
    label: 'Fraude Sospechado',
    badgeClass: 'bg-rose-500/15 text-rose-300 border-rose-500/30',
  },
  CONFIRMED_FRAUD: {
    label: 'Fraude Confirmado',
    badgeClass: 'bg-red-600/25 text-red-200 border-red-500/50',
  },
  DISMISSED_FALSE_ALARM: {
    label: 'Falsa Alarma',
    badgeClass: 'bg-sky-500/15 text-sky-300 border-sky-500/30',
  },
};

export default function App() {
  const [items, setItems] = useState<Reconciliation[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [filter, setFilter] = useState<FilterTab>('PENDING');
  const [loading, setLoading] = useState(true);
  const [apiOnline, setApiOnline] = useState<boolean | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Human review form
  const [auditorName, setAuditorName] = useState('auditor.facu');
  const [auditorNotes, setAuditorNotes] = useState('');
  const [submittingReview, setSubmittingReview] = useState(false);

  // Simulate modal
  const [showModal, setShowModal] = useState(false);
  const [simulating, setSimulating] = useState(false);
  const [simForm, setSimForm] = useState({
    truck_plate: 'AF999ZZ',
    dispatched_volume: 32000,
    dispatched_temp_c: 15,
    received_volume: 31150,
    received_temp_c: 21.5,
    valve_opened_in_transit: true,
    max_speed_kmh: 78,
  });

  const loadData = async (silent = false) => {
    if (!silent) {
      setLoading(true);
      setErrorMsg(null);
    }
    const healthy = await checkApiHealth();
    setApiOnline(healthy);
    try {
      const data = await fetchReconciliations();
      setItems(data);
      setSelectedId((prev) => prev || (data.length > 0 ? data[0].id : null));
    } catch (err) {
      if (!silent) {
        setErrorMsg(err instanceof Error ? err.message : 'Error de conexión con backend');
      }
    } finally {
      if (!silent) {
        setLoading(false);
      }
    }
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(() => {
      loadData(true);
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  const filteredItems = useMemo(() => {
    return items.filter((item) => {
      if (filter === 'PENDING') {
        return (
          item.status === 'FRAUD_SUSPECTED' ||
          item.status === 'INVESTIGATION_REQUIRED'
        );
      }
      if (filter === 'CONFIRMED') return item.status === 'CONFIRMED_FRAUD';
      if (filter === 'DISMISSED') {
        return (
          item.status === 'DISMISSED_FALSE_ALARM' || item.status === 'NORMAL'
        );
      }
      return true;
    });
  }, [items, filter]);

  const selected = useMemo(
    () => items.find((i) => i.id === selectedId) || filteredItems[0] || null,
    [items, selectedId, filteredItems],
  );

  const stats = useMemo(() => {
    const pending = items.filter(
      (i) =>
        i.status === 'FRAUD_SUSPECTED' || i.status === 'INVESTIGATION_REQUIRED',
    ).length;
    const confirmed = items.filter((i) => i.status === 'CONFIRMED_FRAUD').length;
    const resolved = items.filter(
      (i) => i.status === 'DISMISSED_FALSE_ALARM' || i.status === 'NORMAL',
    ).length;
    return { total: items.length, pending, confirmed, resolved };
  }, [items]);

  const handleReview = async (
    decision: 'CONFIRMED_FRAUD' | 'DISMISSED_FALSE_ALARM',
  ) => {
    if (!selected) return;
    if (auditorNotes.trim().length < 3) {
      setErrorMsg('Ingresá una nota de auditoría (mínimo 3 caracteres).');
      return;
    }
    setSubmittingReview(true);
    setErrorMsg(null);
    try {
      const updated = await submitHumanReview(selected.id, {
        decision,
        auditor_notes: auditorNotes.trim(),
        reviewed_by: auditorName.trim() || 'auditor',
      });
      setItems((prev) =>
        prev.map((it) => (it.id === updated.id ? updated : it)),
      );
      setAuditorNotes('');
    } catch (err) {
      setErrorMsg(err instanceof Error ? err.message : 'Error guardando revisión');
    } finally {
      setSubmittingReview(false);
    }
  };

  const handleSimulate = async (e: React.FormEvent) => {
    e.preventDefault();
    setSimulating(true);
    setErrorMsg(null);
    try {
      const created = await simulateReconciliation({
        dispatch_id: `DSP-${Math.floor(1000 + Math.random() * 9000)}`,
        ...simForm,
      });
      setItems((prev) => [created, ...prev]);
      setSelectedId(created.id);
      if (
        created.status === 'FRAUD_SUSPECTED' ||
        created.status === 'INVESTIGATION_REQUIRED'
      ) {
        setFilter('PENDING');
      } else {
        setFilter('ALL');
      }
      setShowModal(false);
    } catch (err) {
      setErrorMsg(err instanceof Error ? err.message : 'Error simulando viaje');
    } finally {
      setSimulating(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      {/* Top Bar */}
      <header className="border-b border-slate-800/80 bg-slate-900/70 backdrop-blur sticky top-0 z-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="h-9 w-9 rounded-lg bg-amber-500/15 border border-amber-500/30 flex items-center justify-center text-amber-400">
              <Flame className="w-5 h-5" />
            </div>
            <div>
              <h1 className="text-base font-semibold tracking-tight flex items-center gap-2">
                Gasoline SOC
                <span className="text-xs font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                  HITL Console
                </span>
              </h1>
              <p className="text-xs text-slate-400">
                Auditoría de Mermas &amp; Fraude • AWS Bedrock Mantle
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="hidden sm:flex items-center gap-2 text-xs px-3 py-1.5 rounded-full bg-slate-900 border border-slate-800">
              <span
                className={`h-2 w-2 rounded-full ${
                  apiOnline === true
                    ? 'bg-emerald-400 animate-pulse'
                    : apiOnline === false
                      ? 'bg-rose-500'
                      : 'bg-slate-500'
                }`}
              />
              <span className="text-slate-300">
                {apiOnline === true
                  ? 'Live • API (:8083)'
                  : apiOnline === false
                    ? 'API Offline'
                    : 'Conectando...'}
              </span>
            </div>

            <button
              onClick={() => loadData(false)}
              className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-200 transition cursor-pointer"
              title="Actualizar ahora"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            </button>

            <button
              onClick={() => setShowModal(true)}
              className="flex items-center gap-2 px-3.5 py-2 rounded-lg bg-amber-500 hover:bg-amber-400 text-slate-950 font-semibold text-sm transition cursor-pointer"
            >
              <Plus className="w-4 h-4" />
              Simular Viaje
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl w-full mx-auto px-4 sm:px-6 py-6 flex-1 flex flex-col gap-6">
        {errorMsg && (
          <div className="px-4 py-3 rounded-lg bg-rose-500/15 border border-rose-500/40 text-rose-200 text-sm flex items-center justify-between">
            <span className="flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 shrink-0" />
              {errorMsg}
            </span>
            <button
              onClick={() => setErrorMsg(null)}
              className="text-xs underline opacity-80 hover:opacity-100"
            >
              Cerrar
            </button>
          </div>
        )}

        {/* KPI Cards */}
        <section className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <KpiCard
            title="Viajes Auditados"
            value={stats.total}
            icon={<Truck className="w-4 h-4 text-slate-400" />}
          />
          <KpiCard
            title="Pendientes Humano"
            value={stats.pending}
            highlight={stats.pending > 0 ? 'amber' : undefined}
            icon={<ShieldAlert className="w-4 h-4 text-amber-400" />}
          />
          <KpiCard
            title="Fraudes Confirmados"
            value={stats.confirmed}
            highlight={stats.confirmed > 0 ? 'red' : undefined}
            icon={<XCircle className="w-4 h-4 text-rose-400" />}
          />
          <KpiCard
            title="Normales / Descartados"
            value={stats.resolved}
            icon={<ShieldCheck className="w-4 h-4 text-emerald-400" />}
          />
        </section>

        {/* Split Master-Detail */}
        <section className="grid grid-cols-1 lg:grid-cols-12 gap-6 flex-1">
          {/* Left Queue */}
          <div className="lg:col-span-5 flex flex-col bg-slate-900/60 border border-slate-800 rounded-xl overflow-hidden">
            <div className="p-3 border-b border-slate-800 flex items-center gap-1.5 overflow-x-auto">
              {(
                [
                  ['PENDING', `Pendientes (${stats.pending})`],
                  ['ALL', `Todos (${stats.total})`],
                  ['CONFIRMED', 'Confirmados'],
                  ['DISMISSED', 'Cerrados'],
                ] as [FilterTab, string][]
              ).map(([tab, label]) => (
                <button
                  key={tab}
                  onClick={() => setFilter(tab)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap transition cursor-pointer ${
                    filter === tab
                      ? 'bg-slate-800 text-white border border-slate-700'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                  }`}
                >
                  {label}
                </button>
              ))}
            </div>

            <div className="divide-y divide-slate-800/80 max-h-[620px] overflow-y-auto">
              {filteredItems.length === 0 ? (
                <div className="p-10 text-center text-slate-500 text-sm">
                  No hay incidentes en esta bandeja.
                  <br />
                  Usá <strong className="text-amber-400">Simular Viaje</strong> arriba para probar AWS Bedrock.
                </div>
              ) : (
                filteredItems.map((item) => {
                  const meta = STATUS_META[item.status];
                  const isActive = selected?.id === item.id;
                  return (
                    <button
                      key={item.id}
                      onClick={() => setSelectedId(item.id)}
                      className={`w-full text-left p-4 transition hover:bg-slate-800/40 cursor-pointer ${
                        isActive ? 'bg-slate-800/70 border-l-2 border-l-amber-400' : ''
                      }`}
                    >
                      <div className="flex items-center justify-between gap-2 mb-1.5">
                        <span className="font-mono text-sm font-semibold text-white">
                          {item.truck_plate}
                        </span>
                        <span
                          className={`text-[11px] font-medium px-2 py-0.5 rounded-full border ${meta.badgeClass}`}
                        >
                          {meta.label}
                        </span>
                      </div>
                      <div className="flex items-center justify-between text-xs text-slate-400">
                        <span className="font-mono">{item.dispatch_id}</span>
                        <span
                          className={`font-mono font-semibold ${
                            item.volume_variance_liters < -100
                              ? 'text-rose-400'
                              : 'text-slate-300'
                          }`}
                        >
                          {item.volume_variance_liters > 0 ? '+' : ''}
                          {item.volume_variance_liters} L ({item.volume_variance_percent}%)
                        </span>
                      </div>
                      {item.ai_analysis && (
                        <div className="mt-2 flex items-center gap-1.5 text-[11px] text-purple-300">
                          <Sparkles className="w-3.5 h-3.5" />
                          <span>IA: {item.ai_analysis.verdict}</span>
                          <span className="text-slate-500">•</span>
                          <span>{Math.round(item.ai_analysis.confidence * 100)}% conf.</span>
                        </div>
                      )}
                    </button>
                  );
                })
              )}
            </div>
          </div>

          {/* Right Forensic Panel */}
          <div className="lg:col-span-7 bg-slate-900/60 border border-slate-800 rounded-xl p-5 flex flex-col gap-5">
            {!selected ? (
              <div className="flex-1 flex flex-col items-center justify-center text-slate-500 py-20 text-sm">
                <Activity className="w-10 h-10 mb-3 opacity-40" />
                Seleccioná un viaje de la izquierda para auditar.
              </div>
            ) : (
              <>
                {/* Detail Header */}
                <div className="flex flex-wrap items-start justify-between gap-4 pb-4 border-b border-slate-800">
                  <div>
                    <div className="flex items-center gap-2.5">
                      <h2 className="text-xl font-bold font-mono text-white">
                        {selected.truck_plate}
                      </h2>
                      <span
                        className={`text-xs font-medium px-2.5 py-0.5 rounded-full border ${
                          STATUS_META[selected.status].badgeClass
                        }`}
                      >
                        {STATUS_META[selected.status].label}
                      </span>
                    </div>
                    <p className="text-xs text-slate-400 mt-1 font-mono">
                      Dispatch: {selected.dispatch_id} • ID: {selected.id.slice(0, 8)}
                    </p>
                  </div>

                  <div className="text-right">
                    <div className="text-xs text-slate-400">Varianza Neta</div>
                    <div
                      className={`text-2xl font-bold font-mono ${
                        selected.volume_variance_liters < -100
                          ? 'text-rose-400'
                          : 'text-emerald-400'
                      }`}
                    >
                      {selected.volume_variance_liters > 0 ? '+' : ''}
                      {selected.volume_variance_liters} L
                    </div>
                  </div>
                </div>

                {/* Physical Measurements */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                  <MetricBox
                    icon={<Droplets className="w-3.5 h-3.5 text-sky-400" />}
                    label="Cargado Refinería"
                    value={`${selected.dispatched_volume.toLocaleString()} L`}
                  />
                  <MetricBox
                    icon={<Thermometer className="w-3.5 h-3.5 text-sky-400" />}
                    label="Temp. Despacho"
                    value={`${selected.dispatched_temp_c} °C`}
                  />
                  <MetricBox
                    icon={<Droplets className="w-3.5 h-3.5 text-amber-400" />}
                    label="Recibido Estación"
                    value={`${selected.received_volume.toLocaleString()} L`}
                  />
                  <MetricBox
                    icon={<Thermometer className="w-3.5 h-3.5 text-amber-400" />}
                    label="Temp. Descarga"
                    value={`${selected.received_temp_c} °C`}
                  />
                </div>

                {/* AWS Bedrock Analysis Card */}
                {selected.ai_analysis ? (
                  <div className="rounded-xl bg-purple-950/20 border border-purple-500/30 p-4 space-y-3">
                    <div className="flex items-center justify-between gap-2">
                      <div className="flex items-center gap-2 text-purple-300 font-semibold text-sm">
                        <Sparkles className="w-4 h-4" />
                        Peritaje AI - Powered by AWS Bedrock Mantle
                      </div>
                      <span className="text-xs font-mono px-2 py-0.5 rounded bg-purple-500/20 text-purple-200 border border-purple-500/30">
                        Confianza: {Math.round(selected.ai_analysis.confidence * 100)}%
                      </span>
                    </div>

                    <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-purple-400 rounded-full transition-all"
                        style={{
                          width: `${Math.min(100, Math.round(selected.ai_analysis.confidence * 100))}%`,
                        }}
                      />
                    </div>

                    <div className="space-y-2 text-sm">
                      <div>
                        <span className="text-xs uppercase tracking-wider text-slate-400">
                          Veredicto IA:{' '}
                        </span>
                        <span className="font-mono font-semibold text-purple-200">
                          {selected.ai_analysis.verdict}
                        </span>
                      </div>
                      <p className="text-slate-300 leading-relaxed">
                        {selected.ai_analysis.explanation}
                      </p>
                      <div className="pt-2 border-t border-purple-500/20 text-xs text-purple-200">
                        <strong>Acción recomendada:</strong>{' '}
                        {selected.ai_analysis.recommended_action}
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="rounded-xl bg-emerald-950/20 border border-emerald-500/30 p-4 text-sm text-emerald-200 flex items-center gap-2.5">
                    <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0" />
                    Viaje dentro de tolerancia física normal. No requirió análisis de IA.
                  </div>
                )}

                {/* Human-in-the-Loop Decision Panel */}
                {selected.human_review ? (
                  <div className="rounded-xl bg-slate-800/60 border border-slate-700 p-4 space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="flex items-center gap-2 text-sm font-semibold text-white">
                        <UserCheck className="w-4 h-4 text-emerald-400" />
                        Resolución Humana Auditada
                      </span>
                      <span className="text-xs font-mono text-slate-400">
                        Por {selected.human_review.reviewed_by}
                      </span>
                    </div>
                    <p className="text-sm text-slate-300">
                      <strong>Decisión:</strong> {selected.human_review.decision}
                    </p>
                    <p className="text-sm text-slate-300">
                      <strong>Notas:</strong> {selected.human_review.notes}
                    </p>
                  </div>
                ) : (
                  selected.status !== 'NORMAL' && (
                    <div className="rounded-xl bg-slate-800/40 border border-slate-700/80 p-4 space-y-3">
                      <div className="flex items-center justify-between">
                        <h3 className="text-sm font-semibold text-white flex items-center gap-2">
                          <UserCheck className="w-4 h-4 text-amber-400" />
                          Decisión Human-in-the-Loop
                        </h3>
                        <input
                          type="text"
                          value={auditorName}
                          onChange={(e) => setAuditorName(e.target.value)}
                          placeholder="Auditor"
                          className="text-xs bg-slate-900 border border-slate-700 rounded-md px-2.5 py-1 text-slate-200 w-36 focus:outline-none focus:border-amber-500"
                        />
                      </div>

                      <textarea
                        rows={3}
                        value={auditorNotes}
                        onChange={(e) => setAuditorNotes(e.target.value)}
                        placeholder="Escribí las conclusiones de auditoría (ej: Se revisaron precintos y cámaras en peaje)..."
                        className="w-full rounded-lg bg-slate-950 border border-slate-700 p-3 text-sm text-slate-100 placeholder:text-slate-500 focus:outline-none focus:border-amber-500"
                      />

                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                        <button
                          disabled={submittingReview}
                          onClick={() => handleReview('CONFIRMED_FRAUD')}
                          className="flex items-center justify-center gap-2 py-2.5 px-4 rounded-lg bg-rose-600 hover:bg-rose-500 disabled:opacity-50 text-white font-semibold text-sm transition cursor-pointer"
                        >
                          <ShieldAlert className="w-4 h-4" />
                          Confirmar Fraude / Bloquear
                        </button>
                        <button
                          disabled={submittingReview}
                          onClick={() => handleReview('DISMISSED_FALSE_ALARM')}
                          className="flex items-center justify-center gap-2 py-2.5 px-4 rounded-lg bg-slate-700 hover:bg-slate-600 disabled:opacity-50 text-slate-100 font-semibold text-sm transition cursor-pointer"
                        >
                          <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                          Descartar (Falsa Alarma)
                        </button>
                      </div>
                    </div>
                  )
                )}
              </>
            )}
          </div>
        </section>
      </main>

      {/* Simulate Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-xl max-w-md w-full p-6 space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-bold text-white">
                Simular Viaje para Auditoría
              </h3>
              <button
                onClick={() => setShowModal(false)}
                className="text-slate-400 hover:text-white text-sm"
              >
                ✕
              </button>
            </div>

            <div className="flex gap-2">
              <button
                type="button"
                onClick={() =>
                  setSimForm({
                    truck_plate: 'AF999ZZ',
                    dispatched_volume: 32000,
                    dispatched_temp_c: 15,
                    received_volume: 31150,
                    received_temp_c: 21.5,
                    valve_opened_in_transit: true,
                    max_speed_kmh: 78,
                  })
                }
                className="flex-1 text-xs py-1.5 px-2 rounded bg-rose-500/15 border border-rose-500/30 text-rose-300 hover:bg-rose-500/25 cursor-pointer"
              >
                Preset: Robo en Ruta (-850L)
              </button>
              <button
                type="button"
                onClick={() =>
                  setSimForm({
                    truck_plate: 'AB100CD',
                    dispatched_volume: 30000,
                    dispatched_temp_c: 15,
                    received_volume: 29970,
                    received_temp_c: 14,
                    valve_opened_in_transit: false,
                    max_speed_kmh: 80,
                  })
                }
                className="flex-1 text-xs py-1.5 px-2 rounded bg-emerald-500/15 border border-emerald-500/30 text-emerald-300 hover:bg-emerald-500/25 cursor-pointer"
              >
                Preset: Viaje Normal
              </button>
            </div>

            <form onSubmit={handleSimulate} className="space-y-3 text-sm">
              <div className="grid grid-cols-2 gap-3">
                <label className="block">
                  <span className="text-xs text-slate-400">Patente</span>
                  <input
                    className="mt-1 w-full bg-slate-950 border border-slate-700 rounded px-2.5 py-1.5"
                    value={simForm.truck_plate}
                    onChange={(e) =>
                      setSimForm({ ...simForm, truck_plate: e.target.value })
                    }
                  />
                </label>
                <label className="block">
                  <span className="text-xs text-slate-400">Vel. Máx (km/h)</span>
                  <input
                    type="number"
                    className="mt-1 w-full bg-slate-950 border border-slate-700 rounded px-2.5 py-1.5"
                    value={simForm.max_speed_kmh}
                    onChange={(e) =>
                      setSimForm({
                        ...simForm,
                        max_speed_kmh: Number(e.target.value),
                      })
                    }
                  />
                </label>
                <label className="block">
                  <span className="text-xs text-slate-400">Cargado (L)</span>
                  <input
                    type="number"
                    className="mt-1 w-full bg-slate-950 border border-slate-700 rounded px-2.5 py-1.5"
                    value={simForm.dispatched_volume}
                    onChange={(e) =>
                      setSimForm({
                        ...simForm,
                        dispatched_volume: Number(e.target.value),
                      })
                    }
                  />
                </label>
                <label className="block">
                  <span className="text-xs text-slate-400">Recibido (L)</span>
                  <input
                    type="number"
                    className="mt-1 w-full bg-slate-950 border border-slate-700 rounded px-2.5 py-1.5"
                    value={simForm.received_volume}
                    onChange={(e) =>
                      setSimForm({
                        ...simForm,
                        received_volume: Number(e.target.value),
                      })
                    }
                  />
                </label>
              </div>

              <label className="flex items-center gap-2 pt-1 cursor-pointer">
                <input
                  type="checkbox"
                  checked={simForm.valve_opened_in_transit}
                  onChange={(e) =>
                    setSimForm({
                      ...simForm,
                      valve_opened_in_transit: e.target.checked,
                    })
                  }
                  className="rounded border-slate-700"
                />
                <span className="text-xs text-slate-300">
                  Válvula de descarga se abrió en ruta (Alerta Telemetría)
                </span>
              </label>

              <button
                type="submit"
                disabled={simulating}
                className="w-full py-2.5 rounded-lg bg-amber-500 hover:bg-amber-400 text-slate-950 font-semibold transition cursor-pointer disabled:opacity-50"
              >
                {simulating
                  ? 'Analizando con AWS Bedrock...'
                  : 'Ejecutar Reconciliación'}
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

function KpiCard({
  title,
  value,
  icon,
  highlight,
}: {
  title: string;
  value: number;
  icon: React.ReactNode;
  highlight?: 'amber' | 'red';
}) {
  const border =
    highlight === 'red'
      ? 'border-rose-500/40 bg-rose-950/10'
      : highlight === 'amber'
        ? 'border-amber-500/40 bg-amber-950/10'
        : 'border-slate-800 bg-slate-900/60';

  return (
    <div className={`rounded-xl border p-4 ${border}`}>
      <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
        <span>{title}</span>
        {icon}
      </div>
      <div className="text-2xl font-bold font-mono text-white">{value}</div>
    </div>
  );
}

function MetricBox({
  icon,
  label,
  value,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
}) {
  return (
    <div className="rounded-lg bg-slate-950/70 border border-slate-800 p-3">
      <div className="flex items-center gap-1.5 text-[11px] text-slate-400 mb-1">
        {icon}
        <span>{label}</span>
      </div>
      <div className="text-sm font-mono font-semibold text-white">{value}</div>
    </div>
  );
}
