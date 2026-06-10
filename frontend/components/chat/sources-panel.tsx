"use client"

import { useState } from "react"
import { ChevronDown, FileText, Quote } from "lucide-react"
import type { Citation } from "@/lib/types"
import { cn } from "@/lib/utils"

function scoreColor(s: number) {
  if (s >= 0.85) return "var(--success)"
  if (s >= 0.72) return "var(--brand-cyan)"
  return "var(--warning)"
}

export function SourcesPanel({ citations }: { citations: Citation[] }) {
  const [open, setOpen] = useState<string | null>(citations[0]?.id ?? null)

  if (!citations.length) return null

  return (
    <div className="mt-3 rounded-xl border border-border/60 bg-card/40">
      <div className="flex items-center gap-2 border-b border-border/60 px-3 py-2">
        <Quote className="size-3.5 text-[var(--brand-purple)]" />
        <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
          {citations.length} Sources
        </span>
      </div>
      <div className="divide-y divide-border/50">
        {citations.map((c) => {
          const expanded = open === c.id
          return (
            <div key={c.id}>
              <button
                onClick={() => setOpen(expanded ? null : c.id)}
                className="flex w-full items-center gap-3 px-3 py-2.5 text-left transition-colors hover:bg-accent/40"
              >
                <FileText className="size-4 shrink-0 text-muted-foreground" />
                <div className="min-w-0 flex-1">
                  <p className="truncate text-sm font-medium">{c.documentName}</p>
                  <p className="truncate text-xs text-muted-foreground">
                    {c.section ? `${c.section} · ` : ""}
                    {c.page ? `p.${c.page}` : ""}
                  </p>
                </div>
                <span
                  className="rounded-md px-2 py-0.5 text-[11px] font-semibold tabular-nums"
                  style={{
                    color: scoreColor(c.similarity),
                    backgroundColor: `color-mix(in oklch, ${scoreColor(
                      c.similarity,
                    )} 16%, transparent)`,
                  }}
                >
                  {(c.similarity * 100).toFixed(0)}%
                </span>
                <ChevronDown
                  className={cn(
                    "size-4 shrink-0 text-muted-foreground transition-transform",
                    expanded && "rotate-180",
                  )}
                />
              </button>
              {expanded && (
                <div className="px-3 pb-3">
                  <p className="rounded-lg border-l-2 border-[var(--brand-purple)] bg-muted/50 px-3 py-2 text-sm leading-relaxed text-muted-foreground">
                    {c.chunkText}
                  </p>
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
