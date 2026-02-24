# CopilotKit React Patterns

**Version 1.0.0**  
CopilotKit  
February 2026

> **Note:**  
> This document is mainly for agents and LLMs to follow when maintaining,  
> generating, or refactoring CopilotKit codebases. Humans  
> may also find it useful, but guidance here is optimized for automation  
> and consistency by AI-assisted workflows.

---

## Abstract

Best practices for building agentic React applications with CopilotKit. Contains 25 rules across 6 categories covering provider configuration, agent hooks, tool rendering, state management, chat UI, and suggestions. Each rule includes incorrect vs correct code examples grounded in the CopilotKit v2 React SDK.

---

## Table of Contents

1. [Provider Setup](#1-provider-setup) — **CRITICAL**
   - 1.1 [Always Configure runtimeUrl](#1.1-always-configure-runtimeurl)
   - 1.2 [Register Tools via Hooks Inside Provider](#1.2-register-tools-via-hooks-inside-provider)
   - 1.3 [Scope Agent Config with Nested Providers](#1.3-scope-agent-config-with-nested-providers)
   - 1.4 [Use useSingleEndpoint for AG-UI Protocol](#1.4-use-usesingleendpoint-for-ag-ui-protocol)
2. [Agent Hooks](#2-agent-hooks) — **HIGH**
   - 2.1 [Always Pass agentId for Multi-Agent](#2.1-always-pass-agentid-for-multi-agent)
   - 2.2 [Declare Dependency Arrays for useFrontendTool](#2.2-declare-dependency-arrays-for-usefrontendtool)
   - 2.3 [Specify useAgent Update Subscriptions](#2.3-specify-useagent-update-subscriptions)
   - 2.4 [Stabilize Tool Handler References](#2.4-stabilize-tool-handler-references)
   - 2.5 [Write Descriptive Context Values](#2.5-write-descriptive-context-values)
3. [Tool Rendering](#3-tool-rendering) — **HIGH**
   - 3.1 [Define Zod Schemas for Tool Args](#3.1-define-zod-schemas-for-tool-args)
   - 3.2 [Handle All Tool Call Statuses](#3.2-handle-all-tool-call-statuses)
   - 3.3 [Prefer useComponent for Simple Rendering](#3.3-prefer-usecomponent-for-simple-rendering)
   - 3.4 [Register Wildcard Renderer as Fallback](#3.4-register-wildcard-renderer-as-fallback)
   - 3.5 [useRenderTool for Display, useFrontendTool for Effects](#3.5-userendertool-for-display-usefrontendtool-for-effects)
4. [Context & State](#4-context-&-state) — **MEDIUM**
   - 4.1 [Avoid Stale Closures in Tool Handlers](#4.1-avoid-stale-closures-in-tool-handlers)
   - 4.2 [Provide Only Relevant Context](#4.2-provide-only-relevant-context)
   - 4.3 [Split Context by Domain](#4.3-split-context-by-domain)
   - 4.4 [Use Structured Objects in Context](#4.4-use-structured-objects-in-context)
5. [Chat UI](#5-chat-ui) — **MEDIUM**
   - 5.1 [Choose Appropriate Chat Layout](#5.1-choose-appropriate-chat-layout)
   - 5.2 [Customize Labels for Your Domain](#5.2-customize-labels-for-your-domain)
   - 5.3 [Provide Welcome Screen with Prompts](#5.3-provide-welcome-screen-with-prompts)
   - 5.4 [Use Appropriate Input Mode](#5.4-use-appropriate-input-mode)
6. [Suggestions](#6-suggestions) — **LOW**
   - 6.1 [Configure Suggestion Generation](#6.1-configure-suggestion-generation)
   - 6.2 [Handle Suggestion Loading States](#6.2-handle-suggestion-loading-states)
   - 6.3 [Provide Rich Context for Suggestions](#6.3-provide-rich-context-for-suggestions)

---

## 1. Provider Setup

**Impact: CRITICAL**

Correct CopilotKitProvider configuration is the foundation. Misconfiguration causes silent failures, broken agent connections, or degraded performance.

### 1.1 Always Configure runtimeUrl

**Impact: CRITICAL (agents will not connect without a runtime URL)**

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

### 1.2 Register Tools via Hooks Inside Provider

**Impact: MEDIUM (hooks provide dynamic registration and proper lifecycle management)**

## Register Tools via Hooks Inside Provider

Register tools using `useFrontendTool` and `useRenderTool` hooks inside components that are children of CopilotKitProvider, rather than passing tool definitions as props. Hook-based registration ties tool availability to component lifecycle and enables dynamic tool sets.

**Incorrect (static tool props on provider):**

```tsx
const tools = [
  { name: "search", handler: searchFn, description: "Search docs" }
]

function App() {
  return (
    <CopilotKitProvider runtimeUrl="/api/copilotkit" tools={tools}>
      <MyApp />
    </CopilotKitProvider>
  )
}
```

**Correct (hook-based registration inside provider):**

```tsx
function MyApp() {
  useFrontendTool({
    name: "search",
    description: "Search the documentation",
    parameters: [{ name: "query", type: "string", description: "Search query" }],
    handler: async ({ query }) => {
      return await searchDocs(query)
    },
  })

  return <Dashboard />
}
```

Reference: [useFrontendTool](https://docs.copilotkit.ai/reference/hooks/useFrontendTool)

### 1.3 Scope Agent Config with Nested Providers

**Impact: HIGH (prevents agent configuration conflicts in multi-agent apps)**

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

### 1.4 Use useSingleEndpoint for AG-UI Protocol

**Impact: CRITICAL (required for v2 agent communication protocol)**

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

## 2. Agent Hooks

**Impact: HIGH**

Patterns for useAgent, useFrontendTool, useAgentContext, and useHumanInTheLoop. Incorrect usage causes re-render storms, stale state, or broken agent interactions.

### 2.1 Always Pass agentId for Multi-Agent

**Impact: HIGH (without agentId, requests route to wrong agent or fail)**

## Always Pass agentId for Multi-Agent

When your application has multiple agents, always specify `agentId` in hooks like `useAgent`, `useFrontendTool`, and in the provider. Without it, CopilotKit cannot route requests to the correct agent, causing unexpected behavior or errors.

**Incorrect (no agentId, ambiguous routing):**

```tsx
function ResearchPanel() {
  const { agent, run } = useAgent({})

  useFrontendTool({
    name: "save_result",
    handler: async ({ result }) => saveToDb(result),
  })

  return <button onClick={() => run("Research AI trends")}>Go</button>
}
```

**Correct (explicit agentId for routing):**

```tsx
function ResearchPanel() {
  const { agent, run } = useAgent({ agentId: "researcher" })

  useFrontendTool({
    name: "save_result",
    agentId: "researcher",
    handler: async ({ result }) => saveToDb(result),
  })

  return <button onClick={() => run("Research AI trends")}>Go</button>
}
```

Reference: [useAgent Hook](https://docs.copilotkit.ai/reference/hooks/useAgent)

### 2.2 Declare Dependency Arrays for useFrontendTool

**Impact: MEDIUM (missing deps cause stale closures or infinite re-registrations)**

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

### 2.3 Specify useAgent Update Subscriptions

**Impact: HIGH (prevents unnecessary re-renders from agent state changes)**

## Specify useAgent Update Subscriptions

The `useAgent` hook accepts an `updates` array that controls which agent changes trigger a React re-render. Without specifying updates, your component may re-render on every agent event. Only subscribe to the updates your component actually needs.

**Incorrect (subscribes to all updates, causes re-render storms):**

```tsx
function AgentStatus() {
  const { agent } = useAgent({ agentId: "researcher" })

  return <div>Status: {agent.runStatus}</div>
}
```

**Correct (subscribes only to run status changes):**

```tsx
import { UseAgentUpdate } from "@copilotkitnext/react"

function AgentStatus() {
  const { agent } = useAgent({
    agentId: "researcher",
    updates: [UseAgentUpdate.OnRunStatusChanged],
  })

  return <div>Status: {agent.runStatus}</div>
}
```

Available update types:
- `UseAgentUpdate.OnMessagesChanged` - re-render when messages update
- `UseAgentUpdate.OnStateChanged` - re-render when agent state changes
- `UseAgentUpdate.OnRunStatusChanged` - re-render when run status changes

Reference: [useAgent Hook](https://docs.copilotkit.ai/reference/hooks/useAgent)

### 2.4 Stabilize Tool Handler References

**Impact: MEDIUM (unstable handler references cause tool re-registration churn)**

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

### 2.5 Write Descriptive Context Values

**Impact: HIGH (vague context produces vague agent responses)**

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

## 3. Tool Rendering

**Impact: HIGH**

Rules for rendering agent tool calls in the UI. Proper tool rendering is what makes CopilotKit's generative UI possible.

### 3.1 Define Zod Schemas for Tool Args

**Impact: HIGH (enables type-safe rendering and partial arg streaming)**

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

### 3.2 Handle All Tool Call Statuses

**Impact: HIGH (unhandled statuses cause blank UI or missing loading states)**

## Handle All Tool Call Statuses

Tool renders receive a `status` field with three possible values: `inProgress`, `executing`, and `complete`. Handle all three to provide proper loading states, execution feedback, and final results. Ignoring statuses causes jarring UI transitions.

**Incorrect (only handles complete, no loading state):**

```tsx
useRenderTool({
  name: "search_results",
  args: z.object({ query: z.string(), results: z.array(z.string()) }),
  render: ({ args }) => {
    return <ResultsList results={args.results} />
  },
})
```

**Correct (handles all three statuses):**

```tsx
useRenderTool({
  name: "search_results",
  args: z.object({ query: z.string(), results: z.array(z.string()) }),
  render: ({ args, status }) => {
    if (status === "inProgress") {
      return <SearchSkeleton query={args.query} />
    }
    if (status === "executing") {
      return <SearchProgress query={args.query} />
    }
    return <ResultsList results={args.results} />
  },
})
```

Reference: [useRenderTool](https://docs.copilotkit.ai/reference/hooks/useRenderTool)

### 3.3 Prefer useComponent for Simple Rendering

**Impact: MEDIUM (reduces boilerplate for common component-rendering patterns)**

## Prefer useComponent for Simple Rendering

When a tool call simply renders a React component from its arguments with no special status handling, use `useComponent` instead of `useRenderTool`. It provides a simpler API that maps tool args directly to component props.

**Incorrect (verbose useRenderTool for simple case):**

```tsx
useRenderTool({
  name: "show_user_card",
  args: z.object({
    name: z.string(),
    email: z.string(),
    avatar: z.string(),
  }),
  render: ({ args, status }) => {
    if (status !== "complete") return <UserCardSkeleton />
    return <UserCard name={args.name} email={args.email} avatar={args.avatar} />
  },
})
```

**Correct (useComponent for direct mapping):**

```tsx
useComponent({
  name: "show_user_card",
  component: UserCard,
  args: z.object({
    name: z.string(),
    email: z.string(),
    avatar: z.string(),
  }),
})
```

`useComponent` automatically handles loading states and maps args to component props.

Reference: [useComponent](https://docs.copilotkit.ai/reference/hooks/useComponent)

### 3.4 Register Wildcard Renderer as Fallback

**Impact: MEDIUM (prevents missing UI when agent calls unregistered tools)**

## Register Wildcard Renderer as Fallback

Register a wildcard `"*"` renderer with `useRenderTool` to catch tool calls that don't have a dedicated renderer. Without a fallback, unregistered tool calls render nothing in the chat, confusing users.

**Incorrect (no fallback, unknown tools render blank):**

```tsx
useRenderTool({
  name: "show_chart",
  render: ({ args }) => <Chart data={args.data} />,
})
```

**Correct (wildcard fallback for unknown tools):**

```tsx
useRenderTool({
  name: "show_chart",
  render: ({ args }) => <Chart data={args.data} />,
})

useRenderTool({
  name: "*",
  render: ({ name, args, status }) => (
    <GenericToolCard
      toolName={name}
      args={args}
      isLoading={status === "inProgress"}
    />
  ),
})
```

Reference: [useRenderTool](https://docs.copilotkit.ai/reference/hooks/useRenderTool)

### 3.5 useRenderTool for Display, useFrontendTool for Effects

**Impact: HIGH (mixing concerns causes side effects during streaming or double execution)**

## useRenderTool for Display, useFrontendTool for Effects

Use `useRenderTool` when you only need to display UI in response to a tool call. Use `useFrontendTool` when the tool call should trigger side effects (API calls, state mutations, navigation). Mixing them causes side effects to fire during streaming or display-only tools to swallow return values.

**Incorrect (side effects in a render tool):**

```tsx
useRenderTool({
  name: "create_ticket",
  render: ({ args, status }) => {
    if (status === "complete") {
      createTicketInDb(args)
    }
    return <TicketCard {...args} />
  },
})
```

**Correct (separate render from effects):**

```tsx
useFrontendTool({
  name: "create_ticket",
  handler: async ({ title, priority }) => {
    const ticket = await createTicketInDb({ title, priority })
    return { ticketId: ticket.id }
  },
})

useRenderTool({
  name: "create_ticket",
  render: ({ args, status }) => {
    if (status === "inProgress") return <TicketSkeleton />
    return <TicketCard title={args.title} priority={args.priority} />
  },
})
```

Reference: [useFrontendTool](https://docs.copilotkit.ai/reference/hooks/useFrontendTool)

## 4. Context & State

**Impact: MEDIUM**

Patterns for providing context to agents and managing shared state. Good context = good agent responses.

### 4.1 Avoid Stale Closures in Tool Handlers

**Impact: HIGH (stale closures cause tools to operate on outdated state)**

## Avoid Stale Closures in Tool Handlers

Tool handlers registered with `useFrontendTool` capture variables from their closure. If state changes between registration and invocation, the handler sees stale values. Use functional state updates or refs to always access current state.

**Incorrect (stale closure captures initial items):**

```tsx
function TodoPanel() {
  const [items, setItems] = useState<string[]>([])

  useFrontendTool({
    name: "add_todo",
    handler: async ({ title }) => {
      setItems([...items, title])
    },
  })

  return <TodoList items={items} />
}
```

**Correct (functional update always uses current state):**

```tsx
function TodoPanel() {
  const [items, setItems] = useState<string[]>([])

  useFrontendTool({
    name: "add_todo",
    handler: async ({ title }) => {
      setItems(prev => [...prev, title])
    },
  })

  return <TodoList items={items} />
}
```

Reference: [useFrontendTool](https://docs.copilotkit.ai/reference/hooks/useFrontendTool)

### 4.2 Provide Only Relevant Context

**Impact: MEDIUM (excessive context wastes tokens and confuses agents)**

## Provide Only Relevant Context

Only provide context that the agent needs for its current task. Dumping entire app state into context wastes LLM tokens, increases latency, and can confuse the agent with irrelevant information.

**Incorrect (entire app state as context):**

```tsx
function App() {
  const appState = useAppStore()

  useAgentContext({
    context: JSON.stringify(appState),
  })

  return <Dashboard />
}
```

**Correct (only relevant context for the current view):**

```tsx
function ProjectView({ projectId }: { projectId: string }) {
  const project = useProject(projectId)
  const tasks = useTasks(projectId)

  useAgentContext({
    context: `Current project: ${project.name} (${project.status}).
Active tasks: ${tasks.filter(t => t.status === "active").length}.
User role: ${project.currentUserRole}.`,
  })

  return <ProjectDashboard project={project} tasks={tasks} />
}
```

Reference: [useAgentContext](https://docs.copilotkit.ai/reference/hooks/useAgentContext)

### 4.3 Split Context by Domain

**Impact: MEDIUM (granular context updates avoid re-sending unchanged data)**

## Split Context by Domain

Instead of one large `useAgentContext` call, split context into multiple calls by domain. This way, only the changed domain's context gets re-sent to the agent, reducing token usage and improving response quality.

**Incorrect (single monolithic context):**

```tsx
function Dashboard() {
  const user = useUser()
  const projects = useProjects()
  const notifications = useNotifications()

  useAgentContext({
    context: `User: ${user.name}, Role: ${user.role}. 
Projects: ${JSON.stringify(projects)}. 
Notifications: ${notifications.length} unread.`,
  })

  return <DashboardView />
}
```

**Correct (split context by domain):**

```tsx
function Dashboard() {
  const user = useUser()
  const projects = useProjects()
  const notifications = useNotifications()

  useAgentContext({
    context: { userName: user.name, role: user.role },
    description: "Current user information",
  })

  useAgentContext({
    context: { projects: projects.map(p => ({ id: p.id, name: p.name, status: p.status })) },
    description: "User's projects",
  })

  useAgentContext({
    context: { unreadCount: notifications.length },
    description: "Notification status",
  })

  return <DashboardView />
}
```

Reference: [useAgentContext](https://docs.copilotkit.ai/reference/hooks/useAgentContext)

### 4.4 Use Structured Objects in Context

**Impact: MEDIUM (structured data enables better agent reasoning than flat strings)**

## Use Structured Objects in Context

When providing context via `useAgentContext`, use structured objects rather than serialized strings. Structured data helps agents parse and reason about context more reliably than free-form text.

**Incorrect (serialized string, hard for agent to parse):**

```tsx
useAgentContext({
  context: `items: ${items.map(i => `${i.name}(${i.price})`).join(", ")}`,
})
```

**Correct (structured object for reliable parsing):**

```tsx
useAgentContext({
  context: {
    cartItems: items.map(item => ({
      name: item.name,
      price: item.price,
      quantity: item.quantity,
    })),
    total: items.reduce((sum, i) => sum + i.price * i.quantity, 0),
    itemCount: items.length,
  },
})
```

Reference: [useAgentContext](https://docs.copilotkit.ai/reference/hooks/useAgentContext)

## 5. Chat UI

**Impact: MEDIUM**

Rules for configuring and customizing CopilotChat, CopilotSidebar, and CopilotPopup components.

### 5.1 Choose Appropriate Chat Layout

**Impact: MEDIUM (wrong layout choice degrades UX for the use case)**

## Choose Appropriate Chat Layout

Choose `CopilotSidebar` for persistent, always-visible agent interaction (e.g., copilot-assisted workflows). Choose `CopilotPopup` for on-demand, quick interactions. Choose `CopilotChat` for inline, embedded chat in a specific page section.

**Incorrect (popup for a workflow that needs persistent chat):**

```tsx
function ProjectWorkspace() {
  return (
    <div>
      <ProjectBoard />
      <CopilotPopup />
    </div>
  )
}
```

**Correct (sidebar for persistent workflow assistance):**

```tsx
function ProjectWorkspace() {
  return (
    <CopilotSidebar
      defaultOpen={true}
      labels={{ title: "Project Assistant" }}
    >
      <ProjectBoard />
    </CopilotSidebar>
  )
}
```

Reference: [Chat Components](https://docs.copilotkit.ai/reference/components/chat)

### 5.2 Customize Labels for Your Domain

**Impact: LOW (default labels feel generic and reduce user trust)**

## Customize Labels for Your Domain

Always customize the `labels` prop on chat components to match your application's domain. Default labels like "How can I help?" feel generic and don't build user confidence in the agent's capabilities.

**Incorrect (default labels, generic feel):**

```tsx
<CopilotSidebar>
  <MyApp />
</CopilotSidebar>
```

**Correct (domain-specific labels):**

```tsx
<CopilotSidebar
  labels={{
    title: "Sales Assistant",
    placeholder: "Ask about leads, deals, or forecasts...",
    initial: "I can help you analyze your pipeline, draft outreach, or update deal stages.",
  }}
>
  <MyApp />
</CopilotSidebar>
```

Reference: [Chat Components](https://docs.copilotkit.ai/reference/components/chat)

### 5.3 Provide Welcome Screen with Prompts

**Impact: LOW (users don't know what to ask without guidance)**

## Provide Welcome Screen with Prompts

Configure a welcome screen with suggested prompts to guide users on what the agent can do. An empty chat box with no guidance leads to low engagement because users don't know what to ask.

**Incorrect (no welcome screen, empty chat):**

```tsx
<CopilotChat />
```

**Correct (welcome screen with actionable prompts):**

```tsx
<CopilotChat
  welcomeScreen={{
    title: "Welcome to your AI Assistant",
    description: "I can help you with your projects and tasks.",
    suggestedPrompts: [
      "Summarize my overdue tasks",
      "Draft a status update for the team",
      "Create a new task for the landing page redesign",
    ],
  }}
/>
```

Reference: [Chat Components](https://docs.copilotkit.ai/reference/components/chat)

### 5.4 Use Appropriate Input Mode

**Impact: LOW (wrong input mode creates friction for the interaction type)**

## Use Appropriate Input Mode

Set the `inputMode` prop to match your use case. Use `"text"` for general chat, `"voice"` for hands-free workflows, and `"multi"` to let users switch between text and voice.

**Incorrect (default text mode for a driving assistant):**

```tsx
function DrivingAssistant() {
  return (
    <CopilotChat
      labels={{ title: "Navigation Assistant" }}
    />
  )
}
```

**Correct (voice mode for hands-free interaction):**

```tsx
function DrivingAssistant() {
  return (
    <CopilotChat
      inputMode="voice"
      labels={{ title: "Navigation Assistant" }}
    />
  )
}
```

Reference: [Chat Components](https://docs.copilotkit.ai/reference/components/chat)

## 6. Suggestions

**Impact: LOW**

Patterns for configuring proactive suggestions that help users discover agent capabilities.

### 6.1 Configure Suggestion Generation

**Impact: LOW (unconfigured suggestions are generic and unhelpful)**

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

### 6.2 Handle Suggestion Loading States

**Impact: LOW (unhandled loading causes layout shift when suggestions appear)**

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

### 6.3 Provide Rich Context for Suggestions

**Impact: LOW (suggestions without context are generic and irrelevant)**

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

---

## References

- https://docs.copilotkit.ai
- https://github.com/CopilotKit/CopilotKit
- https://docs.copilotkit.ai/reference/hooks
- https://docs.copilotkit.ai/reference/components
