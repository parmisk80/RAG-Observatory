// Shared domain types modeled after the RAG Observatory API.

export type TaskStatus = "queued" | "processing" | "completed" | "failed"

export interface Citation {
  id: string
  documentId: string
  documentName: string
  chunkText: string
  similarity: number
  page?: number
  section?: string
}

export interface ChatMessage {
  id: string
  role: "user" | "assistant"
  content: string
  createdAt: number
  citations?: Citation[]
  followups?: string[]
  status?: TaskStatus
  streaming?: boolean
}

export interface Conversation {
  id: string
  title: string
  updatedAt: number
  messages: ChatMessage[]
}

export type DocStatus = "queued" | "processing" | "indexed" | "failed"

export interface DocItem {
  id: string
  name: string
  type: string
  sizeKb: number
  chunks: number
  status: DocStatus
  progress: number
  uploadedAt: number
}
