import { cn } from "@/lib/utils"

const map = {
  online: { label: "Online", color: "var(--success)" },
  degraded: { label: "Degraded", color: "var(--warning)" },
  offline: { label: "Offline", color: "var(--destructive)" },
} as const

export function StatusDot({
  status,
  withLabel = true,
}: {
  status: keyof typeof map
  withLabel?: boolean
}) {
  const s = map[status]
  return (
    <span className="inline-flex items-center gap-1.5">
      <span className="relative flex size-2.5">
        {status === "online" && (
          <span
            className="absolute inline-flex size-full animate-ping rounded-full opacity-60"
            style={{ backgroundColor: s.color }}
          />
        )}
        <span
          className="relative inline-flex size-2.5 rounded-full"
          style={{ backgroundColor: s.color }}
        />
      </span>
      {withLabel && (
        <span
          className={cn("text-xs font-medium")}
          style={{ color: s.color }}
        >
          {s.label}
        </span>
      )}
    </span>
  )
}
