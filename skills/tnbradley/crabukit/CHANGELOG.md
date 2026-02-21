# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.1] - 2026-02-21

### Added
- Test suite with 7 pytest tests for CI/CD
- `crabukit install` command for native safe installation
- Clawdex integration (external scanner support)
- Shell wrapper script (claw-safe-install.sh / csi)

### Fixed
- Security review findings: Fixed fake email references
- Security review findings: Clarified defensive nature of prompt injection patterns
- Security review findings: Fixed metadata mismatch in SKILL.md
- Documentation: Fixed all github.com/troy references to github.com/tnbradley

### Security
- All contact info now points to real GitHub resources
- Added defensive comments explaining security scanning patterns

## [0.1.0] - 2026-02-20

### Added
- Initial release of Crabukit - comprehensive OpenClaw skill security scanner
- **Prompt Injection Detection**: Direct, indirect, encoded, and typoglycemia attacks
- **Code Vulnerability Detection**: eval(), exec(), shell injection, path traversal
- **Secret Detection**: AWS keys, GitHub tokens, OpenAI keys, JWTs, private keys
- **AI Malware Detection**: PROMPTFLUX/PROMPTSTEAL-style patterns
- **Supply Chain Detection**: Typosquatting, homoglyphs, hidden files
- **Tool Combination Analysis**: Detects dangerous tool pairings (Confused Deputy)
- **Backdoor Detection**: Cron jobs, SSH keys, persistent execution
- Rich CLI output with severity colors and recommendations
- JSON output format for automation
- CI/CD integration with exit codes
- Comprehensive test suite with malicious skill fixtures

### Security
- Based on OWASP LLM Top 10
- Incorporates Lakera AI Q4 2025 research
- Implements Google Threat Intelligence malware patterns
- Protects against WithSecure's ReAct Confused Deputy attacks

[0.1.1]: https://github.com/tnbradley/crabukit/releases/tag/v0.1.1
[0.1.0]: https://github.com/tnbradley/crabukit/releases/tag/v0.1.0
