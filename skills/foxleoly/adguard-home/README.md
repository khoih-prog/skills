# 🛡️ AdGuard Home Skill

Query AdGuard Home instances for DNS statistics, blocked domains, filter rules, and configuration.

## Features

- 📊 DNS query and blocking statistics
- 💻 Top clients ranking
- 🚫 Blocked domains leaderboard
- 🔧 Service status monitoring
- 🌐 DNS configuration details
- 🛡️ Filter rules inspection
- 📜 Recent query log
- 👥 Client management
- 🔒 TLS/encryption status
- ✅ Multi-instance support

## Installation

### Via ClawHub (Recommended)

```bash
clawhub install adguard-home
```

### Manual Installation

Copy this skill folder to your OpenClaw workspace:

```bash
cp -r skills/adguard-home ~/.openclaw/workspace/skills/
```

## Configuration

### 🔒 Security Best Practices

**⚠️ Important:** Never store plaintext credentials in files. Always use secure credential injection.

#### Option 1: Environment Variables (Recommended)

```bash
export ADGUARD_URL="http://192.168.145.249:1080"
export ADGUARD_USERNAME="admin"
export ADGUARD_PASSWORD="your-secure-password"
```

Add to your shell profile (`~/.bashrc`, `~/.zshrc`) for persistence.

#### Option 2: 1Password CLI (Most Secure)

```bash
export ADGUARD_URL=$(op read "op://vault/AdGuard/url")
export ADGUARD_USERNAME=$(op read "op://vault/AdGuard/username")
export ADGUARD_PASSWORD=$(op read "op://vault/AdGuard/password")
```

**❌ Deprecated: File-based Config**

Previous versions allowed creating `adguard-instances.json` with credentials. **This is no longer recommended** due to the risk of accidental commits and plaintext storage. Migrate to environment variables or 1Password.

## Usage

```bash
# Statistics
/adguard stats [instance]
/adguard top-clients [instance]
/adguard top-blocked [instance]

# Status & Configuration
/adguard status [instance]
/adguard dns-info [instance]
/adguard filter-rules [instance]
/adguard tls-status [instance]
/adguard clients [instance]

# Query Log
/adguard querylog [instance] [limit]

# Health Check
/adguard health [instance]
```

## Examples

```bash
# Check DNS statistics
/adguard stats dns1

# View service status
/adguard status dns1

# See DNS configuration
/adguard dns-info dns1

# View filter rules
/adguard filter-rules dns1

# Check last 20 queries
/adguard querylog dns1 20
```

## Version

**v1.2.2** - Removed file-based credential storage, env vars and 1Password only

## Author

**Leo Li (@foxleoly)**

## License

MIT
