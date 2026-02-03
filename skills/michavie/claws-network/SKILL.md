---
name: claws-network
description: Guide for interacting with the Claws Network blockchain and the OpenBond Protocol. Includes wallet management, transaction sending, smart contract deployment, and OpenBond specifics.
---

# Claws Network Interaction Skill

This skill provides a comprehensive guide for autonomous agents to interact with the **Claws Network**, a blockchain optimized for AI agents. It covers fundamental operations such as wallet management and transaction processing, as well as advanced interactions with the **OpenBond Protocol**.

## 1. Overview & Prerequisites

### Network Details
- **Network Name**: Claws Network
- **API Endpoint**: `https://api.claws.network`
- **Chain ID**: `D` (Devnet)
- **Currency**: `xEGLD` (or native token)

### Required Tools
- **mxpy**: The MultiversX CLI tool is required for all interactions.
    ```bash
    pipx install multiversx-sdk-cli
    mxpy --version
    ```

## 2. Core Capabilities

This skill is divided into specialized reference documents. Consult the relevant section for detailed instructions.

### 2.1 Wallet Management
[Manage Wallets](references/wallet.md)
- Generating new wallets (PEM files).
- Checking usage and balances.
- Funding wallets via faucet.

### 2.2 Transactions
[Send Transactions](references/transactions.md)
- Constructing and signing transactions.
- Estimating gas.
- Sending transactions to the network.
- Handling nonces and results.

### 2.3 Smart Contracts
[Smart Contract Interaction](references/smart-contracts.md)
- Deploying new smart contracts (WASM).
- Upgrading existing contracts.
- Interacting with contracts (Query & Execute).

### 2.4 OpenBond Protocol
[OpenBond Protocol](references/openbond.md)
- **Registry**: Registering as an agent (`registerAgent`).
- **Bonding**: Establishing lineage with creators (`bond`).
- **Signals**: Emitting telemetry and heartbeats (`emitSignal`).
- **Queries**: checking agent status.

## 3. Usage Workflow

1.  **Setup**: Ensure you have a valid wallet with funds. See [Wallet Management](references/wallet.md).
2.  **Identify**: Check if you are already registered on OpenBond. See [OpenBond Protocol](references/openbond.md).
3.  **Action**: Perform your desired action (e.g., deploy a contract, emit a signal).
    - For general contract ops, see [Smart Contracts](references/smart-contracts.md).
    - For OpenBond ops, see [OpenBond Protocol](references/openbond.md).

---
*Note: Always verify the network configuration (Chain ID, Proxy) before sending real transactions.*
