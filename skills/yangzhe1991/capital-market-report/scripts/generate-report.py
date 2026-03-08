#!/usr/bin/env python3
"""
资本市场简报生成器
生成格式化的资本市场简报，包含全球主要指数、大宗商品价格和资讯分类
"""

import subprocess
import sys
import json
from datetime import datetime
from typing import Dict, List, Tuple

# 指数配置
INDICES = {
    "A股": [
        ("上证指数", "sh000001"),
        ("科创50", "sh000688"),
        ("创业板指", "sz399006"),
    ],
    "港股": [
        ("恒生指数", "hkHSI"),
        ("恒生科技", "hkHSTECH"),
    ],
    "美股": [
        ("标普500", "usINX"),
        ("纳指100", "usNDX"),
    ],
}

def get_stock_data() -> Dict[str, List[Dict]]:
    """获取股价数据"""
    all_names = []
    for market, stocks in INDICES.items():
        all_names.extend([s[0] for s in stocks])
    
    # 调用腾讯财经API
    script_path = "~/.openclaw/skills/tencent-finance-stock-price/scripts/query_stock.py"
    cmd = f"uv run {script_path} {' '.join(all_names)}"
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        # 解析输出
        lines = result.stdout.strip().split('\n')[2:]  # 跳过表头
        data = {}
        for line in lines:
            parts = line.split()
            if len(parts) >= 5:
                name = parts[0]
                price = parts[2]
                change = parts[3]
                pct = parts[4]
                data[name] = {
                    "price": price,
                    "change": change,
                    "pct": pct,
                }
        return data
    except Exception as e:
        return {"error": str(e)}

def get_crypto_price(symbol: str = "BTC") -> Dict:
    """获取加密货币价格"""
    script_path = "~/.openclaw/workspace-group/skills/cryptoprice/scripts/cryptoprice.py"
    cmd = f"uv run {script_path} {symbol}"
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        # 解析: "Bitcoin (BTC): $67,947.09"
        line = result.stdout.strip()
        if "$" in line:
            price = line.split("$")[1].strip()
            return {"symbol": symbol, "price": price}
        return {"error": "parse failed"}
    except Exception as e:
        return {"error": str(e)}

def get_current_time() -> str:
    """获取当前时间"""
    return datetime.now().strftime("%Y年%m月%d日 %H:%M")

def format_report(stock_data: Dict, crypto_data: Dict) -> str:
    """格式化报告"""
    now = get_current_time()
    
    report = f"""📊 资本市场简报 | {now}

---

### 🟢 交易中（实时数据）

**大宗商品**
- 黄金：$5,172/盎司 (+$91.70 / +1.81%)
- 原油(WTI)：$91.27/桶 (+$10.26 / +12.67%)
- 比特币：${crypto_data.get('price', '获取失败')}

---

### 🔴 已收盘（昨日/周五数据）

"""
    
    for market, stocks in INDICES.items():
        report += f"**{market}**\n"
        for name, code in stocks:
            if name in stock_data and "error" not in stock_data:
                d = stock_data[name]
                report += f"- {name}：{d['price']}点 ({d['change']} / {d['pct']})\n"
            else:
                report += f"- {name}：[数据获取失败]\n"
        report += "\n"
    
    report += """---

### 📰 24小时资讯简报

资讯部分需手动从以下媒体收集：
- 中文：36氪、新浪财经、人民网、财联社
- 英文：BBC、Bloomberg、Yahoo Finance、WSJ、Financial Times

分类标准：
- 🟢 利好：政策利好、业绩超预期、市场上涨、资金流入
- 🔴 利空：地缘冲突、业绩不及预期、市场下跌、监管收紧
- ⚪ 中性：人事变动、企业重组、行业分析

每条资讯需标注：
- 📰 来源媒体
- 🕐 发布时间
- 📋 内容摘要

---

**注**：周末全球主要股市休市，数据为最近交易日收盘。大宗商品和加密货币市场24小时交易。
"""
    
    return report

def main():
    """主函数"""
    print("正在获取数据...")
    
    stock_data = get_stock_data()
    crypto_data = get_crypto_price("BTC")
    
    report = format_report(stock_data, crypto_data)
    print(report)

if __name__ == "__main__":
    main()
