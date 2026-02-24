---
title: Configure Suggestion Generation
impact: LOW
impactDescription: unconfigured suggestions are generic and unhelpful
tags: suggestions, configuration, useConfigureSuggestions
---

## Configure Suggestion Generation

Use `useConfigureSuggestions` to control how and when suggestions are generated. Without configuration, suggestions may be too generic or generated at inappropriate times, wasting LLM calls.

**Incorrect (no suggestion configuration):**

```tsx
function App() {
  return (
    <CopilotKitProvider runtimeUrl="/api/copilotkit">
      <CopilotSidebar>
        <Dashboard />
      </CopilotSidebar>
    </CopilotKitProvider>
  )
}
```

**Correct (configured suggestion generation):**

```tsx
function Dashboard() {
  useConfigureSuggestions({
    instructions: "Suggest actions relevant to the user's current project and recent activity.",
    maxSuggestions: 3,
    minDelay: 1000,
  })

  return <DashboardView />
}
```

Reference: [useConfigureSuggestions](https://docs.copilotkit.ai/reference/hooks/useConfigureSuggestions)
