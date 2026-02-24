---
title: useRenderTool for Display, useFrontendTool for Effects
impact: HIGH
impactDescription: mixing concerns causes side effects during streaming or double execution
tags: tool, rendering, useFrontendTool, useRenderTool, separation
---

## useRenderTool for Display, useFrontendTool for Effects

Use `useRenderTool` when you only need to display UI in response to a tool call. Use `useFrontendTool` when the tool call should trigger side effects (API calls, state mutations, navigation). Mixing them causes side effects to fire during streaming or display-only tools to swallow return values.

**Incorrect (side effects in a render tool):**

```tsx
useRenderTool({
  name: "create_ticket",
  render: ({ args, status }) => {
    if (status === "complete") {
      createTicketInDb(args)
    }
    return <TicketCard {...args} />
  },
})
```

**Correct (separate render from effects):**

```tsx
useFrontendTool({
  name: "create_ticket",
  handler: async ({ title, priority }) => {
    const ticket = await createTicketInDb({ title, priority })
    return { ticketId: ticket.id }
  },
})

useRenderTool({
  name: "create_ticket",
  render: ({ args, status }) => {
    if (status === "inProgress") return <TicketSkeleton />
    return <TicketCard title={args.title} priority={args.priority} />
  },
})
```

Reference: [useFrontendTool](https://docs.copilotkit.ai/reference/hooks/useFrontendTool)
