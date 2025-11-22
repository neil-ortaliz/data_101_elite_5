# Task 7 - Buy/Sell Signal Generation

import pandas as pd
import numpy as np
from typing import Dict, Any


def generate_trading_signal(
    card_id: Any,
    price_history: pd.DataFrame,
    lookback_days: int = 90,
    *,
    date_col: str = "date",
    price_col: str = "price",
    card_id_col: str = "card_id",
    rsi_window: int = 14,
    projection_days: int = 30
) -> Dict[str, Any]:
    """
    Generate a Buy/Sell/Hold trading signal for a card based on technical indicators.

    Returns:
        {
            'signal': 'Strong Buy'|'Buy'|'Hold'|'Sell'|'Strong Sell',
            'confidence': float (0-100),
            'reason': str,
            'target_price': float,
            'indicators': {...},
            'net_score': float
        }
    """

    df = price_history.copy()

    
    # Column Normalization
    
    # Accept flexible column names
    if card_id_col not in df.columns and "id" in df.columns:
        df = df.rename(columns={"id": card_id_col})
    if date_col not in df.columns and "date" in df.columns:
        date_col = "date"
    if price_col not in df.columns:
        for alt in ["market", "avgPrice", "lastPrice", "price_usd"]:
            if alt in df.columns:
                price_col = alt
                break

    if card_id_col not in df.columns or date_col not in df.columns or price_col not in df.columns:
        raise KeyError("price_history must contain card_id, date, and price columns")

   
    # Filter to this card
   
    card_df = df[df[card_id_col] == card_id].copy()
    if card_df.empty:
        return {
            "signal": "Hold",
            "confidence": 0,
            "reason": "No price history available",
            "target_price": None,
            "indicators": {},
            "net_score": 0,
        }

    # Parse dates
    card_df[date_col] = pd.to_datetime(card_df[date_col], errors="coerce")
    card_df = card_df.dropna(subset=[date_col]).sort_values(date_col)

   
    # Build daily price series

    card_df["day"] = card_df[date_col].dt.normalize()
    daily = card_df.groupby("day")[price_col].last().sort_index()

    # Ensure continuous daily index
    end = daily.index.max()
    start = end - pd.Timedelta(days=lookback_days - 1)
    full_idx = pd.date_range(start=start, end=end, freq="D")

    daily = daily.reindex(full_idx).ffill().dropna()

    if len(daily) < 5:
        return {
            "signal": "Hold",
            "confidence": 0,
            "reason": "Insufficient data (need ≥5 days)",
            "target_price": None,
            "indicators": {},
            "net_score": 0,
        }

    prices = daily.values
    days = np.arange(len(prices))

   
    # Indicators
   
    # Moving averages
    ma_5 = float(pd.Series(prices).rolling(5, min_periods=1).mean().iloc[-1])
    ma_15 = float(pd.Series(prices).rolling(15, min_periods=1).mean().iloc[-1])

    # Trend slope using linear regression (numpy.polyfit)
    slope, intercept = np.polyfit(days, prices, 1)
    slope_pct = slope / prices[-1] if prices[-1] != 0 else 0

    # Volatility (std of daily returns)
    returns = pd.Series(prices).pct_change().dropna()
    vol_daily = float(returns.std(ddof=0))
    vol_annual_pct = vol_daily * np.sqrt(252) * 100

    # RSI
    delta = pd.Series(prices).diff()
    gain = delta.where(delta > 0, 0).rolling(rsi_window, min_periods=1).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(rsi_window, min_periods=1).mean()
    rs = gain / loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    current_rsi = float(rsi.iloc[-1])

    current_price = float(prices[-1])

   
    # Decision logic
  
    bullish = 0
    bearish = 0

    # MA crossover
    if ma_5 > ma_15:
        bullish += 2
    else:
        bearish += 2

    # Trend direction
    if slope_pct > 0.001:      # +0.1% per day
        bullish += 2
    elif slope_pct < -0.001:   # -0.1% per day
        bearish += 2

    # RSI
    if current_rsi < 30:
        bullish += 3
    elif current_rsi > 70:
        bearish += 3

    # Price relative to MA15
    if current_price > ma_15:
        bullish += 1
    else:
        bearish += 1

    # Final score
    net = bullish - bearish

    # ---------------------------#
    # SIGNAL MAPPING
    # ---------------------------#
    if net >= 5:
        signal = "Strong Buy"
        reason = "Multiple bullish indicators (MA crossover, trend, RSI)"
    elif net >= 2:
        signal = "Buy"
        reason = "Bullish momentum and positive indicators"
    elif net <= -5:
        signal = "Strong Sell"
        reason = "Multiple bearish indicators (MA crossover, trend, RSI)"
    elif net <= -2:
        signal = "Sell"
        reason = "Bearish momentum and negative indicators"
    else:
        signal = "Hold"
        reason = "Mixed indicators — no clear direction"

   
    # Confidence (0–100)
   
    base_conf = min(100, abs(net) / 6 * 100)
    vol_factor = 1 - min(1, vol_daily * np.sqrt(252))
    confidence = float(max(0, min(100, base_conf * max(0.2, vol_factor))))

 
    # Target Price (projected)
   
    projected = current_price + slope * projection_days
    max_change = 0.5 * current_price
    projected = max(current_price - max_change, min(current_price + max_change, projected))

    return {
        "card_id": card_id,
        "signal": signal,
        "confidence": confidence,
        "reason": reason,
        "target_price": float(projected),
        "net_score": float(net),
        "indicators": {
            "current_price": current_price,
            "ma_5": ma_5,
            "ma_15": ma_15,
            "trend_slope_per_day": float(slope),
            "trend_slope_pct_per_day": float(slope_pct),
            "volatility_daily": vol_daily,
            "volatility_annual_pct": vol_annual_pct,
            "rsi": current_rsi,
            "lookback_days_used": int(len(daily)),
        },
    }

