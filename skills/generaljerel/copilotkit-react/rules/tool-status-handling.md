---
title: Handle All Tool Call Statuses
impact: HIGH
impactDescription: unhandled statuses cause blank UI or missing loading states
tags: tool, rendering, status, streaming
---

## Handle All Tool Call Statuses

Tool renders receive a `status` field with three possible values: `inProgress`, `executing`, and `complete`. Handle all three to provide proper loading states, execution feedback, and final results. Ignoring statuses causes jarring UI transitions.

**Incorrect (only handles complete, no loading state):**

```tsx
useRenderTool({
  name: "search_results",
  args: z.object({ query: z.string(), results: z.array(z.string()) }),
  render: ({ args }) => {
    return <ResultsList results={args.results} />
  },
})
```

**Correct (handles all three statuses):**

```tsx
useRenderTool({
  name: "search_results",
  args: z.object({ query: z.string(), results: z.array(z.string()) }),
  render: ({ args, status }) => {
    if (status === "inProgress") {
      return <SearchSkeleton query={args.query} />
    }
    if (status === "executing") {
      return <SearchProgress query={args.query} />
    }
    return <ResultsList results={args.results} />
  },
})
```

Reference: [useRenderTool](https://docs.copilotkit.ai/reference/hooks/useRenderTool)
