---
name: browser-auth
description: Start a secure remote browser tunnel for manual user authentication (solving Captchas, 2FA, logins) and capture session data. Use when an agent needs to access a website that requires manual login or has bot protection.
---

# Browser Auth

This skill allows the agent to request the user to perform a manual login on a website and then capture the session cookies for further automated work.

## 🚨 Security Warning: RCE Risk

Running a remote browser session carries a risk of **Remote Code Execution (RCE)** if the browser navigates to a malicious website. To mitigate this:
1.  **Sandbox Enabled**: This skill runs Chromium with the sandbox **ENABLED** by default. 
2.  **Avoid Unsafe Sites**: Do not use this tunnel to visit untrusted or unknown URLs.
3.  **Local Bind**: Defaults to `127.0.0.1`. Do not expose to the public internet without a secure tunnel (VPN, SSH, Cloudflare Tunnel).
4.  **Isolation**: It is highly recommended to run the agent/node in an isolated container or VM.

## When to Use

- When a website requires a login that involves Captcha or 2FA.
- When bot detection prevents the agent from logging in automatically.
- When the user prefers not to share their password with the agent.

## Workflow

1.  **Request Auth**: Use `scripts/auth_server.js` to start a tunnel. It will print a unique Access URL.
2.  **Provide Link**: Give the user the link with the token.
3.  **Wait for Session**: Wait for the user to complete the login and click "DONE".
4.  **Verify**: Use `scripts/verify_session.js` to ensure the session is valid.
5.  **Use Cookies**: Use the captured `session.json` in other browser tools.

## Tools

### Start Auth Server
Starts the secure interactive browser tunnel.
```bash
AUTH_HOST=127.0.0.1 AUTH_TOKEN=secret123 node scripts/auth_server.js <port> <output_session_file>
```
Default port: `19191`. Default host: `127.0.0.1`.

### Verify Session
Checks if the captured cookies actually log you in.
```bash
node scripts/verify_session.js <session_file> <target_url> <expected_string_in_page>
```

## Troubleshooting

### Sandbox Issues on Linux
If the browser fails to start with a "sandbox" error, you may need to enable unprivileged user namespaces on your host or (less securely) set `BROWSER_NO_SANDBOX=true`. 
**Warning**: Disabling the sandbox significantly increases the risk of host compromise if a malicious site is visited.

## Runtime Requirements

Requires the following Node.js packages: `express`, `socket.io`, `playwright-core`.
