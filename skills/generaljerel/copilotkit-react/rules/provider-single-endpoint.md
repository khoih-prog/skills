---
title: Use useSingleEndpoint for AG-UI Protocol
impact: CRITICAL
impactDescription: required for v2 agent communication protocol
tags: provider, AG-UI, protocol, endpoint
---

## Use useSingleEndpoint for AG-UI Protocol

CopilotKit v2 uses the AG-UI protocol, which communicates through a single streaming endpoint. Enable `useSingleEndpoint` on the provider to route all agent traffic through one connection, reducing overhead and enabling proper event streaming.

**Incorrect (legacy multi-endpoint mode):**

```tsx
<CopilotKitProvider runtimeUrl="/api/copilotkit">
  <MyApp />
</CopilotKitProvider>
```

**Correct (single endpoint for AG-UI):**

```tsx
<CopilotKitProvider
  runtimeUrl="/api/copilotkit"
  useSingleEndpoint
>
  <MyApp />
</CopilotKitProvider>
```

When using Copilot Cloud, `useSingleEndpoint` is the default and does not need to be set explicitly.

Reference: [CopilotKit Provider](https://docs.copilotkit.ai/reference/components/CopilotKitProvider)
