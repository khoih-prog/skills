---
name: chart-splat
description: Generate beautiful charts via the Chart Splat API. Use when the user asks to create, generate, or visualize data as charts, graphs, or plots. Supports line, bar, pie, doughnut, radar, and polar area charts. Returns PNG images.
version: 1.0.0
license: MIT
compatibility: Requires Node.js and npx with network access to api.chartsplat.com
metadata:
  author: workingdevshero
  version: "1.0.0"
  homepage: https://chartsplat.com
  openclaw:
    requires:
      env:
        - CHARTSPLAT_API_KEY
      bins:
        - node
        - npx
    primaryEnv: CHARTSPLAT_API_KEY
    emoji: "bar-chart"
    homepage: https://chartsplat.com
    os:
      - darwin
      - linux
      - win32
    install:
      - kind: node
        package: chartsplat-cli
        bins: [chartsplat]
        label: "Install Chart Splat CLI via npm"
---

# Chart Splat

Generate beautiful charts from data using the Chart Splat API. Charts are rendered server-side with Chart.js and returned as PNG images.

## Supported Chart Types

| Type | Best For |
|------|----------|
| `line` | Trends over time |
| `bar` | Comparing categories |
| `pie` | Parts of a whole |
| `doughnut` | Parts of a whole (with center space) |
| `radar` | Multivariate comparison |
| `polarArea` | Comparing categories with radial layout |

## Method 1: CLI (Preferred)

Use the `chartsplat` CLI via npx. No install required.

```bash
npx -y chartsplat-cli bar \
  --labels "Q1,Q2,Q3,Q4" \
  --data "50,75,60,90" \
  --title "Quarterly Revenue" \
  --color "#8b5cf6" \
  -o chart.png
```

### CLI Options

| Flag | Description |
|------|-------------|
| `-l, --labels <csv>` | Comma-separated labels |
| `-d, --data <csv>` | Comma-separated numeric values |
| `-t, --title <text>` | Chart title |
| `--label <text>` | Dataset label for legend |
| `-c, --color <hex>` | Background color |
| `-w, --width <px>` | Image width (default: 800) |
| `--height <px>` | Image height (default: 600) |
| `-o, --output <file>` | Output file path (default: chart.png) |
| `--config <file>` | JSON config file for complex charts |

### CLI Chart Commands

```bash
npx -y chartsplat-cli line -l "Mon,Tue,Wed,Thu,Fri" -d "100,200,150,300,250" -o line.png
npx -y chartsplat-cli bar -l "A,B,C" -d "10,20,30" -o bar.png
npx -y chartsplat-cli pie -l "Red,Blue,Green" -d "30,50,20" -o pie.png
npx -y chartsplat-cli doughnut -l "Yes,No,Maybe" -d "60,25,15" -o doughnut.png
npx -y chartsplat-cli radar -l "Speed,Power,Range,Durability,Precision" -d "80,90,70,85,95" -o radar.png
npx -y chartsplat-cli polararea -l "N,E,S,W" -d "40,30,50,20" -o polar.png
```

### Complex Charts via Config File

For multi-dataset or customized charts, write a JSON config file then pass it to the CLI:

```bash
npx -y chartsplat-cli bar --config chart-config.json -o chart.png
```

See [examples/sample-charts.json](examples/sample-charts.json) for config file examples and [references/api-reference.md](references/api-reference.md) for the full config schema.

## Method 2: Helper Script

Use the bundled script for quick generation without installing the CLI:

```bash
node scripts/generate-chart.js bar "Q1,Q2,Q3,Q4" "50,75,60,90" "Revenue" chart.png
```

Or with a config file:

```bash
node scripts/generate-chart.js --config chart-config.json -o chart.png
```

## Output Handling

- Charts are saved as PNG files to the specified output path
- Default output is `chart.png` in the current directory
- For messaging platforms (Discord, Slack), return the file path: `MEDIA: /path/to/chart.png`
- The CLI and helper script handle base64 decoding automatically

## Error Handling

| Error | Cause | Fix |
|-------|-------|-----|
| `API key required` | Missing `CHARTSPLAT_API_KEY` | Set the env var in agent config |
| `Invalid API key` | Wrong or revoked key | Generate a new key at chartsplat.com/dashboard |
| `Rate limit exceeded` | Monthly quota reached | Upgrade plan or wait for reset |
| `Invalid chart configuration` | Bad request payload | Check that `data.labels` and `data.datasets` are present |

## Tips

- Always provide both `labels` and `data` arrays of the same length
- Use hex colors (e.g., `#8b5cf6`) for consistent styling
- For pie/doughnut charts, use an array of colors for `backgroundColor` to color each segment
- Default dimensions (800x600) work well for most uses; increase for presentations
- The `--config` flag accepts any valid Chart.js configuration for full customization
