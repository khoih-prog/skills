import fs from "node:fs/promises";
import path from "node:path";
import crypto from "node:crypto";
import os from "node:os";
import { scanDirectoryWithSummary } from "../../../src/security/skill-scanner.ts";

// Heuristic to find workspace root and config dir
const workspaceRoot = process.cwd();
const stateDir = process.env.OPENCLAW_STATE_DIR || path.join(os.homedir(), ".openclaw");
const allowlistPath = path.join(stateDir, "security", "safety-allowlist.json");

async function calculateHash(filePath: string) {
    const buffer = await fs.readFile(filePath);
    return crypto.createHash("sha256").update(buffer).digest("hex");
}

async function checkVirusTotal(hash: string) {
    const apiKey = process.env.VIRUSTOTAL_API_KEY;
    if (!apiKey) {
        throw new Error("VIRUSTOTAL_API_KEY environment variable is not set.");
    }

    const url = `https://www.virustotal.com/api/v3/files/${hash}`;
    const response = await fetch(url, {
        headers: { "x-apikey": apiKey }
    });

    if (response.status === 404) {
        return { unknown: true };
    }

    if (!response.ok) {
        const error = await response.json() as any;
        throw new Error(`VirusTotal API error: ${JSON.stringify(error)}`);
    }

    const data = await response.json() as any;
    const stats = data.data.attributes.last_analysis_stats;
    return {
        malicious: stats.malicious as number,
        suspicious: stats.suspicious as number,
        undetected: stats.undetected as number,
        total: Object.values(stats).reduce((a: any, b: any) => a + b, 0) as number,
        unknown: false,
        link: data.data.links?.self || ""
    };
}

type AllowlistEntry = {
    hash: string;
    verifiedAt: string;
    source: string;
    vtLink?: string;
    originalFile?: string;
};

// Now shifted to a flat array of safe hashes for global verification
type SafetyAllowlist = AllowlistEntry[];

async function run() {
    const isCommit = process.argv.includes("--commit");
    console.log(`🧹 Skill Cleaner starting (${isCommit ? "COMMIT MODE" : "DRY RUN MODE"})...`);
    if (!isCommit) {
        console.log("   (Pass --commit to actually update the safety allowlist)\n");
    }
    
    const skillDirs = ["skills", "my-skills"];
    let allFindings: any[] = [];

    for (const dir of skillDirs) {
        const fullDir = path.join(workspaceRoot, dir);
        try {
            const stats = await fs.stat(fullDir);
            if (!stats.isDirectory()) continue;
            
            console.log(`🔍 Scanning directory: ${dir}...`);
            const summary = await scanDirectoryWithSummary(fullDir);
            const findings = summary.findings.map(f => ({
                ...f,
                file: path.relative(workspaceRoot, f.file)
            }));
            allFindings.push(...findings);
        } catch (err) { }
    }

    if (allFindings.length === 0) {
        console.log("✅ No suspicious patterns found in skills. Nothing to clean.");
        return;
    }

    let allowlist: SafetyAllowlist = [];
    try {
        const data = await fs.readFile(allowlistPath, "utf-8");
        const parsed = JSON.parse(data);
        allowlist = Array.isArray(parsed) ? parsed : [];
    } catch (err) { }

    let cleanedCount = 0;
    const filesToExamine = [...new Set(allFindings.map(f => f.file))];
    
    for (const relFile of filesToExamine) {
        const absolutePath = path.resolve(workspaceRoot, relFile);
        if (!absolutePath.startsWith(workspaceRoot)) continue;

        console.log(`\n🔍 Examining: ${relFile}`);
        
        try {
            const hash = await calculateHash(absolutePath);
            console.log(`   Hash: ${hash}`);
            
            // Check if already allowlisted
            if (allowlist.some(e => e.hash === hash)) {
                console.log("   ✨ File hash is already allowlisted. Skipping VT check.");
                continue;
            }

            const vt = await checkVirusTotal(hash);
            
            if (vt.unknown) {
                console.log("   ❓ VirusTotal has never seen this file. Skipping safe allowlist.");
                continue;
            }
            
            if (vt.malicious === 0 && vt.suspicious === 0) {
                console.log(`   ✅ VirusTotal reports 0 detections. Marking as safe.`);
                
                allowlist.push({
                    hash,
                    verifiedAt: new Date().toISOString(),
                    source: "VirusTotal",
                    vtLink: vt.link,
                    originalFile: relFile.replaceAll("\\", "/")
                });
                cleanedCount++;
            } else {
                console.log(`   ⚠️ VirusTotal detected potential threats: ${vt.malicious} malicious, ${vt.suspicious} suspicious.`);
            }
        } catch (err: any) {
            console.error(`   ❌ Error checking file: ${err.message}`);
        }
    }

    if (cleanedCount > 0) {
        if (isCommit) {
            await fs.mkdir(path.dirname(allowlistPath), { recursive: true });
            await fs.writeFile(allowlistPath, JSON.stringify(allowlist, null, 2));
            console.log(`\n🎉 Success! Added ${cleanedCount} hashes to the safety allowlist.`);
            console.log(`   Allowlist saved to: ${allowlistPath}`);
        } else {
            console.log(`\n💡 Dry run complete. Found ${cleanedCount} files that could be cleaned.`);
            console.log("   Run with --commit to apply changes.");
        }
    } else {
        console.log("\nDone. No new safe hashes found.");
    }
}

run().catch(err => {
    console.error("Fatal error:", err);
    process.exit(1);
});
