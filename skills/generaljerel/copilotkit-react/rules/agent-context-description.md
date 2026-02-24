---
title: Write Descriptive Context Values
impact: HIGH
impactDescription: vague context produces vague agent responses
tags: agent, context, useAgentContext, quality
---

## Write Descriptive Context Values

When using `useAgentContext`, provide specific, descriptive context that helps the agent understand the current application state. Vague or minimal context leads to generic agent responses that don't match the user's situation.

**Incorrect (vague context, agent lacks understanding):**

```tsx
useAgentContext({
  context: "user is on dashboard",
})
```

**Correct (specific context with relevant details):**

```tsx
useAgentContext({
  context: `The user is viewing the project dashboard for "${project.name}". 
There are ${tasks.length} tasks, ${tasks.filter(t => t.status === "overdue").length} are overdue. 
The user has admin permissions and can reassign tasks.`,
})
```

Reference: [useAgentContext](https://docs.copilotkit.ai/reference/hooks/useAgentContext)
