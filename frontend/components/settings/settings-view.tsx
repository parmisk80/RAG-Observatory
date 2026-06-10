"use client"

import { useState } from "react"
import { toast } from "sonner"
import { PageContainer } from "@/components/page-container"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Switch } from "@/components/ui/switch"

function Row({
  title,
  description,
  children,
}: {
  title: string
  description: string
  children: React.ReactNode
}) {
  return (
    <div className="flex items-center justify-between gap-4 py-4">
      <div className="min-w-0">
        <p className="text-sm font-medium">{title}</p>
        <p className="text-xs text-muted-foreground">{description}</p>
      </div>
      <div className="shrink-0">{children}</div>
    </div>
  )
}

function Section({
  title,
  children,
}: {
  title: string
  children: React.ReactNode
}) {
  return (
    <div className="rounded-2xl border border-border/60 bg-card/60 p-5">
      <h2 className="text-sm font-semibold">{title}</h2>
      <div className="mt-2 divide-y divide-border/50">{children}</div>
    </div>
  )
}

export function SettingsView() {
  const [topK, setTopK] = useState("5")
  const [temperature, setTemperature] = useState("0.2")
  const [model, setModel] = useState("llama3")
  const [streaming, setStreaming] = useState(true)
  const [autoFollowups, setAutoFollowups] = useState(true)
  const [rewrite, setRewrite] = useState(true)

  return (
    <PageContainer
      title="Settings"
      description="Tune how RAG Observatory retrieves and generates answers."
      action={
        <Button
          className="gradient-brand border-0 text-white"
          onClick={() => toast.success("Settings saved")}
        >
          Save changes
        </Button>
      }
    >
      <div className="grid gap-6 lg:grid-cols-2">
        <Section title="Retrieval">
          <Row
            title="Top-K passages"
            description="Number of chunks retrieved per query"
          >
            <Input
              value={topK}
              onChange={(e) => setTopK(e.target.value)}
              className="w-20 bg-background/50 text-center"
              inputMode="numeric"
            />
          </Row>
          <Row
            title="Query rewriting"
            description="Reformulate questions before retrieval"
          >
            <Switch checked={rewrite} onCheckedChange={setRewrite} />
          </Row>
        </Section>

        <Section title="Generation">
          <Row title="Model" description="Ollama model used for answers">
            <Input
              value={model}
              onChange={(e) => setModel(e.target.value)}
              className="w-40 bg-background/50"
            />
          </Row>
          <Row
            title="Temperature"
            description="Higher values increase creativity"
          >
            <Input
              value={temperature}
              onChange={(e) => setTemperature(e.target.value)}
              className="w-20 bg-background/50 text-center"
              inputMode="decimal"
            />
          </Row>
          <Row
            title="Stream responses"
            description="Render answers as they generate"
          >
            <Switch checked={streaming} onCheckedChange={setStreaming} />
          </Row>
          <Row
            title="Suggested follow-ups"
            description="Offer related questions after answers"
          >
            <Switch
              checked={autoFollowups}
              onCheckedChange={setAutoFollowups}
            />
          </Row>
        </Section>

        <Section title="Connection">
          <Row
            title="API base URL"
            description="FastAPI backend endpoint"
          >
            <Input
              defaultValue="https://api.rag-observatory.app"
              className="w-64 bg-background/50"
            />
          </Row>
          <div className="pt-4">
            <Label className="text-xs text-muted-foreground">
              The frontend polls{" "}
              <code className="rounded bg-muted px-1 py-0.5 text-[11px]">
                /api/v1/answer/&#123;task_id&#125;
              </code>{" "}
              until background tasks complete.
            </Label>
          </div>
        </Section>

        <Section title="Appearance">
          <Row
            title="Theme"
            description="Dark mode is optimized for long sessions"
          >
            <span className="rounded-lg bg-accent/60 px-3 py-1.5 text-xs font-medium text-accent-foreground">
              Dark
            </span>
          </Row>
        </Section>
      </div>
    </PageContainer>
  )
}
