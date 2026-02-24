---
title: Always Pass agentId for Multi-Agent
impact: HIGH
impactDescription: without agentId, requests route to wrong agent or fail
tags: agent, hooks, multi-agent, routing
---

## Always Pass agentId for Multi-Agent

When your application has multiple agents, always specify `agentId` in hooks like `useAgent`, `useFrontendTool`, and in the provider. Without it, CopilotKit cannot route requests to the correct agent, causing unexpected behavior or errors.

**Incorrect (no agentId, ambiguous routing):**

```tsx
function ResearchPanel() {
  const { agent, run } = useAgent({})

  useFrontendTool({
    name: "save_result",
    handler: async ({ result }) => saveToDb(result),
  })

  return <button onClick={() => run("Research AI trends")}>Go</button>
}
```

**Correct (explicit agentId for routing):**

```tsx
function ResearchPanel() {
  const { agent, run } = useAgent({ agentId: "researcher" })

  useFrontendTool({
    name: "save_result",
    agentId: "researcher",
    handler: async ({ result }) => saveToDb(result),
  })

  return <button onClick={() => run("Research AI trends")}>Go</button>
}
```

Reference: [useAgent Hook](https://docs.copilotkit.ai/reference/hooks/useAgent)
