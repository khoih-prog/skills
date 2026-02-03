# Wallet Management

This guide details how to manage wallets (accounts) on the Claws Network using `mxpy`.

## 1. Create a New Wallet

Generate a new wallet and save it as a PEM file.

```bash
mxpy wallet new --format pem --outfile wallet.pem
```

<Tip>
  Store your `wallet.pem` securely. Do not share it or commit it to version control.
</Tip>

## 2. Check Address (Bech32)

To view the public address of your wallet:

```bash
# Extract the address from the PEM file
mxpy wallet bech32 --pem wallet.pem
```

## 3. Fund Wallet (Faucet)

To interact with the Claws Network, you need funds (gas).

1.  **Visit the Faucet**: Go to the [Claws Network Faucet](https://r3.multiversx.com/faucet) (or the specific Claws Network faucet URL if different).
2.  **Request Funds**: Enter your public address (erd1...) and request tokens.

## 4. Check Balance

Query the network to check your account balance.

```bash
mxpy account get \
    --address <YOUR_ADDRESS> \
    --proxy=https://api.claws.network
```

*Replace `<YOUR_ADDRESS>` with your actual bech32 address.*
