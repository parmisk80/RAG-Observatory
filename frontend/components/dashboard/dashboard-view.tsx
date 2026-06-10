"use client"

import {
  FileStack,
  Boxes,
  Cpu,
  Search,
  Repeat2,
  Crosshair,
  ShieldCheck,
  ListChecks,
  Database,
  Server,
  Bot,
} from "lucide-react"
import {
  Area,
  AreaChart,
  ResponsiveContainer,
  XAxis,
  YAxis,
  Tooltip as RTooltip,
  CartesianGrid,
} from "recharts"
import { kpis, services, retrievalTrend, BRAND } from "@/lib/metrics"
import { useStore } from "@/lib/store"
import { PageContainer } from "@/components/page-container"
import { MetricCard } from "@/components/metric-card"
import { StatusDot } from "@/components/status-dot"

function Gauge({
  value,
  label,
  color,
}: {
  value: number
  label: string
  color: string
}) {
  const pct = Math.round(value * 100)
  const r = 34
  const c = 2 * Math.PI * r
  const offset = c - (pct / 100) * c
  return (
    <div className="flex flex-col items-center gap-2 rounded-2xl border border-border/60 bg-card/60 p-5">
      <div className="relative size-24">
        <svg viewBox="0 0 80 80" className="size-24 -rotate-90">
          <circle
            cx="40"
            cy="40"
            r={r}
            fill="none"
            stroke="rgba(255,255,255,0.1)"
            strokeWidth="7"
          />
          <circle
            cx="40"
            cy="40"
            r={r}
            fill="none"
            stroke={color}
            strokeWidth="7"
            strokeLinecap="round"
            strokeDasharray={c}
            strokeDashoffset={offset}
          />
        </svg>
        <span className="absolute inset-0 flex items-center justify-center text-xl font-semibold tabular-nums">
          {pct}%
        </span>
      </div>
      <p className="text-center text-sm font-medium text-muted-foreground">
        {label}
      </p>
    </div>
  )
}

const serviceIcon: Record<string, typeof Database> = {
  Redis: Database,
  ChromaDB: Boxes,
  Ollama: Bot,
  Celery: Server,
}

export function DashboardView() {
  const { documents } = useStore()
  const indexed = documents.filter((d) => d.status === "indexed").length

  return (
    <PageContainer
      title="Dashboard"
      description="Real-time observability across ingestion, retrieval, generation, and evaluation."
    >
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <MetricCard
          label="Documents Indexed"
          value={(kpis.documentsIndexed + indexed).toLocaleString()}
          icon={FileStack}
          accent={BRAND.purple}
          delta={8}
        />
        <MetricCard
          label="Total Chunks"
          value={kpis.totalChunks.toLocaleString()}
          icon={Boxes}
          accent={BRAND.indigo}
          delta={12}
        />
        <MetricCard
          label="Embeddings Generated"
          value={kpis.embeddingsGenerated.toLocaleString()}
          icon={Cpu}
          accent={BRAND.cyan}
          delta={12}
        />
        <MetricCard
          label="Retrieval Count"
          value={kpis.retrievalCount.toLocaleString()}
          icon={Search}
          accent={BRAND.pink}
          delta={5}
        />
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2 rounded-2xl border border-border/60 bg-card/60 p-5">
          <div className="mb-4 flex items-center justify-between">
            <div>
              <h2 className="text-sm font-semibold">Retrieval & Query Rewrite</h2>
              <p className="text-xs text-muted-foreground">Last 14 days</p>
            </div>
            <ListChecks className="size-4 text-muted-foreground" />
          </div>
          <ResponsiveContainer width="100%" height={240}>
            <AreaChart data={retrievalTrend}>
              <defs>
                <linearGradient id="gRet" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor={BRAND.purple} stopOpacity={0.5} />
                  <stop offset="100%" stopColor={BRAND.purple} stopOpacity={0} />
                </linearGradient>
                <linearGradient id="gRew" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor={BRAND.cyan} stopOpacity={0.5} />
                  <stop offset="100%" stopColor={BRAND.cyan} stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.08)" vertical={false} />
              <XAxis dataKey="label" stroke="var(--muted-foreground)" fontSize={11} tickLine={false} axisLine={false} />
              <YAxis stroke="var(--muted-foreground)" fontSize={11} tickLine={false} axisLine={false} width={32} />
              <RTooltip
                contentStyle={{
                  background: "var(--popover)",
                  border: "1px solid var(--border)",
                  borderRadius: 12,
                  fontSize: 12,
                  color: "var(--popover-foreground)",
                }}
              />
              <Area type="monotone" dataKey="retrievals" stroke={BRAND.purple} strokeWidth={2} fill="url(#gRet)" />
              <Area type="monotone" dataKey="rewrites" stroke={BRAND.cyan} strokeWidth={2} fill="url(#gRew)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        <div className="grid grid-cols-2 gap-4 lg:grid-cols-1">
          <Gauge value={kpis.queryRewriteSuccess} label="Query Rewrite Success" color={BRAND.indigo} />
          <Gauge value={kpis.avgRetrievalScore} label="Avg Retrieval Score" color={BRAND.cyan} />
        </div>
      </div>

      <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <MetricCard
          label="Query Rewrite Success"
          value={`${(kpis.queryRewriteSuccess * 100).toFixed(1)}%`}
          icon={Repeat2}
          accent={BRAND.indigo}
        />
        <MetricCard
          label="Avg Retrieval Score"
          value={kpis.avgRetrievalScore.toFixed(3)}
          icon={Crosshair}
          accent={BRAND.cyan}
        />
        <MetricCard
          label="Avg Evaluation Score"
          value={kpis.avgEvaluationScore.toFixed(3)}
          icon={ShieldCheck}
          accent={BRAND.success}
        />
        <MetricCard
          label="Active Celery Tasks"
          value={kpis.activeCeleryTasks}
          icon={Server}
          accent={BRAND.warning}
          hint="Running background jobs"
        />
      </div>

      <div className="mt-6 rounded-2xl border border-border/60 bg-card/60 p-5">
        <h2 className="mb-4 text-sm font-semibold">Service Health</h2>
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {services.map((s) => {
            const Icon = serviceIcon[s.name] ?? Server
            return (
              <div
                key={s.name}
                className="flex items-center gap-3 rounded-xl border border-border/50 bg-background/40 p-3"
              >
                <div className="flex size-9 items-center justify-center rounded-lg bg-accent/60" style={{ color: BRAND.purple }}>
                  <Icon className="size-4" />
                </div>
                <div className="min-w-0 flex-1">
                  <div className="flex items-center justify-between gap-2">
                    <p className="text-sm font-medium">{s.name}</p>
                    <StatusDot status={s.status} withLabel={false} />
                  </div>
                  <p className="truncate text-[11px] text-muted-foreground">
                    {s.latencyMs}ms · {s.detail}
                  </p>
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </PageContainer>
  )
}
