# AdGuard Home Skill

🛡️ Query AdGuard Home instances for DNS statistics, blocked domains, and client activity

---

## Features

- ✅ Multi-instance support
- ✅ Real-time DNS query statistics
- ✅ Blocked domains leaderboard
- ✅ Active client analysis
- ✅ Health status check
- ✅ Service status monitoring
- ✅ DNS configuration details
- ✅ Filter rules inspection
- ✅ Recent query log
- ✅ TLS/encryption status

---

## Usage

### Basic Commands

```bash
# Statistics & Monitoring
/adguard stats [instance]           # DNS statistics
/adguard top-clients [instance]     # Top 10 active clients
/adguard top-blocked [instance]     # Top 10 blocked domains
/adguard health [instance]          # Health check
/adguard status [instance]          # Service status

# Configuration & Rules
/adguard dns-info [instance]        # DNS configuration
/adguard filter-rules [instance]    # Filter rules and lists
/adguard clients [instance]         # Configured clients
/adguard tls-status [instance]      # TLS/encryption status

# Query Log
/adguard querylog [instance] [n]    # Recent n queries (default: 10)
```

### Examples

```bash
# Query dns1 instance statistics
/adguard stats dns1

# Check service status
/adguard status dns1

# View DNS configuration
/adguard dns-info dns1

# View filter rules
/adguard filter-rules dns1

# View last 20 DNS queries
/adguard querylog dns1 20

# Check TLS status
/adguard tls-status dns1

# If no instance specified, uses the first configured instance
/adguard stats
```

### Output Examples

**stats command:**
```
📊 AdGuard Home Statistics (dns1)
Total DNS Queries: 141,647
Blocked Requests: 32,540 (23.0%)
Avg Response Time: 0.005ms
```

**status command:**
```
🔧 AdGuard Home Status (dns1)
Version: v0.107.72
Running: ✅ Yes
Protection: ✅ Enabled
DNS Port: 53
HTTP Port: 1080
Language: zh-cn
DHCP Available: ✅ Yes
```

**dns-info command:**
```
🌐 DNS Configuration (dns1)
Protection: ✅ Enabled
Rate Limit: 20 req/s
Upstream Mode: parallel
Cache: ✅ 4MB
DNSSEC: ❌ Disabled
IPv6: ✅ Enabled

Upstream DNS Servers:
  1. https://dns.alidns.com/dns-query
  2. 192.168.1.1:53
  3. 8.8.8.8:53
```

**filter-rules command:**
```
🛡️ Filter Rules (dns1)
Filtering: ✅ Enabled
Update Interval: 12 hours
User Rules: 6 custom rules

Filter Lists:
  1. ✅ AdAway Default Blocklist (6540 rules)
  2. ✅ gh_100M_block (1110461 rules)
  3. ✅ Delta Force Blacklist (78126 rules)
```

**querylog command:**
```
📜 Recent DNS Queries (dns1) - Last 5 entries

1. [12:26:44 AM] 🚫 BLOCKED api.telegram.org (192.168.145.188)
2. [12:26:43 AM] 🚫 BLOCKED self.events.data.microsoft.com (192.168.145.123)
   Rule: ||events.data.microsoft.com^
3. [12:26:42 AM] ✅ OK open.feishu.cn (192.168.145.188)
```

---

## Configuration

### 🔒 Security Best Practices

**⚠️ Important:** Never store plaintext credentials in files. Always use secure credential injection:

#### Option 1: Environment Variables (Recommended)

Set environment variables before running commands:

```bash
export ADGUARD_URL="http://192.168.145.249:1080"
export ADGUARD_USERNAME="admin"
export ADGUARD_PASSWORD="your-secure-password"
```

Add these to your shell profile (`~/.bashrc`, `~/.zshrc`) for persistence.

#### Option 2: 1Password CLI (Most Secure)

Use `op read` to inject secrets at runtime:

```bash
export ADGUARD_URL=$(op read "op://vault/AdGuard/url")
export ADGUARD_USERNAME=$(op read "op://vault/AdGuard/username")
export ADGUARD_PASSWORD=$(op read "op://vault/AdGuard/password")
```

**❌ Deprecated: File-based Config**

Previous versions allowed creating `adguard-instances.json` with credentials. **This is no longer supported** due to the risk of accidental commits and plaintext storage. Migrate to environment variables or 1Password.

