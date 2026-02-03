# Smart Contract Interaction

This guide covers deploying, upgrading, and interacting with smart contracts on the Claws Network.

## 1. Build Contract

Ensure you have built your contract to a WASM file.

```bash
# Example build command (using mxpy in a contract directory)
mxpy contract build
```

## 2. Deploy Contract

Deploy a compiled WASM file to the network.

```bash
mxpy contract deploy \
    --bytecode="./output/contract.wasm" \
    --recall-nonce \
    --gas-limit=60000000 \
    --proxy=https://api.claws.network \
    --chain=D \
    --pem="wallet.pem" \
    --send
    # Add --arguments if the contract has a constructor
```

**Output**: The command returns a transaction hash and the computed contract address.

## 3. Upgrade Contract

Upgrade the code of an existing contract. Only the owner can do this.

```bash
mxpy contract upgrade <CONTRACT_ADDRESS> \
    --bytecode="./output/contract.wasm" \
    --recall-nonce \
    --gas-limit=60000000 \
    --proxy=https://api.claws.network \
    --chain=D \
    --pem="wallet.pem" \
    --send
```

## 4. Interact (Execute)

Call a function on the smart contract (write operation).

```bash
mxpy contract call <CONTRACT_ADDRESS> \
    --function="myFunction" \
    --arguments 123 str:example \
    --recall-nonce \
    --gas-limit=10000000 \
    --proxy=https://api.claws.network \
    --chain=D \
    --pem="wallet.pem" \
    --send
```

## 5. Query (Read-Only)

Read state from the smart contract without gas costs.

```bash
mxpy contract query <CONTRACT_ADDRESS> \
    --function="myViewFunction" \
    --arguments <ARGS_IF_ANY> \
    --proxy=https://api.claws.network
```
