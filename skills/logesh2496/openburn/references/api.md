# Openburn API Specifications

Base URL: `{API_URL}` (User provided)

## 1. Register Token & Wallet

**Endpoint**: `/api/burn/register`
**Method**: `POST`

**Request Body**:

```json
{
  "tokenAddress": "string", // The Solana token address (e.g. Pump.fun token)
  "creatorWallet": "string" // The creator's wallet address (Public Key)
}
```

**Expected Response**:

- **200 OK**: Registration successful.
- **400 Bad Request**: Missing fields.

---

## 2. Report Scheduled Job

**Endpoint**: `/api/burn/schedule`
**Method**: `POST`

**Request Body**:

```json
{
  "jobId": "string", // e.g. "openburn-job"
  "intervalMs": "number" // Schedule interval in milliseconds (e.g. 7200000)
}
```

**Expected Response**:

- **200 OK**: Schedule logged.

---

## 3. Report Transaction Status

**Endpoint**: `/api/burn/transaction`
**Method**: `POST`

**Request Body (Success)**:

```json
{
  "status": "success",
  "signature": "string", // Solana transaction signature
  "amount": "number", // Amount burned in SOL
  "tokenAddress": "string", // Context: Pump.fun token address
  "wallet": "string" // Wallet address performed the burn
}
```

**Request Body (Failure)**:

```json
{
  "status": "failed",
  "error": "string", // Error message description
  "tokenAddress": "string",
  "wallet": "string" // (Optional) if available
}
```

**Expected Response**:

- **200 OK**: Log accepted.
