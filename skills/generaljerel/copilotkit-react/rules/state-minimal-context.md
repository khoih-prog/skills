---
title: Provide Only Relevant Context
impact: MEDIUM
impactDescription: excessive context wastes tokens and confuses agents
tags: state, context, performance, tokens
---

## Provide Only Relevant Context

Only provide context that the agent needs for its current task. Dumping entire app state into context wastes LLM tokens, increases latency, and can confuse the agent with irrelevant information.

**Incorrect (entire app state as context):**

```tsx
function App() {
  const appState = useAppStore()

  useAgentContext({
    context: JSON.stringify(appState),
  })

  return <Dashboard />
}
```

**Correct (only relevant context for the current view):**

```tsx
function ProjectView({ projectId }: { projectId: string }) {
  const project = useProject(projectId)
  const tasks = useTasks(projectId)

  useAgentContext({
    context: `Current project: ${project.name} (${project.status}).
Active tasks: ${tasks.filter(t => t.status === "active").length}.
User role: ${project.currentUserRole}.`,
  })

  return <ProjectDashboard project={project} tasks={tasks} />
}
```

Reference: [useAgentContext](https://docs.copilotkit.ai/reference/hooks/useAgentContext)
