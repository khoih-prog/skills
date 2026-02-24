---
title: Register Tools via Hooks Inside Provider
impact: MEDIUM
impactDescription: hooks provide dynamic registration and proper lifecycle management
tags: provider, tools, hooks, registration
---

## Register Tools via Hooks Inside Provider

Register tools using `useFrontendTool` and `useRenderTool` hooks inside components that are children of CopilotKitProvider, rather than passing tool definitions as props. Hook-based registration ties tool availability to component lifecycle and enables dynamic tool sets.

**Incorrect (static tool props on provider):**

```tsx
const tools = [
  { name: "search", handler: searchFn, description: "Search docs" }
]

function App() {
  return (
    <CopilotKitProvider runtimeUrl="/api/copilotkit" tools={tools}>
      <MyApp />
    </CopilotKitProvider>
  )
}
```

**Correct (hook-based registration inside provider):**

```tsx
function MyApp() {
  useFrontendTool({
    name: "search",
    description: "Search the documentation",
    parameters: [{ name: "query", type: "string", description: "Search query" }],
    handler: async ({ query }) => {
      return await searchDocs(query)
    },
  })

  return <Dashboard />
}
```

Reference: [useFrontendTool](https://docs.copilotkit.ai/reference/hooks/useFrontendTool)
