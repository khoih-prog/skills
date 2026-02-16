---
name: openburn
description: Automates burning SOL tokens from a creator wallet to a burn address. Use this skill when the user wants to set up a regular burning schedule for their Pump.fun tokens.
metadata:
  {
    "openclaw":
      {
        "emoji": "🔥",
        "requires":
          {
            "modules": ["@solana/web3.js"],
            "env":
              [
                "CREATOR_WALLET_PRIVATE_KEY",
                "PUMP_FUN_TOKEN_ADDRESS",
                "API_URL",
              ],
          },
        "install":
          [
            {
              "id": "pnpm-solana",
              "kind": "npm",
              "module": "@solana/web3.js",
              "cmd": "pnpm add @solana/web3.js -w",
              "label": "Install @solana/web3.js",
            },
          ],
      },
  }
---

# Openburn

This skill helps users automate the burning of SOL tokens from a creator wallet to a burn address on Pump.fun.

## Setup Instructions

1.  **Request Credentials**:
    Ask the user for the following information:
    - `PUMP_FUN_TOKEN_ADDRESS` (The token address on Pump.fun)
    - `CREATOR_WALLET_PRIVATE_KEY` (The private key of the wallet to burn from)
    - `API_URL` (The base URL for the API to report status to, e.g., `https://api.example.com`)

    > [!IMPORTANT]
    > Remind the user that their keys will be stored locally in the `.env` file.

2.  **Store Credentials**:
    Check if the `.env` file exists in the root directory.
    - If it exists, append the keys.
    - If not, create it.

    Format:

    ```env
    PUMP_FUN_TOKEN_ADDRESS=...
    CREATOR_WALLET_PRIVATE_KEY=...
    API_URL=...
    ```

3.  **Register Token**:
    Make a POST request to register the token and wallet.

    **Endpoint**: `POST {API_URL}/api/burn/register`
    **Body**:

    ```json
    {
      "tokenAddress": "...",
      "creatorWallet": "..." (Public key derived from private key if possible, or ask user for public key if needed. For now, sending the token address is key)
    }
    ```

    _Note: If the user provided the private key, you can explain that the script will derive the public key, but for this registration call, you might strictly send what you have or just the token address if that's what the API expects._

4.  **Schedule Job**:
    Ask the user for the scheduling interval (default: every 2 hours).

    Use the `cron` tool to register a new job:
    - **Name**: `openburn-job`
    - **Schedule**: `{ "kind": "every", "everyMs": 7200000 }` (replace 7200000 with user's interval in ms)
    - **Session Target**: `isolated`
    - **Payload**:
      ```json
      {
        "kind": "agentTurn",
        "message": "Execute the openburn script to burn SOL tokens.",
        "deliver": true
      }
      ```

5.  **Report Schedule**:
    Make a POST request to report the scheduled job.

    **Endpoint**: `POST {API_URL}/api/burn/schedule`
    **Body**:

    ```json
    {
      "jobId": "openburn-job",
      "intervalMs": 7200000
    }
    ```

## Execution Instructions

When the cron job triggers (receiving the message "Execute the openburn script..."):

1.  **Execute the Script**:
    Run the burn script located at `skills/openburn/scripts/burn.ts`.

    ```bash
    node --import tsx skills/openburn/scripts/burn.ts
    ```

2.  **Report Results**:
    The script will automatically report transaction success/failure to `{API_URL}/api/burn/transaction`.
    You should also report the output (transaction signature) to the user in the chat.

## References

- [API Specifications](references/api.md)
