# AGENTS.md — Team Capabilities

Use this to decide routing. Each agent is described by what they CAN do, what they CANNOT do, what INPUT they need, what OUTPUT format to expect, and their default TIMEOUT.

---

## Communication Signals

All agents may include these tags in their output to flag non-standard situations. Clean deliveries use `[READY]` or no tag.

| Signal | Meaning | Your Action |
|--------|---------|-------------|
| `[READY]` | Standard delivery — complete and confident | Normal quality review |
| `[NEEDS_INFO]` | Agent needs more context | Gather info (ask owner, check shared/, or delegate to another agent), re-brief |
| `[BLOCKED]` | Agent cannot complete the task | Assess why, try alternative approach or different agent, or escalate |
| `[LOW_CONFIDENCE]` | Output delivered but agent flags uncertainty | Review more carefully, consider Researcher verification or Reviewer |
| `[SCOPE_FLAG]` | Task is bigger than expected or prerequisites missing | Reassess scope with owner before proceeding |
| `[KB_PROPOSE]` | Agent proposes a shared knowledge update | Parse proposal; apply if owner-confirmed context, ask owner if inference |
| `[MEMORY_DONE]` | Agent finished writing its own memory (not sent by Reviewer) | Safe to route next step |
| `[CONTEXT_LOST]` | Agent session was compacted, needs context re-send | Re-send current task state from SCRATCH.md |

---

## Timeout Defaults

Default timeout guidance per agent:

| Agent | Timeout | Rationale |
|-------|---------|-----------|
| Researcher | 180s | Web search can be slow |
| Content | 120s | Text generation is fast |
| Designer | 180s | Image generation takes time |
| Operator | 120s (300s for browser tasks) | Browser automation is variable |
| Engineer | 300s | Coding tasks can be complex |
| Reviewer | 90s | Review = reading + structured verdict |

**On timeout** (`outcome: "timeout"`):
1. Update status message with timeout icon
2. Retry once with a simpler brief, or try a different approach
3. If second timeout → escalate to owner
4. **Never** silently retry indefinitely

---

## Communication Channels

All agent communication uses `sessions_send` (persistent sessions). `sessions_spawn` is not used.

- **Session key format**: `agent:{id}:main` (e.g., `agent:content:main`)
- **Same agent**: serial — one task at a time. Session context persists across tasks.
- **Cross agent**: parallel — Leader can message Content + Designer + Researcher simultaneously.
- **Multi-task queuing**: Multiple owner requests are queued by the gateway. Leader processes them at ping-pong boundaries.
- **Ping-pong limit**: 3 rounds per `sessions_send`. For longer exchanges, send a new `sessions_send` (session context is preserved).
- **Reviewer**: Participates in A2A but remains read-only. Does not send `[MEMORY_DONE]`.

---

## Researcher

**Capabilities:**
- Market research and competitive analysis
- Trend identification and forecasting
- Data gathering, synthesis, and interpretation
- Audience profiling and demographic analysis
- Fact-checking and source verification
- Structured report generation with confidence levels

**Cannot:**
- Write final copy or creative content
- Execute code or API calls
- Access browser or external tools

**Input needs:**
- Specific research question or hypothesis
- Scope constraints (depth, timeframe, geography)
- Relevant shared/ file paths for context
- Brand scope (from brand-registry.md)

**Output format:**
- Structured brief: Key Findings → Analysis → Recommendations → Confidence & Gaps → Sources
- Proposes significant findings for shared/domain/ via `[KB_PROPOSE]`

---

## Content

**Capabilities:**
- Multi-language copywriting (adapts to brand content language per profile.md)
- Content strategy and editorial planning
- Brand voice adaptation
- Translation and localization
- A/B copy variation generation
- Hashtag strategy
- Social media caption and post writing

**Cannot:**
- Generate images or visual assets
- Execute code or API calls
- Post or publish content
- Access browser

**Input needs:**
- Brand context (brand_id from brand-registry.md, link to shared/brands/{brand_id}/)
- Platform and format (e.g., "Facebook post", "Instagram caption")
- Topic or content brief
- Research insights (if available, from Researcher)
- Tone/style guidance (or reference to brand profile)

**Output format:**
- Ready-to-review content with platform formatting
- 2-3 variations for important pieces
- Tagged `[PENDING APPROVAL]` for external-facing content

---

## Designer

**Capabilities:**
- Visual concept development and art direction
- Image generation prompt engineering
- Brand visual consistency management
- Mood board and visual brief creation
- Platform-specific visual formatting (aspect ratios, safe zones)
- Color palette and typography guidance

**Cannot:**
- Write final copy (only placeholder text in visual briefs)
- Execute code or API calls
- Access browser

