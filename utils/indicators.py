"""技术指标计算模块"""

import math


def calculate_sma(data, period):
    """计算简单移动平均线"""
    if len(data) < period:
        return None
    return sum(data[-period:]) / period


def calculate_ema(data, period):
    """计算指数移动平均线"""
    if len(data) < period:
        return None
    multiplier = 2 / (period + 1)
    ema = sum(data[:period]) / period
    for price in data[period:]:
        ema = (price - ema) * multiplier + ema
    return ema


def calculate_rsi(data, period=14):
    """计算RSI相对强弱指标"""
    if len(data) < period + 1:
        return 50.0

    gains = []
    losses = []
    for i in range(1, len(data)):
        change = data[i] - data[i - 1]
        if change > 0:
            gains.append(change)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(abs(change))

    if len(gains) < period:
        return 50.0

    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period

    if avg_loss == 0:
        return 100.0

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return round(rsi, 2)


def calculate_macd(data, fast=12, slow=26, signal=9):
    """计算MACD指标"""
    if len(data) < slow + signal:
        return {"macd": 0, "signal": 0, "histogram": 0}

    ema_fast = calculate_ema(data, fast)
    ema_slow = calculate_ema(data, slow)

    if ema_fast is None or ema_slow is None:
        return {"macd": 0, "signal": 0, "histogram": 0}

    macd_line = ema_fast - ema_slow

    # 简化信号线计算
    macd_values = []
    for i in range(len(data) - slow + 1):
        chunk = data[i:i + slow]
        ef = calculate_ema(chunk[:fast])
        es = calculate_ema(chunk[:slow])
        if ef and es:
            macd_values.append(ef - es)

    if len(macd_values) < signal:
        return {
            "macd": round(macd_line, 3),
            "signal": round(macd_line, 3),
            "histogram": 0,
        }

    signal_line = sum(macd_values[-signal:]) / signal
    histogram = macd_line - signal_line

    return {
        "macd": round(macd_line, 3),
        "signal": round(signal_line, 3),
        "histogram": round(histogram, 3),
    }


def calculate_volume_ratio(current_volume, avg_volume):
    """计算成交量比率"""
    if avg_volume == 0:
        return 0
    return round(current_volume / avg_volume, 2)


def calculate_change_percent(current, previous):
    """计算涨跌幅百分比"""
    if previous == 0:
        return 0
    return round(((current - previous) / previous) * 100, 2)


def get_trend_status(short_ma, medium_ma, long_ma):
    """根据均线判断趋势"""
    if short_ma is None or medium_ma is None or long_ma is None:
        return "unknown"

    if short_ma > medium_ma > long_ma:
        return "uptrend"
    elif short_ma < medium_ma < long_ma:
        return "downtrend"
    else:
        return "sideways"


def get_rsi_signal(rsi, overbought=70, oversold=30):
    """获取RSI信号"""
    if rsi > overbought:
        return "overbought"
    elif rsi < oversold:
        return "oversold"
    else:
        return "neutral"


def get_macd_signal(macd_data):
    """获取MACD信号"""
    if macd_data["histogram"] > 0 and macd_data["macd"] < macd_data["signal"]:
        return "golden_cross"
    elif macd_data["histogram"] < 0 and macd_data["macd"] > macd_data["signal"]:
        return "death_cross"
    elif macd_data["histogram"] > 0:
        return "bullish"
    else:
        return "bearish"