# Task 8 - Backtesting and Validation

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Any, Dict, List


# Simple trading signal (used by backtest)

def generate_trading_signal_simple(
    card_id: Any,
    price_history: pd.DataFrame,
    lookback_days: int = 90,
    date_col: str = "date",
    price_col: str = "price",
    card_id_col: str = "card_id",
    rsi_window: int = 14,
    projection_days: int = 30
) -> Dict[str, Any]:
    """
    Lightweight trading-signal generator using MA crossover, slope, RSI and volatility.
    Returns a dict containing 'signal','confidence','reason','target_price','indicators','net'.
    """
    dff = price_history.copy()

    # Flexible column names
    if card_id_col not in dff.columns and "id" in dff.columns:
        dff = dff.rename(columns={"id": card_id_col})
    if date_col not in dff.columns and "date" in dff.columns:
        date_col = "date"
    if price_col not in dff.columns:
        for alt in ["market", "avgPrice", "lastPrice", "price_usd"]:
            if alt in dff.columns:
                price_col = alt
                break

    if card_id_col not in dff.columns or date_col not in dff.columns or price_col not in dff.columns:
        raise KeyError("price_history must contain card_id, date and price columns")

    card_df = dff[dff[card_id_col] == card_id].copy()
    if card_df.empty:
        return {"signal": "Hold", "confidence": 0.0, "reason": "No data", "target_price": None, "indicators": {}, "net": 0.0}

    card_df[date_col] = pd.to_datetime(card_df[date_col], errors="coerce")
    # remove timezone awareness if present
    try:
        card_df[date_col] = card_df[date_col].dt.tz_localize(None)
    except Exception:
        pass
    card_df = card_df.dropna(subset=[date_col]).sort_values(date_col)

    card_df["day"] = card_df[date_col].dt.normalize()
    daily = card_df.groupby("day")[price_col].last().sort_index()

    if daily.empty:
        return {"signal": "Hold", "confidence": 0.0, "reason": "No daily price series", "target_price": None, "indicators": {}, "net": 0.0}

    # ensure continuous daily index for lookback window
    end = daily.index.max()
    start = end - pd.Timedelta(days=lookback_days - 1)
    full_idx = pd.date_range(start=start, end=end, freq="D")
    daily = daily.reindex(full_idx).ffill().dropna()

    if len(daily) < 5:
        return {"signal": "Hold", "confidence": 0.0, "reason": "Insufficient data (need >=5 days)", "target_price": None, "indicators": {}, "net": 0.0}

    prices = daily.values
    days = np.arange(len(prices))

    # indicators
    ma_5 = float(pd.Series(prices).rolling(5, min_periods=1).mean().iloc[-1])
    ma_15 = float(pd.Series(prices).rolling(15, min_periods=1).mean().iloc[-1])
    slope, intercept = np.polyfit(days, prices, 1)
    slope_pct = slope / prices[-1] if prices[-1] != 0 else 0.0

    returns = pd.Series(prices).pct_change().dropna()
    vol_daily = float(returns.std(ddof=0)) if not returns.empty else 0.0
    vol_annual_pct = vol_daily * np.sqrt(252) * 100.0

    delta = pd.Series(prices).diff()
    gain = delta.where(delta > 0, 0).rolling(rsi_window, min_periods=1).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(rsi_window, min_periods=1).mean()
    rs = gain / loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    current_rsi = float(rsi.iloc[-1]) if not rsi.isna().all() else 50.0

    current_price = float(prices[-1])

    # scoring
    bullish = 0.0
    bearish = 0.0

    if ma_5 > ma_15:
        bullish += 2.0
    else:
        bearish += 2.0

    if slope_pct > 0.001:
        bullish += 2.0
    elif slope_pct < -0.001:
        bearish += 2.0

    if current_rsi < 30:
        bullish += 3.0
    elif current_rsi > 70:
        bearish += 3.0

    if current_price > ma_15:
        bullish += 1.0
    else:
        bearish += 1.0

    net = bullish - bearish

    # signal mapping
    if net >= 5:
        signal = "Strong Buy"
        reason = "Multiple bullish indicators"
    elif net >= 2:
        signal = "Buy"
        reason = "Bullish momentum"
    elif net <= -5:
        signal = "Strong Sell"
        reason = "Multiple bearish indicators"
    elif net <= -2:
        signal = "Sell"
        reason = "Bearish momentum"
    else:
        signal = "Hold"
        reason = "Mixed indicators"

    base_conf = min(100.0, abs(net) / 6.0 * 100.0)
    vol_factor = 1.0 - min(1.0, vol_daily * np.sqrt(252))
    confidence = float(max(0.0, min(100.0, base_conf * max(0.2, vol_factor))))

    projected = current_price + slope * projection_days
    max_change = 0.5 * current_price
    projected = max(current_price - max_change, min(current_price + max_change, projected))

    indicators = {
        "current_price": current_price,
        "ma_5": ma_5,
        "ma_15": ma_15,
        "slope": float(slope),
        "slope_pct": float(slope_pct),
        "vol_daily": vol_daily,
        "vol_annual_pct": vol_annual_pct,
        "rsi": current_rsi,
        "lookback_days_used": int(len(daily))
    }

    return {"signal": signal, "confidence": confidence, "reason": reason, "target_price": float(projected), "indicators": indicators, "net": float(net)}



