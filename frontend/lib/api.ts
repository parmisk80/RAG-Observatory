import type { Citation, DocItem } from "./types"

// ---------------------------------------------------------------------------
// RAG Observatory — frontend API client
//
// USE_MOCK = true  →  داده‌های fake برای توسعه بدون بکند
// USE_MOCK = false →  وصل به FastAPI واقعی
//
// آدرس بکند رو توی .env.local بذار:
// NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
// ---------------------------------------------------------------------------

const USE_MOCK = false
const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://172.20.10.7:8080"
const API_BASE_PREFIX = "api/v1"

// ── Types ──────────────────────────────────────────────────────────────────

export interface AnswerResult {
  status: "completed" | "failed"
  answer: string
  citations: Citation[]
  followups: string[]
}

// ── Mock Data (فقط وقتی USE_MOCK = true) ─────────────────────────────────

const KNOWLEDGE: { name: string; section: string; text: string }[] = [
  {
    name: "Vector Search Primer.pdf",
    section: "Embeddings",
    text: "Embeddings map text into a high-dimensional vector space where semantic similarity corresponds to geometric proximity. Nearest-neighbor search over these vectors lets the system retrieve passages by meaning rather than keyword overlap.",
  },
  {
    name: "Vector Search Primer.pdf",
    section: "Chunking",
    text: "Documents are split into overlapping chunks of roughly 500 tokens. Overlap preserves context across boundaries so that an answer is never truncated mid-thought during retrieval.",
  },
  {
    name: "RAG Architecture Guide.md",
    section: "Pipeline",
    text: "A retrieval-augmented generation pipeline rewrites the user query, retrieves the most relevant chunks from the vector store, grounds the language model on those chunks, and finally evaluates the answer for faithfulness before returning it.",
  },
  {
    name: "RAG Architecture Guide.md",
    section: "Evaluation",
    text: "Faithfulness scoring compares each generated claim against the retrieved context. Answers that introduce unsupported statements are penalized, which keeps hallucination rates low and citations trustworthy.",
  },
  {
    name: "Operations Handbook.docx",
    section: "Scaling",
    text: "Background ingestion is handled by Celery workers backed by Redis. This decouples heavy embedding work from the request path, so uploading a large corpus never blocks the chat experience.",
  },
]

function pickCitations(query: string): Citation[] {
  const q = query.toLowerCase()
  const scored = KNOWLEDGE.map((k, i) => {
    const words = q.split(/\s+/).filter(Boolean)
    const hits = words.filter((w) => k.text.toLowerCase().includes(w)).length
    const base = 0.62 + Math.min(hits * 0.07, 0.3)
    return {
      id: `cite-${i}`,
      documentId: `doc-${i}`,
      documentName: k.name,
      chunkText: k.text,
      section: k.section,
      page: ((i * 7) % 24) + 1,
      similarity: Math.min(0.98, base + (Math.random() * 0.04 - 0.02)),
    }
  })
  return scored.sort((a, b) => b.similarity - a.similarity).slice(0, 3)
}

function synthesize(query: string, citations: Citation[]): string {
  const lead = citations[0]?.chunkText ?? ""
  return `Based on your indexed knowledge base, here is what I found regarding "${query.trim()}".\n\n${lead}\n\nIn short, the retrieved sources agree on the core idea and provide grounded, verifiable detail. Expand the sources below to inspect the exact passages and their similarity scores.`
}

const tasks = new Map<string, { startedAt: number; query: string }>()

// ── Helper: تبدیل contexts بکند به Citation فرانت ─────────────────────────

function mapContextsToCitations(contexts: any[]): Citation[] {
  return contexts.slice(0, 3).map((c: any, i: number) => ({
    id:           `cite-${i}`,
    documentId:   c.id         ?? `doc-${i}`,
    documentName: c.source     ?? "unknown",
    chunkText:    c.text       ?? "",
    similarity:   c.score      ?? 0,
    section:      String(c.metadata?.chunk_index ?? ""),
    page:         c.metadata?.page ?? undefined,
  }))
}

// ── askQuestion ────────────────────────────────────────────────────────────

export async function askQuestion(
  question: string,
): Promise<{ task_id: string; status: string }> {

  if (!USE_MOCK) {
    const res = await fetch(`${API_BASE}/${API_BASE_PREFIX}/ask`, {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify({ "user_id": "123",
      "question": question,
      "conversation_id": "123" }),
    })
    if (!res.ok) throw new Error(`askQuestion failed: ${res.status}`)
    return res.json()
  }

  // Mock
  const task_id = `task_${Math.random().toString(36).slice(2, 11)}`
  tasks.set(task_id, { startedAt: Date.now(), query: question })
  return { task_id, status: "queued" }
}

