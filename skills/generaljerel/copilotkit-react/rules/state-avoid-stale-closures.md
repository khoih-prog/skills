---
title: Avoid Stale Closures in Tool Handlers
impact: HIGH
impactDescription: stale closures cause tools to operate on outdated state
tags: state, closures, handlers, useFrontendTool
---

## Avoid Stale Closures in Tool Handlers

Tool handlers registered with `useFrontendTool` capture variables from their closure. If state changes between registration and invocation, the handler sees stale values. Use functional state updates or refs to always access current state.

**Incorrect (stale closure captures initial items):**

```tsx
function TodoPanel() {
  const [items, setItems] = useState<string[]>([])

  useFrontendTool({
    name: "add_todo",
    handler: async ({ title }) => {
      setItems([...items, title])
    },
  })

  return <TodoList items={items} />
}
```

**Correct (functional update always uses current state):**

```tsx
function TodoPanel() {
  const [items, setItems] = useState<string[]>([])

  useFrontendTool({
    name: "add_todo",
    handler: async ({ title }) => {
      setItems(prev => [...prev, title])
    },
  })

  return <TodoList items={items} />
}
```

Reference: [useFrontendTool](https://docs.copilotkit.ai/reference/hooks/useFrontendTool)
