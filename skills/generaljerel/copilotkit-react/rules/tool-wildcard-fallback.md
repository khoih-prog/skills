---
title: Register Wildcard Renderer as Fallback
impact: MEDIUM
impactDescription: prevents missing UI when agent calls unregistered tools
tags: tool, rendering, wildcard, fallback
---

## Register Wildcard Renderer as Fallback

Register a wildcard `"*"` renderer with `useRenderTool` to catch tool calls that don't have a dedicated renderer. Without a fallback, unregistered tool calls render nothing in the chat, confusing users.

**Incorrect (no fallback, unknown tools render blank):**

```tsx
useRenderTool({
  name: "show_chart",
  render: ({ args }) => <Chart data={args.data} />,
})
```

**Correct (wildcard fallback for unknown tools):**

```tsx
useRenderTool({
  name: "show_chart",
  render: ({ args }) => <Chart data={args.data} />,
})

useRenderTool({
  name: "*",
  render: ({ name, args, status }) => (
    <GenericToolCard
      toolName={name}
      args={args}
      isLoading={status === "inProgress"}
    />
  ),
})
```

Reference: [useRenderTool](https://docs.copilotkit.ai/reference/hooks/useRenderTool)
