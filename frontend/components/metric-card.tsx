import type { LucideIcon } from "lucide-react"
import { ArrowUpRight, ArrowDownRight } from "lucide-react"
import { cn } from "@/lib/utils"

export function MetricCard({
  label,
  value,
  icon: Icon,
  accent = "#a78bfa",
  delta,
  hint,
}: {
  label: string
  value: string | number
  icon: LucideIcon
  accent?: string
  delta?: number
  hint?: string
}) {
  return (
    <div className="group relative overflow-hidden rounded-2xl border border-border/60 bg-card/60 p-5 transition-all hover:border-border">
      <div
        className="pointer-events-none absolute -right-8 -top-8 size-28 rounded-full opacity-20 blur-2xl transition-opacity group-hover:opacity-40"
        style={{ backgroundColor: accent }}
      />
      <div className="flex items-start justify-between">
        <div
          className="flex size-10 items-center justify-center rounded-xl"
          style={{
            color: accent,
            backgroundColor: `color-mix(in oklch, ${accent} 14%, transparent)`,
          }}
        >
          <Icon className="size-5" />
        </div>
        {typeof delta === "number" && (
          <span
            className={cn(
              "flex items-center gap-0.5 rounded-md px-1.5 py-0.5 text-xs font-semibold",
              delta >= 0
                ? "bg-[color-mix(in_oklch,var(--success)_16%,transparent)] text-[var(--success)]"
                : "bg-[color-mix(in_oklch,var(--destructive)_16%,transparent)] text-destructive",
            )}
          >
            {delta >= 0 ? (
              <ArrowUpRight className="size-3" />
            ) : (
              <ArrowDownRight className="size-3" />
            )}
            {Math.abs(delta)}%
          </span>
        )}
      </div>
      <p className="mt-4 text-3xl font-semibold tracking-tight tabular-nums">
        {value}
      </p>
      <p className="mt-1 text-sm font-medium text-muted-foreground">{label}</p>
      {hint && (
        <p className="mt-0.5 text-xs text-muted-foreground/70">{hint}</p>
      )}
    </div>
  )
}
