---
title: Scope Agent Config with Nested Providers
impact: HIGH
impactDescription: prevents agent configuration conflicts in multi-agent apps
tags: provider, nesting, multi-agent, configuration
---

## Scope Agent Config with Nested Providers

When different parts of your app need different agent configurations (different agents, tools, or context), nest CopilotKitProviders to scope configuration. Inner providers inherit from outer ones but can override specific settings.

**Incorrect (single provider, all agents share config):**

```tsx
function App() {
  return (
    <CopilotKitProvider runtimeUrl="/api/copilotkit">
      <ResearchPanel />
      <WritingPanel />
    </CopilotKitProvider>
  )
}
```

**Correct (nested providers scope agent config):**

```tsx
function App() {
  return (
    <CopilotKitProvider runtimeUrl="/api/copilotkit">
      <CopilotKitProvider agentId="researcher">
        <ResearchPanel />
      </CopilotKitProvider>
      <CopilotKitProvider agentId="writer">
        <WritingPanel />
      </CopilotKitProvider>
    </CopilotKitProvider>
  )
}
```

Reference: [CopilotKit Provider](https://docs.copilotkit.ai/reference/components/CopilotKitProvider)
