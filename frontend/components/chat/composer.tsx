"use client"

import { useRef, useState, type FormEvent } from "react"
import { ArrowUp, Paperclip } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"

export function Composer({
  onSend,
  onAttach,
  disabled,
  value,
  onChange,
}: {
  onSend: (text: string) => void
  onAttach?: (files: FileList) => void
  disabled?: boolean
  value: string
  onChange: (v: string) => void
}) {
  const fileRef = useRef<HTMLInputElement>(null)
  const [focused, setFocused] = useState(false)

  function submit(e: FormEvent) {
    e.preventDefault()
    const text = value.trim()
    if (!text || disabled) return
    onSend(text)
  }

  return (
    <form onSubmit={submit} className="mx-auto w-full max-w-3xl px-4 pb-4">
      <div
        className={`flex items-end gap-2 rounded-2xl border bg-card/70 p-2 shadow-lg backdrop-blur transition-all ${
          focused
            ? "border-[var(--brand-purple)] glow-purple"
            : "border-border/70"
        }`}
      >
        <input
          ref={fileRef}
          type="file"
          multiple
          accept=".pdf,.txt,.docx,.md"
          className="hidden"
          onChange={(e) => {
            if (e.target.files?.length) onAttach?.(e.target.files)
            e.target.value = ""
          }}
        />
        <Button
          type="button"
          variant="ghost"
          size="icon"
          className="size-9 shrink-0 rounded-xl text-muted-foreground"
          onClick={() => fileRef.current?.click()}
          aria-label="Attach document"
        >
          <Paperclip className="size-5" />
        </Button>
        <Textarea
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onFocus={() => setFocused(true)}
          onBlur={() => setFocused(false)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault()
              submit(e)
            }
          }}
          rows={1}
          placeholder="Ask anything about your documents…"
          className="max-h-40 min-h-9 flex-1 resize-none border-0 bg-transparent px-1 py-1.5 text-sm shadow-none focus-visible:ring-0"
        />
        <Button
          type="submit"
          size="icon"
          disabled={disabled || !value.trim()}
          className="size-9 shrink-0 rounded-xl gradient-brand border-0 text-white shadow-md hover:opacity-90 disabled:opacity-40"
          aria-label="Send message"
        >
          <ArrowUp className="size-5" />
        </Button>
      </div>
      <p className="mt-2 text-center text-[11px] text-muted-foreground/70">
        Answers are grounded in your indexed knowledge base. Attach PDF, TXT,
        DOCX, or Markdown.
      </p>
    </form>
  )
}
