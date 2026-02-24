---
title: Define Zod Schemas for Tool Args
impact: HIGH
impactDescription: enables type-safe rendering and partial arg streaming
tags: tool, rendering, zod, type-safety
---

## Define Zod Schemas for Tool Args

When using `useRenderTool`, always define a Zod schema for the `args` parameter. This enables type-safe access to tool arguments and allows CopilotKit to stream partial arguments while the tool call is in progress, giving users real-time feedback.

**Incorrect (no schema, args are untyped):**

```tsx
useRenderTool({
  name: "show_weather",
  render: ({ args, status }) => {
    return (
      <WeatherCard
        city={args.city}
        temp={args.temperature}
      />
    )
  },
})
```

**Correct (Zod schema provides type safety and streaming):**

```tsx
import { z } from "zod"

useRenderTool({
  name: "show_weather",
  args: z.object({
    city: z.string(),
    temperature: z.number(),
    condition: z.enum(["sunny", "cloudy", "rainy"]),
  }),
  render: ({ args, status }) => {
    if (status === "inProgress") {
      return <WeatherCardSkeleton city={args.city} />
    }
    return (
      <WeatherCard
        city={args.city}
        temp={args.temperature}
        condition={args.condition}
      />
    )
  },
})
```

The Zod schema enables:
- TypeScript inference for `args` in the render function
- Partial args during `inProgress` status (for streaming UI)
- Validation before `executing` and `complete` statuses

Reference: [useRenderTool](https://docs.copilotkit.ai/reference/hooks/useRenderTool)
