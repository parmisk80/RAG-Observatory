import type { ReactNode } from "react"
import { ScrollArea } from "@/components/ui/scroll-area"

export function PageContainer({
  title,
  description,
  action,
  children,
}: {
  title: string
  description?: string
  action?: ReactNode
  children: ReactNode
}) {
  return (
    <ScrollArea className="h-full">
      <div className="mx-auto w-full max-w-6xl px-5 py-8 sm:px-8">
        <div className="mb-8 flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <h1 className="text-balance text-2xl font-semibold tracking-tight sm:text-3xl">
              {title}
            </h1>
            {description && (
              <p className="mt-1.5 max-w-2xl text-pretty text-sm leading-relaxed text-muted-foreground">
                {description}
              </p>
            )}
          </div>
          {action}
        </div>
        {children}
      </div>
    </ScrollArea>
  )
}
