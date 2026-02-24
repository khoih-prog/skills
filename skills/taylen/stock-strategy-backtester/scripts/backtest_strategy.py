#!/usr/bin/env python3
"""
Backtest long-only stock strategies from OHLCV CSV data.

The script avoids look-ahead bias by generating a signal on bar t and
executing entries/exits at bar t+1 open.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import asdict, dataclass
from datetime import date, datetime
from pathlib import Path
from statistics import mean, stdev
from typing import Dict, List, Optional, Sequence, Tuple

TRADING_DAYS_PER_YEAR = 252


@dataclass
class Candle:
    date: date
    open_price: float
    high: float
    low: float
    close: float
    volume: float


@dataclass
class Trade:
    entry_date: str
    exit_date: str
    entry_price: float
    exit_price: float
    return_pct: float
    pnl: float
    holding_days: int


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Backtest long-only stock strategies from OHLCV CSV data.",
    )
    parser.add_argument("--csv", required=True, help="Path to OHLCV CSV file.")
    parser.add_argument(
        "--strategy",
        default="sma-crossover",
        choices=["sma-crossover", "rsi-reversion", "breakout"],
        help="Strategy preset to run.",
    )
    parser.add_argument(
        "--initial-capital",
        type=float,
        default=100000.0,
        help="Initial portfolio value.",
    )
    parser.add_argument(
        "--commission-bps",
        type=float,
        default=5.0,
        help="Commission in basis points per side.",
    )
    parser.add_argument(
        "--slippage-bps",
        type=float,
        default=2.0,
        help="Slippage in basis points per side.",
    )
    parser.add_argument(
        "--risk-free-rate",
        type=float,
        default=0.02,
        help="Annual risk-free rate for Sharpe ratio (e.g. 0.02).",
    )

    parser.add_argument("--fast-window", type=int, default=20)
    parser.add_argument("--slow-window", type=int, default=60)
    parser.add_argument("--rsi-period", type=int, default=14)
    parser.add_argument("--rsi-entry", type=float, default=30.0)
    parser.add_argument("--rsi-exit", type=float, default=55.0)
    parser.add_argument("--lookback", type=int, default=20)

    parser.add_argument(
        "--output-json",
        help="Optional path to write full JSON result.",
    )
    parser.add_argument(
        "--output-trades",
        help="Optional path to write trade log CSV.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Skip human-readable summary and print JSON only.",
    )
    return parser.parse_args()


def normalize_header(name: str) -> str:
    return "".join(ch.lower() for ch in name if ch.isalnum())


def parse_date(raw: str) -> date:
    text = raw.strip()
    if not text:
        raise ValueError("empty date")
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00")).date()
    except ValueError:
        pass
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"unsupported date format: {raw}")


def parse_float(raw: str, field_name: str, line_no: int) -> float:
    text = (raw or "").strip()
    if text == "":
        raise ValueError(f"line {line_no}: missing {field_name}")
    try:
        return float(text.replace(",", ""))
    except ValueError as exc:
        raise ValueError(f"line {line_no}: invalid {field_name} value '{raw}'") from exc


def resolve_columns(fieldnames: Sequence[str]) -> Dict[str, str]:
    normalized = {normalize_header(name): name for name in fieldnames}
    aliases = {
        "date": ("date", "datetime", "timestamp", "time"),
        "open": ("open", "openprice", "o"),
        "high": ("high", "highprice", "h"),
        "low": ("low", "lowprice", "l"),
        "close": ("close", "adjclose", "adjustedclose", "c"),
        "volume": ("volume", "vol", "v"),
    }

    resolved: Dict[str, str] = {}
    for canonical, candidates in aliases.items():
        for candidate in candidates:
            if candidate in normalized:
                resolved[canonical] = normalized[candidate]
                break
    if "date" not in resolved or "close" not in resolved:
        raise ValueError("CSV must include Date and Close columns.")
    return resolved


def load_candles(csv_path: Path) -> List[Candle]:
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    with csv_path.open("r", newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError("CSV is missing headers.")
        columns = resolve_columns(reader.fieldnames)

        deduped: Dict[date, Candle] = {}
        for line_no, row in enumerate(reader, start=2):
            date_value = parse_date(row[columns["date"]])
            close = parse_float(row[columns["close"]], "close", line_no)
            open_value = close
            high = close
            low = close
            volume = 0.0
            if "open" in columns and row.get(columns["open"], "").strip():
                open_value = parse_float(row[columns["open"]], "open", line_no)
            if "high" in columns and row.get(columns["high"], "").strip():
                high = parse_float(row[columns["high"]], "high", line_no)
            if "low" in columns and row.get(columns["low"], "").strip():
                low = parse_float(row[columns["low"]], "low", line_no)
            if "volume" in columns and row.get(columns["volume"], "").strip():
                volume = parse_float(row[columns["volume"]], "volume", line_no)
            deduped[date_value] = Candle(
                date=date_value,
                open_price=open_value,
                high=high,
                low=low,
                close=close,
                volume=volume,
            )

    candles = [deduped[key] for key in sorted(deduped)]
    if len(candles) < 3:
        raise ValueError("Need at least 3 rows of OHLCV data for backtesting.")
    return candles


def rolling_sma(values: Sequence[float], window: int) -> List[Optional[float]]:
    if window <= 0:
        raise ValueError("SMA window must be > 0.")
    result: List[Optional[float]] = [None] * len(values)
    running_sum = 0.0
    for idx, value in enumerate(values):
        running_sum += value
        if idx >= window:
            running_sum -= values[idx - window]
        if idx >= window - 1:
            result[idx] = running_sum / window
    return result


def rolling_rsi(values: Sequence[float], period: int) -> List[Optional[float]]:
    if period <= 0:
        raise ValueError("RSI period must be > 0.")
    result: List[Optional[float]] = [None] * len(values)
    if len(values) <= period:
        return result

    gains: List[float] = []
    losses: List[float] = []
    for idx in range(1, period + 1):
        delta = values[idx] - values[idx - 1]
        gains.append(max(delta, 0.0))
        losses.append(max(-delta, 0.0))

    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period
    result[period] = 100.0 if avg_loss == 0 else 100.0 - (100.0 / (1.0 + (avg_gain / avg_loss)))

    for idx in range(period + 1, len(values)):
        delta = values[idx] - values[idx - 1]
        gain = max(delta, 0.0)
        loss = max(-delta, 0.0)
        avg_gain = ((avg_gain * (period - 1)) + gain) / period
        avg_loss = ((avg_loss * (period - 1)) + loss) / period
        result[idx] = 100.0 if avg_loss == 0 else 100.0 - (100.0 / (1.0 + (avg_gain / avg_loss)))

    return result


def round_or_none(value: Optional[float], digits: int = 4) -> Optional[float]:
    if value is None:
        return None
    return round(value, digits)


def choose_target_position(
    *,
    strategy: str,
    index: int,
    in_position: bool,
    closes: Sequence[float],
    highs: Sequence[float],
    lows: Sequence[float],
    fast_sma: Sequence[Optional[float]],
    slow_sma: Sequence[Optional[float]],
    rsi_values: Sequence[Optional[float]],
    args: argparse.Namespace,
) -> bool:
    if strategy == "sma-crossover":
        fast = fast_sma[index]
        slow = slow_sma[index]
        if fast is None or slow is None:
            return in_position
        return fast > slow

    if strategy == "rsi-reversion":
        rsi_value = rsi_values[index]
        if rsi_value is None:
            return in_position
        if not in_position and rsi_value <= args.rsi_entry:
            return True
        if in_position and rsi_value >= args.rsi_exit:
            return False
        return in_position

    lookback = args.lookback
    if index < lookback:
        return in_position
    highest_recent = max(highs[index - lookback : index])
    lowest_recent = min(lows[index - lookback : index])
    close_value = closes[index]
    if not in_position and close_value > highest_recent:
        return True
    if in_position and close_value < lowest_recent:
        return False
    return in_position


def calc_max_drawdown(equity_values: Sequence[float]) -> float:
    peak = equity_values[0]
    worst = 0.0
    for equity in equity_values:
        if equity > peak:
            peak = equity
        if peak <= 0:
            continue
        drawdown = (equity / peak) - 1.0
        if drawdown < worst:
            worst = drawdown
    return abs(worst)


def calc_sharpe_ratio(daily_returns: Sequence[float], risk_free_rate: float) -> float:
    if len(daily_returns) < 2:
        return 0.0
    volatility = stdev(daily_returns)
    if volatility == 0:
        return 0.0
    excess_daily = mean(daily_returns) - (risk_free_rate / TRADING_DAYS_PER_YEAR)
    return (excess_daily / volatility) * math.sqrt(TRADING_DAYS_PER_YEAR)


def calc_cagr(initial_equity: float, final_equity: float, period_days: int) -> float:
    if period_days <= 0 or initial_equity <= 0 or final_equity <= 0:
        return -1.0
    years = period_days / 365.25
    if years <= 0:
        return -1.0
    return (final_equity / initial_equity) ** (1.0 / years) - 1.0


def write_trades_csv(path: Path, trades: Sequence[Trade]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "entry_date",
                "exit_date",
                "entry_price",
                "exit_price",
                "return_pct",
                "pnl",
                "holding_days",
            ],
        )
        writer.writeheader()
        for trade in trades:
            row = asdict(trade)
            row["entry_price"] = round(trade.entry_price, 6)
            row["exit_price"] = round(trade.exit_price, 6)
            row["return_pct"] = round(trade.return_pct, 4)
            row["pnl"] = round(trade.pnl, 4)
            writer.writerow(row)


def run_backtest(candles: Sequence[Candle], args: argparse.Namespace) -> Tuple[dict, List[Trade]]:
    commission = max(args.commission_bps, 0.0) / 10000.0
    slippage = max(args.slippage_bps, 0.0) / 10000.0
    cash = args.initial_capital
    shares = 0.0
    in_position = False
    entry_date: Optional[date] = None
    entry_price = 0.0
    entry_cost_basis = 0.0
    trades: List[Trade] = []
    days_in_market = 0

    closes = [candle.close for candle in candles]
    highs = [candle.high for candle in candles]
    lows = [candle.low for candle in candles]
    fast_sma = rolling_sma(closes, args.fast_window)
    slow_sma = rolling_sma(closes, args.slow_window)
    rsi_values = rolling_rsi(closes, args.rsi_period)

    equity_curve: List[Tuple[date, float]] = [(candles[0].date, cash)]

    for index in range(len(candles) - 1):
        target_position = choose_target_position(
            strategy=args.strategy,
            index=index,
            in_position=in_position,
            closes=closes,
            highs=highs,
            lows=lows,
            fast_sma=fast_sma,
            slow_sma=slow_sma,
            rsi_values=rsi_values,
            args=args,
        )

        next_candle = candles[index + 1]

        if not in_position and target_position:
            entry_exec = next_candle.open_price * (1.0 + slippage)
            unit_cost = entry_exec * (1.0 + commission)
            if unit_cost > 0:
                shares = cash / unit_cost
                fee = shares * entry_exec * commission
                notional = shares * entry_exec
                entry_cost_basis = notional + fee
                cash -= entry_cost_basis
                cash = max(cash, 0.0)
                in_position = True
                entry_date = next_candle.date
                entry_price = entry_exec

        elif in_position and not target_position:
            exit_exec = next_candle.open_price * (1.0 - slippage)
            gross = shares * exit_exec
            fee = gross * commission
            proceeds = gross - fee
            cash += proceeds
            trade_return = 0.0 if entry_cost_basis <= 0 else (proceeds / entry_cost_basis) - 1.0
            assert entry_date is not None
            trades.append(
                Trade(
                    entry_date=entry_date.isoformat(),
                    exit_date=next_candle.date.isoformat(),
                    entry_price=entry_price,
                    exit_price=exit_exec,
                    return_pct=trade_return * 100.0,
                    pnl=proceeds - entry_cost_basis,
                    holding_days=max((next_candle.date - entry_date).days, 1),
                )
            )
            shares = 0.0
            in_position = False
            entry_date = None
            entry_price = 0.0
            entry_cost_basis = 0.0

        equity = cash + (shares * next_candle.close if in_position else 0.0)
        if in_position:
            days_in_market += 1
        equity_curve.append((next_candle.date, equity))

    if in_position:
        last_candle = candles[-1]
        exit_exec = last_candle.close * (1.0 - slippage)
        gross = shares * exit_exec
        fee = gross * commission
        proceeds = gross - fee
        cash += proceeds
        trade_return = 0.0 if entry_cost_basis <= 0 else (proceeds / entry_cost_basis) - 1.0
        assert entry_date is not None
        trades.append(
            Trade(
                entry_date=entry_date.isoformat(),
                exit_date=last_candle.date.isoformat(),
                entry_price=entry_price,
                exit_price=exit_exec,
                return_pct=trade_return * 100.0,
                pnl=proceeds - entry_cost_basis,
                holding_days=max((last_candle.date - entry_date).days, 1),
            )
        )
        shares = 0.0
        in_position = False
        equity_curve[-1] = (last_candle.date, cash)

    equity_values = [item[1] for item in equity_curve]
    daily_returns = [
        (equity_values[idx] / equity_values[idx - 1]) - 1.0
        for idx in range(1, len(equity_values))
        if equity_values[idx - 1] > 0
    ]

    start_date = equity_curve[0][0]
    end_date = equity_curve[-1][0]
    period_days = max((end_date - start_date).days, 1)
    final_equity = equity_values[-1]
    total_return = (final_equity / args.initial_capital) - 1.0
    cagr = calc_cagr(args.initial_capital, final_equity, period_days)
    max_drawdown = calc_max_drawdown(equity_values)
    sharpe = calc_sharpe_ratio(daily_returns, args.risk_free_rate)
    wins = [trade.return_pct for trade in trades if trade.return_pct > 0]
    losses = [trade.return_pct for trade in trades if trade.return_pct <= 0]
    win_rate = (len(wins) / len(trades)) if trades else 0.0
    gross_win = sum(wins)
    gross_loss = abs(sum(losses))
    profit_factor: Optional[float]
    if gross_loss == 0:
        profit_factor = None
    else:
        profit_factor = gross_win / gross_loss
    expectancy = mean([trade.return_pct for trade in trades]) if trades else 0.0

    result = {
        "strategy": args.strategy,
        "period": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat(),
            "bars": len(candles),
            "days": period_days,
        },
        "metrics": {
            "initial_capital": round(args.initial_capital, 2),
            "final_equity": round(final_equity, 2),
            "net_profit": round(final_equity - args.initial_capital, 2),
            "total_return_pct": round(total_return * 100.0, 4),
            "cagr_pct": round(cagr * 100.0, 4),
            "max_drawdown_pct": round(max_drawdown * 100.0, 4),
            "sharpe_ratio": round(sharpe, 4),
            "exposure_pct": round((days_in_market / max(len(candles) - 1, 1)) * 100.0, 4),
            "trade_count": len(trades),
            "win_rate_pct": round(win_rate * 100.0, 4),
            "avg_trade_return_pct": round(expectancy, 4),
            "avg_win_pct": round(mean(wins), 4) if wins else 0.0,
            "avg_loss_pct": round(mean(losses), 4) if losses else 0.0,
            "profit_factor": round_or_none(profit_factor, 4),
        },
        "config": {
            "commission_bps": args.commission_bps,
            "slippage_bps": args.slippage_bps,
            "risk_free_rate": args.risk_free_rate,
            "fast_window": args.fast_window,
            "slow_window": args.slow_window,
            "rsi_period": args.rsi_period,
            "rsi_entry": args.rsi_entry,
            "rsi_exit": args.rsi_exit,
            "lookback": args.lookback,
        },
        "trades": [asdict(trade) for trade in trades],
    }
    return result, trades


def print_summary(result: dict) -> None:
    metrics = result["metrics"]
    period = result["period"]
    print("Backtest Summary")
    print("================")
    print(f"Strategy: {result['strategy']}")
    print(f"Period:   {period['start']} -> {period['end']} ({period['bars']} bars)")
    print(f"Return:   {metrics['total_return_pct']}%")
    print(f"CAGR:     {metrics['cagr_pct']}%")
    print(f"MDD:      {metrics['max_drawdown_pct']}%")
    print(f"Sharpe:   {metrics['sharpe_ratio']}")
    print(f"Trades:   {metrics['trade_count']}")
    print(f"Win rate: {metrics['win_rate_pct']}%")
    print(f"P/L:      {metrics['net_profit']}")


def validate_args(args: argparse.Namespace) -> None:
    if args.initial_capital <= 0:
        raise ValueError("--initial-capital must be > 0.")
    if args.fast_window <= 0 or args.slow_window <= 0:
        raise ValueError("--fast-window and --slow-window must be > 0.")
    if args.fast_window >= args.slow_window:
        raise ValueError("--fast-window must be smaller than --slow-window.")
    if args.rsi_period <= 0:
        raise ValueError("--rsi-period must be > 0.")
    if not (0 <= args.rsi_entry <= 100 and 0 <= args.rsi_exit <= 100):
        raise ValueError("--rsi-entry and --rsi-exit must be between 0 and 100.")
    if args.rsi_entry >= args.rsi_exit:
        raise ValueError("--rsi-entry must be smaller than --rsi-exit.")
    if args.lookback <= 1:
        raise ValueError("--lookback must be > 1.")
    if args.commission_bps < 0 or args.slippage_bps < 0:
        raise ValueError("--commission-bps and --slippage-bps must be >= 0.")


def main() -> None:
    args = parse_args()
    validate_args(args)

    candles = load_candles(Path(args.csv))
    result, trades = run_backtest(candles, args)

    if args.output_json:
        output_json_path = Path(args.output_json)
        output_json_path.parent.mkdir(parents=True, exist_ok=True)
        output_json_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    if args.output_trades:
        write_trades_csv(Path(args.output_trades), trades)

    if not args.quiet:
        print_summary(result)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