// ── getAnswer ──────────────────────────────────────────────────────────────

export async function getAnswer(
  taskId: string,
): Promise<{ status: string; result?: AnswerResult }> {

  if (!USE_MOCK) {
    const res = await fetch(`${API_BASE}/${API_BASE_PREFIX}/answer/${taskId}`)
    if (!res.ok) throw new Error(`getAnswer failed: ${res.status}`)

    const data = await res.json()

    // وقتی task تموم شد، result رو به فرمت فرانت تبدیل کن
    if (data.status === "completed" && data.result) {
      const r = data.result
      return {
        status: "completed",
        result: {
          status:    "completed",
          answer:    r.answer    ?? "",
          citations: mapContextsToCitations(r.contexts ?? []),
          followups: r.followups ?? [],
        },
      }
    }

    // وقتی هنوز در حال پردازشه
    if (data.status === "failed") {
      return { status: "failed" }
    }

    return { status: data.status }
  }

  // Mock
  const t = tasks.get(taskId)
  if (!t) return { status: "failed" }
  const elapsed = Date.now() - t.startedAt
  if (elapsed < 1400) return { status: elapsed < 600 ? "queued" : "processing" }
  const citations = pickCitations(t.query)
  tasks.delete(taskId)
  return {
    status: "completed",
    result: {
      status:    "completed",
      answer:    synthesize(t.query, citations),
      citations,
      followups: [
        "How does this compare to a keyword-only approach?",
        "What are the trade-offs to consider?",
        "Can you summarize the key takeaways from the sources?",
      ],
    },
  }
}

// ── pollAnswer ─────────────────────────────────────────────────────────────

export async function pollAnswer(
  taskId: string,
  onStatus?: (s: string) => void,
): Promise<AnswerResult> {
  for (let i = 0; i < 60; i++) {
    const res = await getAnswer(taskId)
    onStatus?.(res.status)
    if (res.status === "completed" && res.result) return res.result
    if (res.status === "failed") throw new Error("Task failed")
    await new Promise((r) => setTimeout(r, 500))
  }
  throw new Error("Timed out")
}

// ── uploadDocument ─────────────────────────────────────────────────────────

export async function uploadDocument(
  file: File,
): Promise<{ task_id: string; doc: DocItem }> {

  if (!USE_MOCK) {
    const form = new FormData()
    form.append("file", file)

    const res = await fetch(`${API_BASE}/${API_BASE_PREFIX}/documents/upload`, {
      method: "POST",
      body:   form,
    })
    if (!res.ok) throw new Error(`uploadDocument failed: ${res.status}`)

    const data = await res.json()

    // جواب بکند رو به DocItem تبدیل کن
    const doc: DocItem = data.doc ?? {
      id:         data.document_id,
      name:       data.filename   ?? file.name,
      type:       file.name.split(".").pop()?.toUpperCase() ?? "FILE",
      sizeKb:     Math.max(1, Math.round(file.size / 1024)),
      chunks:     0,
      status:     "queued",
      progress:   0,
      uploadedAt: Date.now(),
    }

    return { task_id: data.task_id, doc }
  }

  // Mock
  const doc: DocItem = {
    id:         `doc_${Math.random().toString(36).slice(2, 9)}`,
    name:       file.name,
    type:       file.name.split(".").pop()?.toUpperCase() ?? "FILE",
    sizeKb:     Math.max(1, Math.round(file.size / 1024)),
    chunks:     0,
    status:     "queued",
    progress:   0,
    uploadedAt: Date.now(),
  }
  return { task_id: `task_${Math.random().toString(36).slice(2, 9)}`, doc }
}

// ── getHealth ──────────────────────────────────────────────────────────────

export async function getHealth(): Promise<Record<string, any>> {
  if (!USE_MOCK) {
    const res = await fetch(`${API_BASE}/health`)
    if (!res.ok) throw new Error(`getHealth failed: ${res.status}`)
    return res.json()
  }
  return { overall: "healthy" }
}

// ── getMetrics ─────────────────────────────────────────────────────────────

export async function getMetrics(): Promise<Record<string, any>> {
  if (!USE_MOCK) {
    const res = await fetch(`${API_BASE}/metrics/`)
    if (!res.ok) throw new Error(`getMetrics failed: ${res.status}`)
    return res.json()
  }
  return {}
}