# Backtester

def backtest_trading_signals(
    card_id: Any,
    price_history: pd.DataFrame,
    start_date: str,
    end_date: str,
    lookback_days: int = 30,
    initial_capital: float = 1000.0,
) -> Dict[str, Any]:
    """
    Backtest the simple trading strategy for one card between start_date and end_date.

    Strategy: at each day (after lookback window) compute the trading signal using historical data
    up to the previous day. If signal is Buy/Strong Buy and we hold no position -> buy (all-in).
    If signal is Sell/Strong Sell and we hold a position -> sell (all-out).
    Records trades, equity curve, win rate, drawdown, final value.

    Returns a dict with summary, trades list and equity curve.
    """
    ph = price_history.copy()
    # normalize columns
    if "card_id" not in ph.columns and "id" in ph.columns:
        ph = ph.rename(columns={"id": "card_id"})
    if "price" not in ph.columns:
        for alt in ["market", "avgPrice", "lastPrice", "price_usd"]:
            if alt in ph.columns:
                ph = ph.rename(columns={alt: "price"})
                break
    if "date" not in ph.columns:
        for alt in ["timestamp", "created_at"]:
            if alt in ph.columns:
                ph = ph.rename(columns={alt: "date"})
                break

    ph["date"] = pd.to_datetime(ph["date"], errors="coerce")
    try:
        ph["date"] = ph["date"].dt.tz_localize(None)
    except Exception:
        pass
    ph = ph.dropna(subset=["date", "price", "card_id"]).sort_values("date")

    dfc = ph[ph["card_id"] == card_id].copy()
    if dfc.empty:
        raise ValueError("No data for given card_id")

    mask = (dfc["date"] >= pd.to_datetime(start_date)) & (dfc["date"] <= pd.to_datetime(end_date))
    test_data = dfc.loc[mask].sort_values("date").reset_index(drop=True)
    if test_data.empty or len(test_data) < lookback_days + 5:
        raise ValueError("Not enough data in the selected period for backtest")

    # daily price series inside backtest window
    test_data["day"] = test_data["date"].dt.normalize()
    daily_all = test_data.groupby("day")["price"].last().sort_index()
    days = list(daily_all.index)

    capital = initial_capital
    position = 0.0
    trades: List[Dict[str, Any]] = []
    equity_curve: List[Dict[str, Any]] = []
    last_buy_price = None
    wins, losses, closed_trades = 0, 0, 0

    # iterate day-by-day starting after lookback_days
    for i in range(lookback_days, len(days)):
        current_day = days[i]
        # historical = all days up to previous day
        historical_days = days[:i]
        historical_series = daily_all.loc[historical_days]
        # build a DataFrame shaped like price_history for the signal function
        hist_df = pd.DataFrame({"date": historical_series.index, "price": historical_series.values})
        hist_df["card_id"] = card_id

        sig = generate_trading_signal_simple(card_id, hist_df, lookback_days=lookback_days)

        current_price = float(daily_all.loc[current_day])

        # Execute signals: buy all or sell all
        if sig["signal"] in ["Strong Buy", "Buy"] and position == 0.0:
            position = capital / current_price
            last_buy_price = current_price
            trades.append({"date": current_day, "action": "BUY", "price": current_price, "quantity": position})
            capital = 0.0
        elif sig["signal"] in ["Strong Sell", "Sell"] and position > 0.0:
            capital = position * current_price
            trades.append({"date": current_day, "action": "SELL", "price": current_price, "quantity": position})
            if last_buy_price is not None:
                pnl = (current_price - last_buy_price) / last_buy_price
                if pnl > 0:
                    wins += 1
                else:
                    losses += 1
                closed_trades += 1
            position = 0.0
            last_buy_price = None

        equity = capital + position * current_price
        equity_curve.append({"date": current_day, "equity": equity})

    # finalize
    final_price = float(daily_all.iloc[-1])
    final_value = capital + position * final_price
    total_return = (final_value - initial_capital) / initial_capital * 100.0
    num_trades = len(trades)
    win_rate = (wins / closed_trades * 100.0) if closed_trades > 0 else None

    eq_df = pd.DataFrame(equity_curve).set_index("date").sort_index()
    running_max = eq_df["equity"].cummax() if not eq_df.empty else pd.Series(dtype=float)
    drawdown = (eq_df["equity"] - running_max) / running_max if not eq_df.empty else pd.Series(dtype=float)
    max_drawdown = float(drawdown.min()) if not drawdown.empty else 0.0

    return {
        "card_id": card_id,
        "start_date": start_date,
        "end_date": end_date,
        "initial_capital": initial_capital,
        "final_value": float(final_value),
        "total_return_pct": float(total_return),
        "num_trades": num_trades,
        "closed_trades": closed_trades,
        "win_rate_pct": float(win_rate) if win_rate is not None else None,
        "max_drawdown_pct": float(max_drawdown * 100.0),
        "trades": trades,
        "equity_curve": eq_df.reset_index().to_dict(orient="records"),
    }