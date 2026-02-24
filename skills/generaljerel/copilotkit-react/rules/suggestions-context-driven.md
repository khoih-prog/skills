---
title: Provide Rich Context for Suggestions
impact: LOW
impactDescription: suggestions without context are generic and irrelevant
tags: suggestions, context, relevance
---

## Provide Rich Context for Suggestions

Suggestions are only as good as the context available. Combine `useConfigureSuggestions` with `useAgentContext` to give the suggestion engine enough information to produce relevant, actionable suggestions.

**Incorrect (suggestions without context):**

```tsx
function TaskBoard() {
  useConfigureSuggestions({
    instructions: "Suggest helpful actions",
    maxSuggestions: 3,
  })

  return <Board />
}
```

**Correct (suggestions enriched with context):**

```tsx
function TaskBoard() {
  const tasks = useTasks()
  const overdue = tasks.filter(t => t.isOverdue)

  useAgentContext({
    context: {
      totalTasks: tasks.length,
      overdueTasks: overdue.map(t => ({ id: t.id, title: t.title, dueDate: t.dueDate })),
      currentSprint: "Sprint 14",
    },
  })

  useConfigureSuggestions({
    instructions: "Suggest actions based on overdue tasks and sprint progress. Prioritize urgent items.",
    maxSuggestions: 3,
  })

  return <Board tasks={tasks} />
}
```

Reference: [useConfigureSuggestions](https://docs.copilotkit.ai/reference/hooks/useConfigureSuggestions)
