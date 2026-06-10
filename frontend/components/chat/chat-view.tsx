"use client"

import { useCallback, useEffect, useRef, useState } from "react"
import { Sparkles, FileText, Search, Lightbulb } from "lucide-react"
import { toast } from "sonner"
import type { ChatMessage, Conversation, DocItem } from "@/lib/types"
import { askQuestion, pollAnswer, uploadDocument } from "@/lib/api"
import { useStore } from "@/lib/store"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Message } from "./message"
import { Composer } from "./composer"

const SUGGESTIONS = [
  {
    icon: Search,
    title: "Explain a concept",
    prompt: "How does retrieval-augmented generation work end to end?",
  },
  {
    icon: FileText,
    title: "Summarize a source",
    prompt: "Summarize the key ideas from my indexed documents.",
  },
  {
    icon: Lightbulb,
    title: "Compare approaches",
    prompt: "What are the trade-offs of vector search vs keyword search?",
  },
]

function uid() {
  return Math.random().toString(36).slice(2, 11)
}

export function ChatView() {
  const { upsertConversation, setDocuments } = useStore()
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState("")
  const [busy, setBusy] = useState(false)
  const convoId = useRef<string>(`conv_${uid()}`)
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    scrollRef.current?.scrollTo({
      top: scrollRef.current.scrollHeight,
      behavior: "smooth",
    })
  }, [messages])

  // Persist the conversation into the shared store whenever messages change.
  // Done in an effect so we never call setState on the store during render.
  useEffect(() => {
    if (messages.length === 0) return
    const firstUser = messages.find((m) => m.role === "user")
    const convo: Conversation = {
      id: convoId.current,
      title: firstUser?.content.slice(0, 48) ?? "New chat",
      updatedAt: Date.now(),
      messages,
    }
    upsertConversation(convo)
  }, [messages, upsertConversation])

  const send = useCallback(
    async (text: string) => {
      if (busy) return
      setInput("")
      setBusy(true)

      const userMsg: ChatMessage = {
        id: uid(),
        role: "user",
        content: text,
        createdAt: Date.now(),
      }
      const assistantId = uid()
      const pending: ChatMessage = {
        id: assistantId,
        role: "assistant",
        content: "",
        createdAt: Date.now(),
        status: "queued",
      }

      setMessages((prev) => [...prev, userMsg, pending])

      try {
        // 1. Kick off the async task (returns task_id + queued status)
        const { task_id } = await askQuestion(text)

        // 2. Poll until the Celery worker finishes
        const result = await pollAnswer(task_id, (status) => {
          setMessages((prev) =>
            prev.map((m) =>
              m.id === assistantId
                ? { ...m, status: status as ChatMessage["status"] }
                : m,
            ),
          )
        })

        // 3. Stream the completed answer into the UI
        const full = result.answer
        for (let i = 1; i <= full.length; i += 3) {
          await new Promise((r) => setTimeout(r, 12))
          setMessages((prev) =>
            prev.map((m) =>
              m.id === assistantId
                ? {
                    ...m,
                    status: "completed",
                    streaming: true,
                    content: full.slice(0, i),
                  }
                : m,
            ),
          )
        }

        setMessages((prev) =>
          prev.map((m) =>
            m.id === assistantId
              ? {
                  ...m,
                  status: "completed" as const,
                  streaming: false,
                  content: full,
                  citations: result.citations,
                  followups: result.followups,
                }
              : m,
          ),
        )
      } catch {
        toast.error("Something went wrong while answering. Please try again.")
        setMessages((prev) =>
          prev.map((m) =>
            m.id === assistantId
              ? {
                  ...m,
                  status: "completed",
                  content:
                    "I couldn't complete that request. Please try again.",
                }
              : m,
          ),
        )
      } finally {
        setBusy(false)
      }
    },
    [busy],
  )

  const handleAttach = useCallback(
    async (files: FileList) => {
      for (const file of Array.from(files)) {
        const { doc } = await uploadDocument(file)
        setDocuments((prev) => [doc, ...prev])
        toast.success(`Uploading "${doc.name}"`, {
          description: "Processing in the background…",
        })
        // Simulate async ingestion progress.
        simulateIngestion(doc, setDocuments)
      }
    },
    [setDocuments],
  )

  const empty = messages.length === 0

  return (
    <div className="flex h-full flex-col">
      <ScrollArea className="flex-1">
        <div ref={scrollRef} className="h-full">
          {empty ? (
            <div className="mx-auto flex min-h-[60vh] w-full max-w-3xl flex-col items-center justify-center px-4 py-10 text-center">
              <div className="mb-5 flex size-16 items-center justify-center rounded-2xl gradient-brand text-white shadow-xl">
                <Sparkles className="size-8" />
              </div>
              <h1 className="text-balance text-3xl font-semibold tracking-tight sm:text-4xl">
                Ask your <span className="gradient-text">knowledge base</span>
              </h1>
              <p className="mt-3 max-w-md text-pretty text-sm leading-relaxed text-muted-foreground">
                Upload documents and ask anything. RAG Observatory retrieves the
                most relevant passages and answers with verifiable sources.
              </p>
              <div className="mt-8 grid w-full gap-3 sm:grid-cols-3">
                {SUGGESTIONS.map((s) => (
                  <button
                    key={s.title}
                    onClick={() => send(s.prompt)}
                    className="group flex flex-col gap-2 rounded-xl border border-border/60 bg-card/50 p-4 text-left transition-all hover:border-[var(--brand-purple)] hover:bg-card"
                  >
                    <s.icon className="size-5 text-[var(--brand-purple)]" />
                    <span className="text-sm font-medium">{s.title}</span>
                    <span className="text-xs leading-relaxed text-muted-foreground">
                      {s.prompt}
                    </span>
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div className="mx-auto flex w-full max-w-3xl flex-col gap-6 px-4 py-8">
              {messages.map((m) => (
                <Message key={m.id} message={m} onFollowup={send} />
              ))}
            </div>
          )}
        </div>
      </ScrollArea>
      <Composer
        value={input}
        onChange={setInput}
        onSend={send}
        onAttach={handleAttach}
        disabled={busy}
      />
    </div>
  )
}

function simulateIngestion(
  doc: DocItem,
  setDocuments: React.Dispatch<React.SetStateAction<DocItem[]>>,
) {
  let progress = 0
  const total = Math.max(24, Math.round(doc.sizeKb / 8))
  const tick = setInterval(() => {
    progress += Math.random() * 22 + 8
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
  }, 700)
}
