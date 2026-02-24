---
title: Stabilize Tool Handler References
impact: MEDIUM
impactDescription: unstable handler references cause tool re-registration churn
tags: agent, hooks, useCallback, performance
---

## Stabilize Tool Handler References

When passing handler functions to `useFrontendTool`, wrap them with `useCallback` to maintain stable references. Unstable function references trigger unnecessary tool re-registrations, which can interrupt in-flight agent tool calls.

**Incorrect (new handler created every render):**

```tsx
function DocumentEditor({ docId }: { docId: string }) {
  useFrontendTool({
    name: "update_document",
    handler: async ({ content }) => {
      await updateDoc(docId, content)
    },
    deps: [docId],
  })

  return <Editor docId={docId} />
}
```

**Correct (stable handler via useCallback):**

```tsx
function DocumentEditor({ docId }: { docId: string }) {
  const handler = useCallback(
    async ({ content }: { content: string }) => {
      await updateDoc(docId, content)
    },
    [docId]
  )

  useFrontendTool({
    name: "update_document",
    handler,
    deps: [docId],
  })

  return <Editor docId={docId} />
}
```

Reference: [useFrontendTool](https://docs.copilotkit.ai/reference/hooks/useFrontendTool)
