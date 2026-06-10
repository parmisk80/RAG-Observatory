"use client"

import { useEffect, useState } from "react"
import { Database, Boxes, Bot, Server, RefreshCw, Activity } from "lucide-react"
import { services } from "@/lib/metrics"
import { PageContainer } from "@/components/page-container"
import { StatusDot } from "@/components/status-dot"
import { Button } from "@/components/ui/button"

const icons: Record<string, typeof Database> = {
  Redis: Database,
  ChromaDB: Boxes,
  Ollama: Bot,
  Celery: Server,
}

const uptime: Record<string, string> = {
  Redis: "99.99%",
  ChromaDB: "99.97%",
  Ollama: "99.92%",
  Celery: "99.95%",
}

export function HealthView() {
  const [refreshing, setRefreshing] = useState(false)
  const [lastChecked, setLastChecked] = useState<string>("")

  useEffect(() => {
    setLastChecked(new Date().toLocaleTimeString())
  }, [])

  function refresh() {
    setRefreshing(true)
    setTimeout(() => {
      setRefreshing(false)
      setLastChecked(new Date().toLocaleTimeString())
    }, 900)
  }

  const allOnline = services.every((s) => s.status === "online")

  return (
    <PageContainer
      title="Health Center"
      description="Live status of every backend service powering the pipeline."
      action={
        <Button
          variant="outline"
          onClick={refresh}
          className="gap-2 border-border/70 bg-card/50"
        >
          <RefreshCw className={refreshing ? "size-4 animate-spin" : "size-4"} />
          Refresh
        </Button>
      }
    >
      <div
        className="mb-6 flex items-center gap-4 rounded-2xl border p-5"
        style={{
          borderColor: allOnline
            ? "color-mix(in oklch, var(--success) 40%, transparent)"
            : "var(--border)",
          backgroundColor: allOnline
            ? "color-mix(in oklch, var(--success) 8%, transparent)"
            : "var(--card)",
        }}
      >
        <div
          className="flex size-12 items-center justify-center rounded-xl"
          style={{
            color: "var(--success)",
            backgroundColor: "color-mix(in oklch, var(--success) 16%, transparent)",
          }}
        >
          <Activity className="size-6" />
        </div>
        <div className="flex-1">
          <p className="text-lg font-semibold">
            {allOnline ? "All systems operational" : "Some services degraded"}
          </p>
          <p className="text-sm text-muted-foreground">
            Last checked at {lastChecked || "—"}
          </p>
        </div>
        <StatusDot status={allOnline ? "online" : "degraded"} />
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        {services.map((s) => {
          const Icon = icons[s.name] ?? Server
          return (
            <div
              key={s.name}
              className="rounded-2xl border border-border/60 bg-card/60 p-5"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="flex size-10 items-center justify-center rounded-xl bg-accent/60 text-[var(--brand-purple)]">
                    <Icon className="size-5" />
                  </div>
                  <div>
                    <p className="font-medium">{s.name}</p>
                    <p className="text-xs text-muted-foreground">{s.detail}</p>
                  </div>
                </div>
                <StatusDot status={s.status} />
              </div>
              <div className="mt-4 grid grid-cols-2 gap-3">
                <div className="rounded-lg bg-background/50 p-3">
                  <p className="text-xs text-muted-foreground">Latency</p>
                  <p className="text-lg font-semibold tabular-nums">
                    {s.latencyMs}
                    <span className="text-sm text-muted-foreground"> ms</span>
                  </p>
                </div>
                <div className="rounded-lg bg-background/50 p-3">
                  <p className="text-xs text-muted-foreground">Uptime (30d)</p>
                  <p className="text-lg font-semibold tabular-nums">
                    {uptime[s.name]}
                  </p>
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </PageContainer>
  )
}
