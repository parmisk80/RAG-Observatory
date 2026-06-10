"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { useState } from "react"
import {
  MessageSquarePlus,
  Sparkles,
  FileText,
  LayoutDashboard,
  Activity,
  HeartPulse,
  Settings,
  Menu,
  X,
} from "lucide-react"
import { cn } from "@/lib/utils"
import { StoreProvider, useStore } from "@/lib/store"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"

const nav = [
  { href: "/", label: "Chat", icon: Sparkles },
  { href: "/documents", label: "Documents", icon: FileText },
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/monitoring", label: "Monitoring", icon: Activity },
  { href: "/health", label: "Health Center", icon: HeartPulse },
  { href: "/settings", label: "Settings", icon: Settings },
]

function timeAgo(ts: number) {
  const m = Math.floor((Date.now() - ts) / 60000)
  if (m < 1) return "just now"
  if (m < 60) return `${m}m ago`
  const h = Math.floor(m / 60)
  if (h < 24) return `${h}h ago`
  return `${Math.floor(h / 24)}d ago`
}

function SidebarContent({ onNavigate }: { onNavigate?: () => void }) {
  const pathname = usePathname()
  const { conversations } = useStore()

  return (
    <div className="flex h-full flex-col gap-4 p-3">
      <div className="flex items-center gap-2.5 px-2 pt-2">
        <div className="flex size-9 items-center justify-center rounded-xl gradient-brand text-white shadow-lg">
          <Sparkles className="size-5" />
        </div>
        <div className="leading-tight">
          <p className="text-sm font-semibold tracking-tight">RAG Observatory</p>
          <p className="text-[11px] text-muted-foreground">Knowledge Assistant</p>
        </div>
      </div>

      <Link href="/" onClick={onNavigate}>
        <Button className="w-full justify-start gap-2 gradient-brand border-0 text-white shadow-md hover:opacity-90">
          <MessageSquarePlus className="size-4" />
          New Chat
        </Button>
      </Link>

      <nav className="flex flex-col gap-1">
        {nav.map((item) => {
          const active =
            item.href === "/"
              ? pathname === "/"
              : pathname.startsWith(item.href)
          return (
            <Link key={item.href} href={item.href} onClick={onNavigate}>
              <span
                className={cn(
                  "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                  active
                    ? "bg-sidebar-accent text-sidebar-accent-foreground"
                    : "text-muted-foreground hover:bg-sidebar-accent/60 hover:text-foreground",
                )}
              >
                <item.icon className="size-4" />
                {item.label}
              </span>
            </Link>
          )
        })}
      </nav>

      <div className="flex min-h-0 flex-1 flex-col">
        <p className="px-3 pb-2 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
          Conversations
        </p>
        <ScrollArea className="flex-1">
          <div className="flex flex-col gap-0.5 pr-2">
            {conversations.length === 0 && (
              <p className="px-3 py-2 text-xs text-muted-foreground/70">
                Your chats will appear here.
              </p>
            )}
            {conversations.map((c) => (
              <Link key={c.id} href={`/?c=${c.id}`} onClick={onNavigate}>
                <span className="block truncate rounded-lg px-3 py-2 text-sm text-muted-foreground transition-colors hover:bg-sidebar-accent/60 hover:text-foreground">
                  {c.title}
                  <span className="block text-[10px] text-muted-foreground/60">
                    {timeAgo(c.updatedAt)}
                  </span>
                </span>
              </Link>
            ))}
          </div>
        </ScrollArea>
      </div>

      <div className="rounded-xl border border-border/60 bg-card/50 p-3">
        <div className="flex items-center gap-2">
          <span className="size-2 rounded-full bg-[var(--success)] shadow-[0_0_8px_var(--success)]" />
          <p className="text-xs font-medium">All systems operational</p>
        </div>
        <p className="mt-1 text-[11px] text-muted-foreground">
          Redis · ChromaDB · Ollama online
        </p>
      </div>
    </div>
  )
}

function Shell({ children }: { children: React.ReactNode }) {
  const [open, setOpen] = useState(false)
  return (
    <div className="flex h-dvh w-full overflow-hidden bg-background">
      {/* Desktop sidebar */}
      <aside className="hidden w-72 shrink-0 border-r border-border/60 bg-sidebar md:block">
        <SidebarContent />
      </aside>

      {/* Mobile sidebar */}
      {open && (
        <div className="fixed inset-0 z-50 md:hidden">
          <div
            className="absolute inset-0 bg-black/50 backdrop-blur-sm"
            onClick={() => setOpen(false)}
          />
          <aside className="absolute left-0 top-0 h-full w-72 border-r border-border/60 bg-sidebar">
            <div className="flex justify-end p-2">
              <Button variant="ghost" size="icon" onClick={() => setOpen(false)}>
                <X className="size-5" />
              </Button>
            </div>
            <SidebarContent onNavigate={() => setOpen(false)} />
          </aside>
        </div>
      )}

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="flex h-14 shrink-0 items-center gap-2 border-b border-border/60 px-4 md:hidden">
          <Button variant="ghost" size="icon" onClick={() => setOpen(true)}>
            <Menu className="size-5" />
          </Button>
          <span className="flex items-center gap-2 font-semibold">
            <span className="flex size-7 items-center justify-center rounded-lg gradient-brand text-white">
              <Sparkles className="size-4" />
            </span>
            RAG Observatory
          </span>
        </header>
        <main className="min-h-0 flex-1 overflow-hidden">{children}</main>
      </div>
    </div>
  )
}

export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <StoreProvider>
      <Shell>{children}</Shell>
    </StoreProvider>
  )
}
