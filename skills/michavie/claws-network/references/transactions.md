# Transaction Management

This guide details how to send transactions on the Claws Network.

## 1. Basic Transaction Structure

A transaction requires:
- **Sender**: Your address.
- **Receiver**: Destination address (user or contract).
- **Value**: Amount of native token to transfer (0 for contract calls usually).
- **Gas Limit**: Maximum gas units to consume.
- **Data**: Payload (optional for transfers, required for contract calls).
- **Chain ID**: `D` for Devnet.
- **Nonce**: Sequence number for ordering.

## 2. Sending Value Transfer

Transfer tokens from your wallet to another address.

```bash
mxpy tx new \
    --receiver <RECEIVER_ADDRESS> \
    --value <AMOUNT_IN_EGLD> \
    --gas-limit 50000 \
    --proxy=https://api.claws.network \
    --chain=D \
    --recall-nonce \
    --pem=wallet.pem \
    --send
```

## 3. Handling Nonces

The `--recall-nonce` flag automatically fetches the correct nonce from the network. If sending multiple transactions in rapid succession, you may need to manually manage nonces.

## 4. Check Transaction Status

After sending, you get a transaction hash. Use it to check the status.

```bash
mxpy tx get \
    --hash <TX_HASH> \
    --proxy=https://api.claws.network
```
