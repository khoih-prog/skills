---
title: Split Context by Domain
impact: MEDIUM
impactDescription: granular context updates avoid re-sending unchanged data
tags: state, context, granularity, optimization
---

## Split Context by Domain

Instead of one large `useAgentContext` call, split context into multiple calls by domain. This way, only the changed domain's context gets re-sent to the agent, reducing token usage and improving response quality.

**Incorrect (single monolithic context):**

```tsx
function Dashboard() {
  const user = useUser()
  const projects = useProjects()
  const notifications = useNotifications()

  useAgentContext({
    context: `User: ${user.name}, Role: ${user.role}. 
Projects: ${JSON.stringify(projects)}. 
Notifications: ${notifications.length} unread.`,
  })

  return <DashboardView />
}
```

**Correct (split context by domain):**

```tsx
function Dashboard() {
  const user = useUser()
  const projects = useProjects()
  const notifications = useNotifications()

  useAgentContext({
    context: { userName: user.name, role: user.role },
    description: "Current user information",
  })

  useAgentContext({
    context: { projects: projects.map(p => ({ id: p.id, name: p.name, status: p.status })) },
    description: "User's projects",
  })

  useAgentContext({
    context: { unreadCount: notifications.length },
    description: "Notification status",
  })

  return <DashboardView />
}
```

Reference: [useAgentContext](https://docs.copilotkit.ai/reference/hooks/useAgentContext)
