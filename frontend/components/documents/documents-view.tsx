"use client"

import { useCallback, useRef, useState } from "react"
import {
  UploadCloud,
  FileText,
  FileType,
  FileCode,
  CheckCircle2,
  Loader2,
  Trash2,
} from "lucide-react"
import { toast } from "sonner"
import { useStore } from "@/lib/store"
import { uploadDocument } from "@/lib/api"
import type { DocItem } from "@/lib/types"
import { PageContainer } from "@/components/page-container"
import { Progress } from "@/components/ui/progress"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

function iconFor(type: string) {
  if (type === "PDF") return FileText
  if (type === "MD") return FileCode
  return FileType
}

function timeAgo(ts: number) {
  const m = Math.floor((Date.now() - ts) / 60000)
  if (m < 1) return "just now"
  if (m < 60) return `${m}m ago`
  const h = Math.floor(m / 60)
  if (h < 24) return `${h}h ago`
  return `${Math.floor(h / 24)}d ago`
}

function fmtSize(kb: number) {
  return kb >= 1024 ? `${(kb / 1024).toFixed(1)} MB` : `${kb} KB`
}

function simulateIngestion(
  doc: DocItem,
  setDocuments: React.Dispatch<React.SetStateAction<DocItem[]>>,
) {
  let progress = 0
  const total = Math.max(24, Math.round(doc.sizeKb / 8))
  const tick = setInterval(() => {
    progress += Math.random() * 20 + 8
    const p = Math.min(100, Math.round(progress))
    setDocuments((prev) =>
      prev.map((d) =>
        d.id === doc.id
          ? {
              ...d,
              progress: p,
              status: p >= 100 ? "indexed" : "processing",
              chunks: Math.round((p / 100) * total),
            }
          : d,
      ),
    )
    if (p >= 100) {
      clearInterval(tick)
      toast.success(`"${doc.name}" indexed`, {
        description: `${total} chunks embedded and ready to query.`,
      })
    }
  }, 650)
}

export function DocumentsView() {
  const { documents, setDocuments } = useStore()
  const [dragging, setDragging] = useState(false)
  const fileRef = useRef<HTMLInputElement>(null)

  const ingest = useCallback(
    async (files: FileList | File[]) => {
      for (const file of Array.from(files)) {
        const { doc } = await uploadDocument(file)
        setDocuments((prev) => [doc, ...prev])
        simulateIngestion(doc, setDocuments)
      }
    },
    [setDocuments],
  )

  const indexed = documents.filter((d) => d.status === "indexed").length
  const processing = documents.filter(
    (d) => d.status === "processing" || d.status === "queued",
  ).length
  const totalChunks = documents.reduce((a, d) => a + d.chunks, 0)

  return (
    <PageContainer
      title="Documents"
      description="Your knowledge base. Upload files and they are chunked, embedded, and indexed automatically in the background."
    >
      <div className="mb-6 grid gap-3 sm:grid-cols-3">
        <Stat label="Indexed" value={indexed} accent="var(--success)" />
        <Stat label="Processing" value={processing} accent="var(--warning)" />
        <Stat
          label="Total chunks"
          value={totalChunks.toLocaleString()}
          accent="var(--brand-cyan)"
        />
      </div>

      <input
        ref={fileRef}
        type="file"
        multiple
        accept=".pdf,.txt,.docx,.md"
        className="hidden"
        onChange={(e) => {
          if (e.target.files?.length) ingest(e.target.files)
          e.target.value = ""
        }}
      />

      <div
        onDragOver={(e) => {
          e.preventDefault()
          setDragging(true)
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => {
          e.preventDefault()
          setDragging(false)
          if (e.dataTransfer.files?.length) ingest(e.dataTransfer.files)
        }}
        onClick={() => fileRef.current?.click()}
        className={cn(
          "flex cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed px-6 py-12 text-center transition-all",
          dragging
            ? "border-[var(--brand-purple)] bg-accent/40 glow-purple"
            : "border-border/70 bg-card/40 hover:border-[var(--brand-purple)]/60 hover:bg-card/70",
        )}
      >
        <div className="mb-4 flex size-14 items-center justify-center rounded-2xl gradient-brand text-white shadow-lg">
          <UploadCloud className="size-7" />
        </div>
        <p className="text-base font-medium">
          Drag & drop files, or click to browse
        </p>
        <p className="mt-1 text-sm text-muted-foreground">
          Supports PDF, TXT, DOCX, and Markdown
        </p>
      </div>

      <div className="mt-8">
        <h2 className="mb-3 text-sm font-semibold uppercase tracking-wider text-muted-foreground">
          Recent documents
        </h2>
        <div className="flex flex-col gap-2">
          {documents.length === 0 && (
            <p className="rounded-xl border border-border/60 bg-card/40 p-6 text-center text-sm text-muted-foreground">
              No documents yet. Upload one to get started.
            </p>
          )}
          {documents.map((d) => {
            const Icon = iconFor(d.type)
            const active = d.status === "processing" || d.status === "queued"
            return (
              <div
                key={d.id}
                className="flex items-center gap-4 rounded-xl border border-border/60 bg-card/50 p-4"
              >
                <div className="flex size-11 shrink-0 items-center justify-center rounded-xl bg-accent/60 text-[var(--brand-purple)]">
                  <Icon className="size-5" />
                </div>
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2">
                    <p className="truncate text-sm font-medium">{d.name}</p>
                    <span className="rounded-md bg-muted px-1.5 py-0.5 text-[10px] font-semibold text-muted-foreground">
                      {d.type}
                    </span>
                  </div>
                  <p className="mt-0.5 text-xs text-muted-foreground">
                    {fmtSize(d.sizeKb)} · {d.chunks} chunks ·{" "}
                    {timeAgo(d.uploadedAt)}
                  </p>
                  {active && (
                    <Progress value={d.progress} className="mt-2 h-1.5" />
                  )}
                </div>
                <div className="flex shrink-0 items-center gap-3">
                  {active ? (
                    <span className="flex items-center gap-1.5 text-xs font-medium text-[var(--warning)]">
                      <Loader2 className="size-3.5 animate-spin" />
                      {d.status === "queued" ? "Queued" : `${d.progress}%`}
                    </span>
                  ) : (
                    <span className="flex items-center gap-1.5 text-xs font-medium text-[var(--success)]">
                      <CheckCircle2 className="size-3.5" />
                      Indexed
                    </span>
                  )}
                  <Button
                    variant="ghost"
                    size="icon"
                    className="size-8 text-muted-foreground hover:text-destructive"
                    onClick={() =>
                      setDocuments((prev) =>
                        prev.filter((x) => x.id !== d.id),
                      )
                    }
                    aria-label={`Delete ${d.name}`}
                  >
                    <Trash2 className="size-4" />
                  </Button>
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </PageContainer>
  )
}

function Stat({
  label,
  value,
  accent,
}: {
  label: string
  value: string | number
  accent: string
}) {
  return (
    <div className="rounded-xl border border-border/60 bg-card/50 p-4">
      <div className="flex items-center gap-2">
        <span
          className="size-2 rounded-full"
          style={{ backgroundColor: accent }}
        />
        <p className="text-xs font-medium text-muted-foreground">{label}</p>
      </div>
      <p className="mt-1 text-2xl font-semibold tabular-nums">{value}</p>
    </div>
  )
}
