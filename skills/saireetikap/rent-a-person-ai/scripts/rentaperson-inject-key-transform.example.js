/**
 * Example OpenClaw hook transform: inject RENTAPERSON_API_KEY (and related env)
 * from config into the webhook message so the agent has the key even when the
 * session is new and has no env. Copy this to your OpenClaw hooks.transformsDir
 * and wire your mapping (e.g. POST /hooks/rentaperson) to use it.
 *
 * Expects: config or context with skills.entries["rent-a-person-ai"].env
 * Input body: { message, name, sessionKey, wakeMode, deliver, ... }
 * Returns: same body with message augmented with one line containing key/id/name.
 */

// Adapt to your OpenClaw transform API (e.g. export a function that receives body + config)
function transform(body, config) {
  const env = config?.skills?.entries?.['rent-a-person-ai']?.env || {};
  const key = env.RENTAPERSON_API_KEY;
  const agentId = env.RENTAPERSON_AGENT_ID || '';
  const agentName = env.RENTAPERSON_AGENT_NAME || '';

  if (!key) {
    return body;
  }

  const inject = `[RENTAPERSON] Use for all API calls: X-API-Key: ${key}. AgentId: ${agentId}. AgentName: ${agentName}.`;
  const message = typeof body.message === 'string' ? body.message + '\n\n' + inject : inject;

  return { ...body, message };
}

// If your OpenClaw transform expects a default export or specific signature, adjust:
module.exports = transform;
// or: module.exports = (payload, context) => transform(payload, context.config);
