# ClaudeHemat

# Introduction
1. **Haiku 4.5** is the default model. Only spawn **Sonnet 4.5** or **Opus 4.6** when the task actually needs either of them
2. Use sessions_spawn to use more advanced models
```
sessions_spawn(
  message: "<the full task description>",
  model: "anthropic/claude-sonnet-4-5",
  label: "<short task label>"
)
```
```
sessions_spawn(
  message: "<the full task description>",
  model: "anthropic/claude-opus-4-6",
  label: "<short task label>"
)
```

# Models
## Haiku 4.5
1. Simple Q&A - What, When, Who, Where
2. Casual chat - No reasoning needed
3. Quick lookups
4. Simple tasks - May but not limited to repetitive tasks
5. Concise output

## Sonnet 4.5
1. Analysis
2. Code (more than 10 lines of codes)
3. Planning
4. Reasoning
5. Comparisons
6. Reporting

## Opus 4.6
1. Deep research
2. Critical decisions
3. Extreme complex reasoning
4. Extreme complex planning
5. Detailed explanation

# Prohibitions
1. Never code using Haiku 4.5
2. Never analyze using Haiku 4.5
3. Never attempt reasoning using Haiku 4.5

# Other Notes
1. When the user asks you to use a specific model, use it
2. Always put which model is used in outputs
3. After you are done with more advanced models (Sonnet 4.5 or Opus 4.6), revert back to Haiku 4.5 as the default model