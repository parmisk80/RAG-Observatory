"use client"

import {
  createContext,
  useContext,
  useState,
  useCallback,
  type ReactNode,
} from "react"
import type { Conversation, DocItem } from "./types"

interface Store {
  conversations: Conversation[]
  documents: DocItem[]
  setConversations: React.Dispatch<React.SetStateAction<Conversation[]>>
  setDocuments: React.Dispatch<React.SetStateAction<DocItem[]>>
  upsertConversation: (c: Conversation) => void
  removeConversation: (id: string) => void
}

const StoreContext = createContext<Store | null>(null)

const seedDocs: DocItem[] = [
  {
    id: "doc-seed-1",
    name: "RAG Architecture Guide.md",
    type: "MD",
    sizeKb: 84,
    chunks: 42,
    status: "indexed",
    progress: 100,
    uploadedAt: Date.now() - 1000 * 60 * 60 * 26,
  },
  {
    id: "doc-seed-2",
    name: "Vector Search Primer.pdf",
    type: "PDF",
    sizeKb: 1280,
    chunks: 188,
    status: "indexed",
    progress: 100,
    uploadedAt: Date.now() - 1000 * 60 * 60 * 5,
  },
  {
    id: "doc-seed-3",
    name: "Operations Handbook.docx",
    type: "DOCX",
    sizeKb: 642,
    chunks: 96,
    status: "indexed",
    progress: 100,
    uploadedAt: Date.now() - 1000 * 60 * 48,
  },
]

export function StoreProvider({ children }: { children: ReactNode }) {
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [documents, setDocuments] = useState<DocItem[]>(seedDocs)

  const upsertConversation = useCallback((c: Conversation) => {
    setConversations((prev) => {
      const idx = prev.findIndex((p) => p.id === c.id)
      if (idx === -1) return [c, ...prev]
      const next = [...prev]
      next[idx] = c
      return next.sort((a, b) => b.updatedAt - a.updatedAt)
    })
  }, [])

  const removeConversation = useCallback((id: string) => {
    setConversations((prev) => prev.filter((c) => c.id !== id))
  }, [])

  return (
    <StoreContext.Provider
      value={{
        conversations,
        documents,
        setConversations,
        setDocuments,
        upsertConversation,
        removeConversation,
      }}
    >
      {children}
    </StoreContext.Provider>
  )
}

export function useStore() {
  const ctx = useContext(StoreContext)
  if (!ctx) throw new Error("useStore must be used within StoreProvider")
  return ctx
}
