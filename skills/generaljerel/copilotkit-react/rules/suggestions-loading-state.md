---
title: Handle Suggestion Loading States
impact: LOW
impactDescription: unhandled loading causes layout shift when suggestions appear
tags: suggestions, loading, UI, state
---

## Handle Suggestion Loading States

When rendering suggestions in the UI, handle the loading state to prevent layout shifts. Suggestions are generated asynchronously and may take a moment to appear.

**Incorrect (no loading state, content jumps when suggestions load):**

```tsx
function SuggestionBar({ suggestions }: { suggestions: string[] }) {
  return (
    <div className="suggestions">
      {suggestions.map(s => (
        <button key={s}>{s}</button>
      ))}
    </div>
  )
}
```

**Correct (loading state with stable layout):**

```tsx
function SuggestionBar({
  suggestions,
  isLoading,
}: {
  suggestions: string[]
  isLoading: boolean
}) {
  return (
    <div className="suggestions" style={{ minHeight: 48 }}>
      {isLoading ? (
        <SuggestionSkeleton count={3} />
      ) : (
        suggestions.map(s => (
          <button key={s}>{s}</button>
        ))
      )}
    </div>
  )
}
```

Reference: [useConfigureSuggestions](https://docs.copilotkit.ai/reference/hooks/useConfigureSuggestions)