**Input needs:**
- Brand context (brand_id from brand-registry.md, link to shared/brands/{brand_id}/)
- Visual brief or concept description
- Platform requirements (dimensions, format)
- Copy to accompany (if available, from Content)
- Reference images or style direction

**Output format:**
- Detailed visual brief OR generated image(s)
- Brief-first workflow: write brief → generate → present
- Tagged `[PENDING APPROVAL]` for external-facing visuals

---

## Operator

**Capabilities:**
- Browser automation (CDP-based Browser Control + OS-level screen automation)
- Web platform UI interaction (social media backends, analytics dashboards, admin panels)
- Form filling, data extraction from web interfaces
- Screenshot capture and visual verification
- Multi-step UI workflow execution (posting, scheduling, data pulling via UI)

**Cannot:**
- Write or execute code
- Edit files or apply patches
- Make strategy or content decisions

**Input needs:**
- Clear execution plan (what to do, in what order, on what platform)
- Which browser tool to use — defaults to screen automation if not specified
- Expected outcome or verification criteria
- Login context (which existing session or credentials to use)
- Brand scope (from brand-registry.md) if brand-specific task

**Output format:**
- Execution confirmation with screenshots or text evidence
- Extracted data in structured format
- Error reports with screenshots if unexpected state encountered

---

## Engineer

**Capabilities:**
- Full-stack development (frontend + backend)
- Script writing and automation
- API integration and data processing
- CLI tool operation (check skills/ for available tools)
- Debugging, testing, deployment
- Database operations

**Cannot:**
- Write marketing copy or brand content
- Make brand/strategy decisions
- Access browser (browser/UI tasks → Operator)

**Input needs:**
- Technical specification or task description
- Existing code/file paths if modifying
- Expected output/behavior
- Constraints (language, framework, security requirements)
- Brand scope (from brand-registry.md) if brand-specific task

**Output format:**
- Working code with tests
- Technical documentation
- Execution results / logs
- Tagged `[PENDING REVIEW]` for code changes

---

## Reviewer

**Capabilities:**
- Cross-model quality assessment (provides independent perspective)
- Brief compliance evaluation
- Brand alignment checking
- Factual accuracy verification
- Audience fit assessment
- Strategic value judgment
- Structured verdict delivery

**Cannot:**
- Write, create, or modify content (review only)
- Access external tools, browser, or execute code
- Write to files

**Input needs:**
- The deliverable to review
- The original task brief
- Relevant shared/ file paths (brand profiles, guidelines — from brand-registry.md)
- Any prior revision context

**Output format:**
- Structured verdict: `[APPROVE]` or `[REVISE]`
- If `[REVISE]`: specific, actionable feedback (not vague suggestions)
- Reviews must be shorter than the deliverable
- Read brand files before reviewing — uninformed reviews waste cycles

**Invocation rules:**
- On-demand only — Leader decides when to invoke
- Max 2 review rounds per task
- Leader evaluates Reviewer feedback as a peer, not as a directive

---

## Handling `[PENDING REVIEW]`

When Engineer delivers code tagged `[PENDING REVIEW]`:
1. **Read the code yourself** — Understand what it does before routing to Reviewer.
2. **Check for obvious issues** — Security, correctness, scope. If clearly broken, send back immediately.
3. **Route to Reviewer** if the change is non-trivial (>20 lines, security-sensitive, or touches shared infrastructure).
4. **Skip Reviewer** for trivial changes (config tweaks, typo fixes, single-line patches) — approve directly.
5. **After review** — Merge Reviewer feedback with your own assessment. Decide whether to request rework or approve.

---

## Scheduling Responsibility

- **Leader** owns the content schedule. Decide what gets posted when, based on brand strategy and owner input.
- **Operator** executes posting actions only when Leader provides an explicit execution plan.
- Operator does NOT independently decide posting times or content order.

---

## Research Request Flow

When Content needs research to inform a piece:
1. Content signals `[NEEDS_INFO]` with specific research questions.
2. Leader routes the research request to Researcher with scope and context.
3. Researcher delivers findings back to Leader.
4. Leader passes relevant findings to Content with the re-brief.

Content does NOT directly request research from Researcher — all routing goes through Leader.

---

## Image Generation Fallback

When Designer's image generation fails (tool unavailable, quota exceeded, quality too low):
1. Designer reports `[BLOCKED]` or `[LOW_CONFIDENCE]` with explanation.
2. Leader assesses options:
   - **Retry** — if transient error, retry once with simplified prompt.
   - **Text-only fallback** — proceed with text content only, note to owner that image was unavailable.
   - **Stock/reference** — ask Designer for a visual brief with reference image URLs instead.
   - **Defer** — hold the post and inform owner, wait for tool availability.
3. Never silently drop the visual component — always inform owner of the fallback chosen.
