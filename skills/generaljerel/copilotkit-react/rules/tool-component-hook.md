---
title: Prefer useComponent for Simple Rendering
impact: MEDIUM
impactDescription: reduces boilerplate for common component-rendering patterns
tags: tool, rendering, useComponent, simplification
---

## Prefer useComponent for Simple Rendering

When a tool call simply renders a React component from its arguments with no special status handling, use `useComponent` instead of `useRenderTool`. It provides a simpler API that maps tool args directly to component props.

**Incorrect (verbose useRenderTool for simple case):**

```tsx
useRenderTool({
  name: "show_user_card",
  args: z.object({
    name: z.string(),
    email: z.string(),
    avatar: z.string(),
  }),
  render: ({ args, status }) => {
    if (status !== "complete") return <UserCardSkeleton />
    return <UserCard name={args.name} email={args.email} avatar={args.avatar} />
  },
})
```

**Correct (useComponent for direct mapping):**

```tsx
useComponent({
  name: "show_user_card",
  component: UserCard,
  args: z.object({
    name: z.string(),
    email: z.string(),
    avatar: z.string(),
  }),
})
```

`useComponent` automatically handles loading states and maps args to component props.

Reference: [useComponent](https://docs.copilotkit.ai/reference/hooks/useComponent)
