"use client"

import { Sparkles, User } from "lucide-react"
import type { ChatMessage } from "@/lib/types"
import { cn } from "@/lib/utils"
import { SourcesPanel } from "./sources-panel"
import { Button } from "@/components/ui/button"

const statusLabel: Record<string, string> = {
  queued: "Queued…",
  processing: "Retrieving and reasoning…",
}

export function Message({
  message,
  onFollowup,
}: {
  message: ChatMessage
  onFollowup?: (q: string) => void
}) {
  const isUser = message.role === "user"

  if (isUser) {
    return (
      <div className="flex justify-end gap-3">
        <div className="max-w-[80%] rounded-2xl rounded-br-md gradient-brand px-4 py-2.5 text-white shadow-md">
          <p className="whitespace-pre-wrap text-sm leading-relaxed text-pretty">
            {message.content}
          </p>
        </div>
        <div className="flex size-8 shrink-0 items-center justify-center rounded-full bg-secondary text-secondary-foreground">
          <User className="size-4" />
        </div>
      </div>
    )
  }

  return (
    <div className="flex gap-3">
      <div className="flex size-8 shrink-0 items-center justify-center rounded-full gradient-brand text-white shadow-md">
        <Sparkles className="size-4" />
      </div>
      <div className="min-w-0 max-w-[80%] flex-1">
        {message.status && message.status !== "completed" ? (
          <div className="flex items-center gap-2 rounded-2xl rounded-tl-md border border-border/60 bg-card/60 px-4 py-3">
            <span className="flex gap-1">
              <span className="size-2 animate-bounce rounded-full bg-[var(--brand-purple)] [animation-delay:-0.3s]" />
              <span className="size-2 animate-bounce rounded-full bg-[var(--brand-pink)] [animation-delay:-0.15s]" />
              <span className="size-2 animate-bounce rounded-full bg-[var(--brand-cyan)]" />
            </span>
            <span className="text-sm text-muted-foreground">
              {statusLabel[message.status] ?? "Thinking…"}
            </span>
          </div>
        ) : (
          <div className="rounded-2xl rounded-tl-md border border-border/60 bg-card/60 px-4 py-3 shadow-sm">
            <p
              className={cn(
                "whitespace-pre-wrap text-sm leading-relaxed text-foreground/90 text-pretty",
              )}
            >
              {message.content}
              {message.streaming && (
                <span className="ml-0.5 inline-block h-4 w-1.5 translate-y-0.5 animate-blink rounded-sm bg-[var(--brand-purple)]" />
              )}
            </p>
          </div>
        )}

        {message.citations && message.citations.length > 0 && (
          <SourcesPanel citations={message.citations} />
        )}

        {!message.streaming &&
          message.followups &&
          message.followups.length > 0 && (
            <div className="mt-3 flex flex-wrap gap-2">
              {message.followups.map((f) => (
                <Button
                  key={f}
                  variant="outline"
                  size="sm"
                  onClick={() => onFollowup?.(f)}
                  className="h-auto rounded-full border-border/70 bg-card/40 px-3 py-1.5 text-xs font-normal text-muted-foreground hover:border-[var(--brand-purple)] hover:text-foreground"
                >
                  {f}
                </Button>
              ))}
            </div>
          )}
      </div>
    </div>
  )
}
