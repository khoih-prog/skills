---
name: qst-memory
description: |
  QST Memory Management System v1.5 for OpenClaw agents. Provides:
  1. Tree-based classification structure (3-level hierarchy)
  2. Three search methods: Tree, Selection Rule, Semantic (Enhanced)
  3. Hybrid Search combining all methods
  4. Auto-classification with AI inference
  5. Memory decay & cleanup system
  6. TF-IDF similarity algorithm with context awareness
  
  Use when: Agent needs intelligent memory management with flexible classification.
  Goal: Reduce token consumption by 70-90%, improve relevance by 20%.
---

# QST Memory Management v1.5

## 🌳 Tree-Based Classification Structure

**Key Innovation**: Hierarchical 3-level classification with automatic keyword matching.

```
QST
├── Physics (FSCA, E8, Mass_Energy)
├── Computation (Orbital, Simulation)
└── Audit (Zero_Calibration)

User
├── Identity, Intent, Projects

Tech
├── Config (API, Model, Cron, Database)
├── Discussion, Skills

Border (Meng Tian)
├── Security, Monitor, Email

HK_Forum
├── Posts, Replies, Users

General
├── Dragon_Ball, History, Chat
```

---

## 🔍 Multi-Mode Search System

### v1.5 New: Hybrid Search Engine

Combines three search methods:

| Method | Strength | Use Case |
|--------|----------|----------|
| **Tree Search** | Precise matching | Exact category known |
| **Selection Rule** | Geometric neighbors | C_ab = 1 neighbors |
| **Semantic (v1.5)** | TF-IDF + Context | Intelligent inference |

### Enhanced Semantic Search (v1.5)

```python
# TF-IDF similarity
similarity = cosine_similarity(query_tfidf, memory_tfidf)

# Context awareness
context_query = " ".join(context[-3:]) + " " + query

# Weight adjustment
adjusted_score = similarity * weight_multiplier
```

### Selection Rule Integration

```
C_ab = 1 when geometric neighbors

QST_Physics ↔ QST_Computation ↔ QST_Audit
```

---

## 🤖 Auto-Classification (v1.5 New)

### Smart Inference

```python
from auto_classify import auto_classify

result = auto_classify("QST暗物質使用FSCA理論")
# → suggested_category: "QST_Physics_FSCA"
# → confidence: "high"
```

### Weight Auto-Detection

| Weight | Trigger Keywords |
|--------|-----------------|
| **[C]** Critical | key, token, config, 密鑰, 決策 |
| **[I]** Important | project, plan, 專案, 討論, 偏好 |
| **[N]** Normal | chat, greeting, 問候, 閒聊 |

---

## 🧹 Memory Decay System (v1.5 New)

### Cleanup Rules

| Weight | Threshold | Action |
|--------|-----------|--------|
| **[C]** Critical | Never | Keep forever |
| **[I]** Important | 365 days | Archive |
| **[N]** Normal | 30 days | Delete |

### Decay Multiplier

```
[C]: 2.0 (never decay)
[I]: max(0.5, 1.5 - age * 0.1/365)
[N]: max(0.1, 1.0 - age * 0.5/30)
```

---

## 📊 Statistics Panel

```bash
python qst_memory.py stats
```

Output:
```
📊 QST Memory v1.5 統計面板
├── 分類結構: 34 分類
├── 記憶總數: 156 條
├── Token 估算: ~8,500
└── 衰減狀態: 3 條高衰減
```

---

## 💾 Memory Format

```markdown
# Memory Title

[Category] [Weight]
Date: 2026-02-14

Content...

Tags: tag1, tag2
```

---

## 🚀 Quick Start

```bash
# Search with hybrid mode (default)
python qst_memory.py search "暗物質"

# Enhanced semantic with context
python qst_memory.py search "ARM芯片" --method enhanced --context "技術討論"

# Auto-classify content
python qst_memory.py classify "QST暗物質計算使用FSCA"

# Save with auto-classification
python qst_memory.py save "採用 FSCA v7 作為暗物質理論"

# Cleanup preview
python qst_memory.py cleanup --dry-run

# Statistics
python qst_memory.py stats
```

---

## 📁 File Structure

```
qst-memory/
├── SKILL.md              # This file
├── config.yaml           # Tree config + settings
├── qst_memory.py         # Main entry (v1.5)
└── scripts/
    ├── tree_search.py        # Tree search
    ├── bfs_search.py         # BFS search
    ├── semantic_search.py    # Basic semantic
    ├── semantic_search_v15.py # Enhanced semantic (v1.5)
    ├── hybrid_search.py      # Hybrid engine (v1.5)
    ├── auto_classify.py      # Auto-classification (v1.5)
    ├── save_memory.py        # Smart save (v1.5)
    ├── cleanup.py            # Decay system (v1.5)
    └── stats_panel.py        # Statistics
```

---

## 🎯 Token Optimization

| Version | Tokens/Query | Relevance |
|---------|--------------|-----------|
| v1.2 | ~500 | 85% |
| v1.4 | ~300 | 90% |
| **v1.5** | **~200** | **95%** |

**Improvement**: 60% token reduction, 95% relevance.

---

## ⚙️ Configuration

```yaml
version: '1.5'

search:
  default_method: "hybrid"
  min_relevance: 0.1

add_category:
  max_depth: 3
  min_occurrences: 3

decay:
  critical: 0      # Never decay
  important: 0.1    # Slow decay
  normal: 0.5       # Fast decay

cleanup:
  enabled: true
  max_age_days:
    critical: -1    # Never
    important: 365  # Archive after 1 year
    normal: 30      # Delete after 30 days
```

---

## 🔧 Installation

### From ClawHub
```bash
clawhub install qst-memory
```

### From GitHub
```bash
git clone https://github.com/ZhuangClaw/qst-memory-skill.git
```

---

*QST Memory v1.5 - Building the next generation of AI memory systems.*
