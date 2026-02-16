import {
  Connection,
  Keypair,
  PublicKey,
  SystemProgram,
  Transaction,
  sendAndConfirmTransaction,
  LAMPORTS_PER_SOL,
} from "@solana/web3.js";
import dotenv from "dotenv";
import path from "path";

// Load environment variables from the root .env file
dotenv.config({ path: path.resolve(process.cwd(), ".env") });

const BURN_ADDRESS = new PublicKey("11111111111111111111111111111111"); // System Program default burn address (or just a dead address)
const AMOUNT_TO_BURN = 0.001 * LAMPORTS_PER_SOL; // Example amount: 0.001 SOL.  Adjust as needed or make configurable.

// Helper to post data to API
async function postToApi(endpoint: string, data: any) {
  const apiUrl = process.env.API_URL;
  if (!apiUrl) {
    console.warn("API_URL not set in .env, skipping API report.");
    return;
  }

  try {
    const response = await fetch(`${apiUrl}${endpoint}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
        console.error(`Failed to post to API: ${response.status} ${response.statusText}`);
    } else {
        console.log(`Successfully reported to API: ${endpoint}`);
    }
  } catch (error) {
    console.error("Error posting to API:", error);
  }
}

async function main() {
  const privateKeyString = process.env.CREATOR_WALLET_PRIVATE_KEY;
  const tokenAddress = process.env.PUMP_FUN_TOKEN_ADDRESS || "unknown"; // For reporting context

  if (!privateKeyString) {
    console.error("Error: CREATOR_WALLET_PRIVATE_KEY is not set in .env");
    process.exit(1);
  }

  // Decode private key (assuming base58 string or JSON array)
  let secretKey: Uint8Array;
  try {
    if (privateKeyString.startsWith("[") && privateKeyString.endsWith("]")) {
      secretKey = Uint8Array.from(JSON.parse(privateKeyString));
    } else {
         secretKey = Uint8Array.from(JSON.parse(privateKeyString));
    }
  } catch (e) {
    const errorMsg = "Error parsing private key. Ensure it is a JSON array of numbers.";
    console.error(errorMsg);
    console.error(e);
    // Report failure
    await postToApi("/api/burn/transaction", {
        status: "failed",
        error: errorMsg,
        tokenAddress
    });
    process.exit(1);
  }

  const payer = Keypair.fromSecretKey(secretKey);
  const connection = new Connection("https://api.mainnet-beta.solana.com", "confirmed");

  console.log(`Wallet Public Key: ${payer.publicKey.toBase58()}`);

  try {
    const balance = await connection.getBalance(payer.publicKey);
    console.log(`Current Balance: ${balance / LAMPORTS_PER_SOL} SOL`);

    if (balance < AMOUNT_TO_BURN + 5000) { // +5000 lamports for fees
        const errorMsg = "Insufficient balance to burn and pay fees.";
        console.error(errorMsg);
        await postToApi("/api/burn/transaction", {
            status: "failed",
            error: errorMsg,
            tokenAddress,
            wallet: payer.publicKey.toBase58()
        });
        process.exit(1);
    }

    const transaction = new Transaction().add(
        SystemProgram.transfer({
        fromPubkey: payer.publicKey,
        toPubkey: BURN_ADDRESS,
        lamports: AMOUNT_TO_BURN,
        })
    );

    console.log(`Burning ${AMOUNT_TO_BURN / LAMPORTS_PER_SOL} SOL to ${BURN_ADDRESS.toBase58()}...`);

    const signature = await sendAndConfirmTransaction(connection, transaction, [payer]);
    console.log(`Burn successful! Transaction signature: ${signature}`);

    await postToApi("/api/burn/transaction", {
        status: "success",
        signature,
        amount: AMOUNT_TO_BURN / LAMPORTS_PER_SOL,
        tokenAddress,
        wallet: payer.publicKey.toBase58()
    });

  } catch (error: any) {
    console.error("Error burning SOL:", error);
    await postToApi("/api/burn/transaction", {
        status: "failed",
        error: error.message || String(error),
        tokenAddress,
        wallet: payer.publicKey.toBase58()
    });
    process.exit(1);
  }
}

main().catch((err) => {
  console.error("Unexpected error:", err);
  process.exit(1);
});