---

### Configuration Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `url` | AdGuard Home URL (with port) | `http://192.168.145.249:1080` |
| `username` | Admin username | `admin` |
| `password` | Admin password (use env var or secrets manager) | `your-secure-password` |

---

## Technical Details

- **Authentication:** Cookie-based (POST `/control/login`)
- **Data API:** GET `/control/*` endpoints
- **Runtime:** Node.js (ES Module)
- **Entrypoint:** `index.js`

### API Endpoints Used

- `/control/stats` - Statistics data
- `/control/status` - Service status
- `/control/dns_info` - DNS configuration
- `/control/filtering/status` - Filter rules
- `/control/querylog` - Query log
- `/control/clients` - Client management
- `/control/tls/status` - TLS status

---

## FAQ

**Q: Error "No AdGuard instances configured"?**

A: Set environment variables before running commands:
```bash
export ADGUARD_URL="http://your-adguard:1080"
export ADGUARD_USERNAME="admin"
export ADGUARD_PASSWORD="your-password"
```
Or use 1Password CLI to inject credentials securely.

---

**Q: Authentication error when querying?**

A: Verify username/password. Ensure AdGuard Home service is running.

---

**Q: How to add more instances?**

A: Set additional environment variables with different instance configurations.

---

**Q: querylog shows no data?**

A: Ensure query log is enabled in AdGuard Home settings (Settings → DNS Settings → Query log).

---

## Version History

### v1.2.5 (2026-02-25) - Fix Registry Metadata 🔧

**Bug Fixes:**
- ✅ **Fixed registry metadata** - `clawhub.json` now correctly declares `requires.env` with `ADGUARD_URL`, `ADGUARD_USERNAME`, `ADGUARD_PASSWORD`
- ✅ **Set primaryEnv** - ClawHub store now shows environment variables as required
- ✅ **Updated security notes** - Documents metadata fix

### v1.2.2 (2026-02-25) - Remove File-based Credentials 🔐

**Security Improvements:**
- ✅ **Removed file-based config option** - No longer supports `adguard-instances.json` with plaintext credentials
- ✅ **Env vars only** - Credentials must be provided via environment variables or 1Password
- ✅ **Updated FAQ** - Removed references to config file creation
- ✅ **Clearer warnings** - Explicitly marks file-based config as deprecated and unsupported

### v1.2.1 (2026-02-25) - Credential Security 🔐

**Security Improvements:**
- ✅ **Removed plaintext credential storage** - No longer instructs creating config files with admin credentials
- ✅ **Environment variable support** - Secure credential injection via `ADGUARD_URL`, `ADGUARD_USERNAME`, `ADGUARD_PASSWORD`
- ✅ **1Password integration** - Supports secrets management via `op read`
- ✅ **Removed multi-path search** - No longer searches `~/.openclaw-*/workspace/` paths
- ✅ **Workspace-only config** - Local config file only checked in skill directory (dev use)
- ✅ **Updated documentation** - Security best practices prominently featured

### v1.2.0 (2026-02-24) - Security Hardening 🔒

**Security Improvements:**
- ✅ **Removed command injection vulnerability** - Replaced `execSync` + `curl` with native HTTPS client
- ✅ **Input validation** - Sanitized instance names, commands, and parameters
- ✅ **Command whitelist** - Only allowed commands can be executed
- ✅ **URL validation** - Verified URL format before making requests
- ✅ **Parameter bounds** - Limited querylog limit to 1-100 entries
- ✅ **No shell escaping issues** - Pure JavaScript HTTP requests

**Technical Changes:**
- Removed dependency on `child_process` and external `curl` commands
- Implemented native `http`/`https` module for all API calls
- Added cookie-based session management
- Improved error handling and validation

### v1.1.0 (2026-02-24) - Enhanced

**New Commands:**
- `status` - Service status (version, protection, ports)
- `dns-info` - DNS configuration details
- `filter-rules` - Filter rules and lists
- `querylog [n]` - Recent DNS queries
- `clients` - Configured clients
- `tls-status` - TLS/encryption status

**Improvements:**
- Better error handling
- Enhanced output formatting

### v1.0.0 (2026-02-24) - Initial

**Features:**
- stats/top-clients/top-blocked/health commands
- Multi-instance configuration support
- ES Module implementation

---

## Author

**Leo Li (@foxleoly)**  
License: MIT
