---
title: Declare Dependency Arrays for useFrontendTool
impact: MEDIUM
impactDescription: missing deps cause stale closures or infinite re-registrations
tags: agent, hooks, useFrontendTool, dependencies
---

## Declare Dependency Arrays for useFrontendTool

`useFrontendTool` re-registers the tool when its configuration changes. Without a dependency array, the tool re-registers on every render. Include all values from the component scope that the handler uses.

**Incorrect (no deps, re-registers every render):**

```tsx
function TaskPanel({ projectId }: { projectId: string }) {
  useFrontendTool({
    name: "create_task",
    handler: async ({ title }) => {
      await createTask(projectId, title)
    },
  })

  return <TaskList projectId={projectId} />
}
```

**Correct (deps array controls re-registration):**

```tsx
function TaskPanel({ projectId }: { projectId: string }) {
  useFrontendTool({
    name: "create_task",
    handler: async ({ title }) => {
      await createTask(projectId, title)
    },
    deps: [projectId],
  })

  return <TaskList projectId={projectId} />
}
```

Reference: [useFrontendTool](https://docs.copilotkit.ai/reference/hooks/useFrontendTool)
