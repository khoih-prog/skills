---
title: Always Configure runtimeUrl
impact: CRITICAL
impactDescription: agents will not connect without a runtime URL
tags: provider, setup, configuration
---

## Always Configure runtimeUrl

CopilotKitProvider requires a `runtimeUrl` to connect to your agent backend. Without it, all agent interactions silently fail. The runtime URL points to your CopilotKit runtime endpoint that bridges frontend and agent.

**Incorrect (no runtime URL, agents can't connect):**

```tsx
function App() {
  return (
    <CopilotKitProvider>
      <CopilotChat />
      <MyApp />
    </CopilotKitProvider>
  )
}
```

**Correct (runtime URL configured):**

```tsx
function App() {
  return (
    <CopilotKitProvider runtimeUrl="/api/copilotkit">
      <CopilotChat />
      <MyApp />
    </CopilotKitProvider>
  )
}
```

For Copilot Cloud, use `publicApiKey` instead of `runtimeUrl`:

```tsx
<CopilotKitProvider publicApiKey="ck_pub_...">
  <CopilotChat />
  <MyApp />
</CopilotKitProvider>
```

Reference: [CopilotKit Provider](https://docs.copilotkit.ai/reference/components/CopilotKitProvider)
