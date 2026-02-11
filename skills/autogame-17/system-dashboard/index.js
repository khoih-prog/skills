const fs = require('fs');
const os = require('os');
const path = require('path');
const { execSync } = require('child_process');

// Configuration
const LOG_DIR = path.join(__dirname, '../../memory/logs');
const EVENTS_FILE = path.join(__dirname, '../../memory/events.jsonl');
const CRON_CMD = 'openclaw cron status';
const SKILLS_DIR = path.join(__dirname, '../../skills');

// Helper: Run command and return output
function runCmd(cmd) {
    try {
        return execSync(cmd, { encoding: 'utf8', timeout: 5000 }).trim();
    } catch (e) {
        return null;
    }
}

// 1. System Metrics
function getSystemMetrics() {
    const uptime = (os.uptime() / 3600).toFixed(1) + 'h';
    const load = os.loadavg()[0].toFixed(2);
    const totalMem = (os.totalmem() / 1024 / 1024 / 1024).toFixed(1);
    const freeMem = (os.freemem() / 1024 / 1024 / 1024).toFixed(1);
    const usedMem = (totalMem - freeMem).toFixed(1);
    
    let diskUsage = 'Unknown';
    try {
        const df = runCmd('df -h / | tail -1 | awk "{print $5}"');
        if (df) diskUsage = df;
    } catch (e) {}

    return { uptime, load, usedMem, totalMem, diskUsage };
}

// 2. Evolver Status
function getEvolverStatus() {
    if (!fs.existsSync(EVENTS_FILE)) return { status: 'Unknown', lastRun: 'Never', successRate: '0%' };
    
    const lines = fs.readFileSync(EVENTS_FILE, 'utf8').split('\n').filter(l => l.trim());
    const total = lines.length;
    const lastEvent = total > 0 ? JSON.parse(lines[total - 1]) : null;
    
    const successCount = lines.filter(l => l.includes('"status":"success"')).length;
    const rate = total > 0 ? Math.round((successCount / total) * 100) : 0;
    
    return {
        status: lastEvent ? lastEvent.outcome?.status || 'unknown' : 'none',
        lastRun: lastEvent ? new Date(parseInt(lastEvent.id.split('_')[1])).toISOString().split('T')[0] : 'Never',
        successRate: rate + '%',
        totalCycles: total
    };
}

// 3. Log Analysis
function getLogStats(days = 1) {
    if (!fs.existsSync(LOG_DIR)) return { errorCount: 0, recentErrors: [] };
    
    const files = fs.readdirSync(LOG_DIR).filter(f => f.endsWith('.md')).sort().reverse().slice(0, days);
    let errorCount = 0;
    let recentErrors = [];
    
    files.forEach(file => {
        const content = fs.readFileSync(path.join(LOG_DIR, file), 'utf8');
        const matches = content.match(/error|fail|exception/gi) || [];
        errorCount += matches.length;
        
        // Extract context lines
        const lines = content.split('\n');
        lines.forEach((line, i) => {
            if (/error|fail|exception/i.test(line)) {
                recentErrors.push(`[${file}] ${line.trim().substring(0, 80)}...`);
            }
        });
    });
    
    return { errorCount, recentErrors: recentErrors.slice(0, 5) };
}

// 4. Cron Status
function getCronStats() {
    try {
        const output = runCmd(CRON_CMD); // JSON output expected? check openclaw cron status
        // openclaw cron status returns JSON: { jobs: 41, ... }
        if (output && output.startsWith('{')) {
            const data = JSON.parse(output);
            return { jobCount: data.jobs, enabled: data.enabled };
        }
        return { jobCount: '?', enabled: false };
    } catch (e) {
        return { jobCount: 'Error', enabled: false };
    }
}

// 5. Skill Health
function getSkillStats() {
    if (!fs.existsSync(SKILLS_DIR)) return { total: 0, broken: 0 };
    const skills = fs.readdirSync(SKILLS_DIR).filter(f => fs.statSync(path.join(SKILLS_DIR, f)).isDirectory());
    const broken = skills.filter(s => !fs.existsSync(path.join(SKILLS_DIR, s, 'SKILL.md'))).length;
    return { total: skills.length, broken };
}

// Main Execution
async function main() {
    const sys = getSystemMetrics();
    const evo = getEvolverStatus();
    const logs = getLogStats();
    const cron = getCronStats();
    const skills = getSkillStats();
    
    // Determine Color
    let color = 'green';
    let statusText = 'Systems Nominal';
    
    if (parseInt(sys.diskUsage) > 80 || logs.errorCount > 10 || skills.broken > 5) {
        color = 'orange';
        statusText = 'Warnings Detected';
    }
    if (parseInt(sys.diskUsage) > 90 || logs.errorCount > 50 || evo.status === 'failed') {
        color = 'red';
        statusText = 'Critical Issues';
    }
    
    // Build Markdown
    const report = [
        `**System Health**`,
        `- **Uptime:** ${sys.uptime}`,
        `- **Load:** ${sys.load}`,
        `- **Memory:** ${sys.usedMem}GB / ${sys.totalMem}GB`,
        `- **Disk:** ${sys.diskUsage} used`,
        ``,
        `**Evolver Status**`,
        `- **Last Run:** ${evo.status.toUpperCase()} (${evo.lastRun})`,
        `- **Success Rate:** ${evo.successRate} (${evo.totalCycles} cycles)`,
        ``,
        `**Operations**`,
        `- **Cron Jobs:** ${cron.jobCount} (Enabled: ${cron.enabled})`,
        `- **Skills:** ${skills.total} (Broken: ${skills.broken})`,
        `- **Recent Errors:** ${logs.errorCount}`,
        logs.recentErrors.length > 0 ? `\n> ${logs.recentErrors.join('\n> ')}` : ''
    ].join('\n');
    
    console.log(report);
    
    // Send to Feishu
    const target = process.argv.includes('--target') ? process.argv[process.argv.indexOf('--target') + 1] : null;
    
    // Use feishu-card send_safe.js
    const sendScript = path.join(__dirname, '../../skills/feishu-card/send_safe.js');
    if (fs.existsSync(sendScript)) {
        // Write temp file
        const tmpFile = path.join(os.tmpdir(), `dashboard_${Date.now()}.md`);
        fs.writeFileSync(tmpFile, report);
        
        let cmd = `node "${sendScript}" --text-file "${tmpFile}" --title "📊 System Dashboard: ${statusText}" --color "${color}"`;
        if (target) cmd += ` --target "${target}"`;
        
        console.log(`Sending dashboard to Feishu...`);
        try {
            execSync(cmd, { stdio: 'inherit' });
        } catch (e) {
            console.error('Failed to send card:', e.message);
        }
        
        fs.unlinkSync(tmpFile);
    } else {
        console.log('feishu-card skill not found. Skipping send.');
    }
}

main().catch(console.error);
