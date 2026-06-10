"use client"

import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip as RTooltip,
  XAxis,
  YAxis,
} from "recharts"
import { evalTrend, latencyTrend, queryVolume, retrievalTrend } from "@/lib/metrics"
import { PageContainer } from "@/components/page-container"

const tooltipStyle = {
  background: "var(--popover)",
  border: "1px solid var(--border)",
  borderRadius: 12,
  fontSize: 12,
  color: "var(--popover-foreground)",
}

const axisProps = {
  stroke: "var(--muted-foreground)",
  fontSize: 11,
  tickLine: false,
  axisLine: false,
}

// Recharts renders these as raw SVG stroke/fill attributes, where some engines
// fail to resolve oklch() CSS variables. Use concrete colors for reliability.
const C = {
  purple: "#a78bfa",
  cyan: "#38d9d4",
  pink: "#fb7baf",
  indigo: "#818cf8",
  success: "#4ade80",
  grid: "rgba(255,255,255,0.08)",
}

function ChartCard({
  title,
  subtitle,
  children,
  legend,
}: {
  title: string
  subtitle: string
  children: React.ReactNode
  legend?: { label: string; color: string }[]
}) {
  return (
    <div className="rounded-2xl border border-border/60 bg-card/60 p-5">
      <div className="mb-4 flex items-start justify-between gap-4">
        <div>
          <h2 className="text-sm font-semibold">{title}</h2>
          <p className="text-xs text-muted-foreground">{subtitle}</p>
        </div>
        {legend && (
          <div className="flex flex-wrap items-center gap-3">
            {legend.map((l) => (
              <span key={l.label} className="flex items-center gap-1.5 text-xs text-muted-foreground">
                <span className="size-2.5 rounded-sm" style={{ backgroundColor: l.color }} />
                {l.label}
              </span>
            ))}
          </div>
        )}
      </div>
      {children}
    </div>
  )
}

export function MonitoringView() {
  return (
    <PageContainer
      title="Monitoring"
      description="Interactive trends across the retrieval and generation pipeline. Hover any chart for exact values."
    >
      <div className="grid gap-6 lg:grid-cols-2">
        <ChartCard
          title="Retrieval Trends"
          subtitle="Retrievals vs query rewrites"
          legend={[
            { label: "Retrievals", color: C.purple },
            { label: "Rewrites", color: C.cyan },
          ]}
        >
          <ResponsiveContainer width="100%" height={260}>
            <AreaChart data={retrievalTrend}>
              <defs>
                <linearGradient id="mRet" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor={C.purple} stopOpacity={0.45} />
                  <stop offset="100%" stopColor={C.purple} stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke={C.grid} vertical={false} />
              <XAxis dataKey="label" {...axisProps} />
              <YAxis width={32} {...axisProps} />
              <RTooltip contentStyle={tooltipStyle} />
              <Area type="monotone" dataKey="retrievals" stroke={C.purple} strokeWidth={2} fill="url(#mRet)" />
              <Area type="monotone" dataKey="rewrites" stroke={C.cyan} strokeWidth={2} fillOpacity={0} />
            </AreaChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard
          title="Evaluation Trends"
          subtitle="Faithfulness & retrieval quality scores"
          legend={[
            { label: "Evaluation", color: C.success },
            { label: "Retrieval", color: C.pink },
          ]}
        >
          <ResponsiveContainer width="100%" height={260}>
            <LineChart data={evalTrend}>
              <CartesianGrid strokeDasharray="3 3" stroke={C.grid} vertical={false} />
              <XAxis dataKey="label" {...axisProps} />
              <YAxis domain={[0.6, 1]} width={32} {...axisProps} />
              <RTooltip contentStyle={tooltipStyle} />
              <Line type="monotone" dataKey="evaluation" stroke={C.success} strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="retrieval" stroke={C.pink} strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard
          title="Processing Latency"
          subtitle="Retrieval vs generation (ms)"
          legend={[
            { label: "Retrieval", color: C.indigo },
            { label: "Generation", color: C.pink },
          ]}
        >
          <ResponsiveContainer width="100%" height={260}>
            <LineChart data={latencyTrend}>
              <CartesianGrid strokeDasharray="3 3" stroke={C.grid} vertical={false} />
              <XAxis dataKey="label" {...axisProps} />
              <YAxis width={40} {...axisProps} />
              <RTooltip contentStyle={tooltipStyle} />
              <Line type="monotone" dataKey="retrieval" stroke={C.indigo} strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="generation" stroke={C.pink} strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Query Volume" subtitle="Queries per hour (today)">
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={queryVolume}>
              <CartesianGrid strokeDasharray="3 3" stroke={C.grid} vertical={false} />
              <XAxis dataKey="label" interval={3} {...axisProps} />
              <YAxis width={32} {...axisProps} />
              <RTooltip contentStyle={tooltipStyle} cursor={{ fill: "var(--accent)", opacity: 0.4 }} />
              <Bar dataKey="queries" fill={C.cyan} radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>
    </PageContainer>
  )
}
