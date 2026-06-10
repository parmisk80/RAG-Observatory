// Deterministic mock metrics for observability pages. In production these
// would come from GET /api/v1/metrics and the health endpoints.

// Concrete brand colors. Recharts and inline SVG render these as raw
// stroke/fill attributes, where oklch() CSS variables can fail to resolve.
export const BRAND = {
  purple: "#a78bfa",
  cyan: "#38d9d4",
  pink: "#fb7baf",
  indigo: "#818cf8",
  success: "#4ade80",
  warning: "#fbbf24",
} as const

export interface ServiceHealth {
  name: string
  status: "online" | "degraded" | "offline"
  latencyMs: number
  detail: string
}

export const services: ServiceHealth[] = [
  { name: "Redis", status: "online", latencyMs: 2, detail: "Broker & result backend" },
  { name: "ChromaDB", status: "online", latencyMs: 14, detail: "Vector store · 514 collections" },
  { name: "Ollama", status: "online", latencyMs: 88, detail: "llama3 · nomic-embed-text" },
  { name: "Celery", status: "online", latencyMs: 6, detail: "4 workers · 12 concurrency" },
]

export const kpis = {
  documentsIndexed: 326,
  totalChunks: 24817,
  embeddingsGenerated: 24817,
  retrievalCount: 18432,
  queryRewriteSuccess: 0.962,
  avgRetrievalScore: 0.841,
  avgEvaluationScore: 0.913,
  activeCeleryTasks: 3,
}

function series(base: number, spread: number, len = 14, seed = 1) {
  let s = seed
  const rng = () => {
    s = (s * 9301 + 49297) % 233280
    return s / 233280
  }
  const days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
  return Array.from({ length: len }, (_, i) => ({
    label: `${days[i % 7]} ${Math.floor(i / 7) + 1}`,
    value: Math.round(base + (rng() - 0.4) * spread + i * (spread / len)),
  }))
}

export const retrievalTrend = series(820, 260, 14, 7).map((d) => ({
  label: d.label,
  retrievals: d.value,
  rewrites: Math.round(d.value * 0.94),
}))

export const evalTrend = Array.from({ length: 14 }, (_, i) => {
  const days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
  return {
    label: `${days[i % 7]} ${Math.floor(i / 7) + 1}`,
    retrieval: +(0.78 + Math.sin(i / 2) * 0.05 + i * 0.003).toFixed(3),
    evaluation: +(0.86 + Math.cos(i / 3) * 0.04 + i * 0.003).toFixed(3),
  }
})

export const latencyTrend = Array.from({ length: 14 }, (_, i) => {
  const days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
  return {
    label: `${days[i % 7]} ${Math.floor(i / 7) + 1}`,
    retrieval: Math.round(120 + Math.sin(i) * 30 + 40),
    generation: Math.round(640 + Math.cos(i / 2) * 120 + 80),
  }
})

export const queryVolume = Array.from({ length: 24 }, (_, h) => ({
  label: `${h.toString().padStart(2, "0")}:00`,
  queries: Math.round(40 + Math.sin((h / 24) * Math.PI * 2) * 35 + 45),
}))
