---
name: clawhub-whitebit-trading
description: Build, install, update, and run a WhiteBIT trading skill through ClawHub (clawhub.ai) for OpenClaw. Use when asked to manage WhiteBIT trading automation as a ClawHub skill and execute trades with MCP-first validation.
metadata:
  openclaw:
    requires:
      env:
        - WHITEBIT_API_KEY
        - WHITEBIT_API_SECRET
      bins:
        - clawhub
    primaryEnv: WHITEBIT_API_SECRET
    skillKey: whitebit
    homepage: https://clawhub.ai/zonder/whitebit
---

# ClawHub WhiteBIT Trading

Run a ClawHub-native workflow for WhiteBIT trading automation in OpenClaw.

## Workflow
1. Verify ClawHub and skill environment first.
- Confirm ClawHub site context: `https://clawhub.ai`.
- Confirm `clawhub` CLI is available and authenticated when publish/update actions are requested.
- Prefer ClawHub skill lifecycle commands from [references/clawhub-cli.md](references/clawhub-cli.md).
- Confirm OpenClaw session will reload skills after install/update.

2. Verify MCP connectivity for runtime execution.
- Confirm trading MCP tools are available in-session.
- Confirm WhiteBIT docs MCP server is available (`https://docs.whitebit.com/mcp`).
- Use the check prompt: `What MCP tools do you have available?`
- If trading tools are unavailable, stop and report the missing capability.

3. Gather the trade intent before execution.
- Require: `symbol`, `side`, `order type`, and `size` (base size or quote notional).
- For limit orders, require `price` and `time in force` if applicable.
- Require execution constraints: max slippage or price bound, and whether partial fill is acceptable.
- Ask for only missing fields; do not place an order with implicit defaults.

4. Resolve exact parameters with MCP documentation lookup.
- Use WhiteBIT docs MCP search first for endpoint rules and required request fields.
- Confirm symbol formatting, precision/step-size constraints, and authentication requirements.
- Keep queries general when search is weak, then refine (for example, `spot order create` before specific field names).
- Use [references/mcp-setup.md](references/mcp-setup.md) for connector setup checks.
- Use [references/whitebit-api-basics.md](references/whitebit-api-basics.md) for baseline request/auth behavior.

5. Run pre-trade safety checks.
- Verify API liveness and account readiness before sending a live order.
- Validate available balance against requested notional plus fees buffer.
- Prefer a dry-run/preview/quote MCP tool when available.
- Apply the checklist in [references/trade-checklist.md](references/trade-checklist.md).

6. Execute via OpenClaw MCP tools.
- Place the order only after explicit user confirmation of final parameters.
- Use idempotency fields when supported (for example, `clientOrderId`) to avoid duplicate placement on retries.
- Capture and return order identifiers immediately.

7. Verify and report post-trade state.
- Query order status/fills after placement.
- Report executed quantity, average fill price, fees, and terminal status.
- If order is open/partial, report remaining quantity and next action options.

8. Handle failures deterministically.
- Parse and surface error payloads in structured form.
- Apply backoff on rate-limit errors.
- Do not blind-retry a market order after network ambiguity; re-check order state first.
- If execution status is uncertain, require user confirmation before any second placement.

9. Manage the skill through ClawHub when requested.
- Search registry: `clawhub search "whitebit"`.
- Install/update in workspace: `clawhub install whitebit`, `clawhub update whitebit`, or `clawhub update --all`.
- Publish this skill folder to ClawHub with explicit slug/version metadata.
- Use `clawhub sync --dry-run` before bulk publish/update operations.

## Guardrails
- Never expose API secret keys or signature material in output.
- Never place a live order without explicit confirmation that includes `symbol`, `side`, `order type`, and `size`.
- Prefer limit orders when the user does not explicitly request market execution.
- Refuse requests that bypass risk controls, such as "all-in", "no checks", or repeated force-retry loops.
- Keep an auditable summary for every execution attempt: timestamp, intent, validated params, action taken, and outcome.
- Do not publish private credentials or local-only data when pushing skills to ClawHub.

## Response Format
Use this compact structure when reporting actions:
1. `Intent`: normalized trade request.
2. `Skill Lifecycle`: ClawHub operation performed (`search/install/update/publish/sync`) or `none`.
3. `Validation`: docs checks and account/risk checks completed.
4. `Execution`: tool called and parameters sent.
5. `Result`: order id/status/fills or precise failure.
6. `Next`: one recommended next action.

## References
- [references/mcp-setup.md](references/mcp-setup.md)
- [references/clawhub-cli.md](references/clawhub-cli.md)
- [references/whitebit-api-basics.md](references/whitebit-api-basics.md)
- [references/trade-checklist.md](references/trade-checklist.md)
