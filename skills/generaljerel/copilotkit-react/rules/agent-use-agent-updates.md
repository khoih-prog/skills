---
title: Specify useAgent Update Subscriptions
impact: HIGH
impactDescription: prevents unnecessary re-renders from agent state changes
tags: agent, hooks, performance, useAgent
---

## Specify useAgent Update Subscriptions

The `useAgent` hook accepts an `updates` array that controls which agent changes trigger a React re-render. Without specifying updates, your component may re-render on every agent event. Only subscribe to the updates your component actually needs.

**Incorrect (subscribes to all updates, causes re-render storms):**

```tsx
function AgentStatus() {
  const { agent } = useAgent({ agentId: "researcher" })

  return <div>Status: {agent.runStatus}</div>
}
```

**Correct (subscribes only to run status changes):**

```tsx
import { UseAgentUpdate } from "@copilotkitnext/react"

function AgentStatus() {
  const { agent } = useAgent({
    agentId: "researcher",
    updates: [UseAgentUpdate.OnRunStatusChanged],
  })

  return <div>Status: {agent.runStatus}</div>
}
```

Available update types:
- `UseAgentUpdate.OnMessagesChanged` - re-render when messages update
- `UseAgentUpdate.OnStateChanged` - re-render when agent state changes
- `UseAgentUpdate.OnRunStatusChanged` - re-render when run status changes

Reference: [useAgent Hook](https://docs.copilotkit.ai/reference/hooks/useAgent)
