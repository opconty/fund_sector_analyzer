"""板块分析引擎 - 技术分析+评级"""

from utils.indicators import (
    calculate_sma,
    calculate_rsi,
    calculate_macd,
    calculate_volume_ratio,
    get_trend_status,
    get_rsi_signal,
    get_macd_signal,
)
from config.settings import ANALYSIS_PARAMS, RATING_THRESHOLDS


class SectorAnalyzer:
    """板块分析师"""

    def __init__(self):
        self.params = ANALYSIS_PARAMS
        self.thresholds = RATING_THRESHOLDS

    def analyze(self, sector_data):
        """
        分析单个板块

        Args:
            sector_data: 板块原始数据字典

        Returns:
            分析结果字典
        """
        # 提取基础数据
        name = sector_data.get("f14", "未知板块")
        change_pct = sector_data.get("f3", 0) or 0
        turnover = sector_data.get("f6", 0) or 0
        volume = sector_data.get("f5", 0) or 0

        # 计算/获取技术指标
        rsi = self._calc_rsi_from_data(sector_data)
        trend = self._determine_trend(sector_data)
        volume_ratio = self._calc_volume_ratio(sector_data)

        # 资金流向分析
        net_flow = self._analyze_net_flow(sector_data)

        # 综合评级
        rating = self._calculate_rating(
            change_pct=change_pct,
            rsi=rsi,
            trend=trend,
            volume_ratio=volume_ratio,
            net_flow=net_flow,
        )

        # 生成信号
        signals = self._generate_signals(
            change_pct=change_pct,
            rsi=rsi,
            trend=trend,
            volume_ratio=volume_ratio,
            net_flow=net_flow,
        )

        return {
            "name": name,
            "change_pct": change_pct,
            "turnover": turnover,
            "volume": volume,
            "rsi": rsi,
            "trend": trend,
            "volume_ratio": volume_ratio,
            "net_flow": net_flow,
            "rating": rating["rating"],
            "rating_score": rating["score"],
            "signals": signals,
            "buy_suggestions": rating.get("buy_suggestions", []),
            "sell_suggestions": rating.get("sell_suggestions", []),
        }

    def _generate_signals(self, change_pct, rsi, trend, volume_ratio, net_flow):
        """生成交易信号"""
        signals = []
        
        if trend == "uptrend" and change_pct > 0:
            signals.append("上升通道")
        elif trend == "downtrend" and change_pct < 0:
            signals.append("下降通道")
        
        if rsi > 70:
            signals.append("超买警示")
        elif rsi < 30:
            signals.append("超卖机会")
        
        if volume_ratio > 2:
            signals.append("放量")
        elif volume_ratio < 0.5:
            signals.append("缩量")
        
        if net_flow > 100000:
            signals.append("大幅资金流入")
        elif net_flow < -100000:
            signals.append("大幅资金流出")
        
        return signals

    def analyze_batch(self, sectors):
        """批量分析板块"""
        results = []
        for sector in sectors:
            try:
                result = self.analyze(sector)
                results.append(result)
            except Exception as e:
                print(f"[警告] 分析板块 {sector.get('f14', '未知')} 失败: {e}")
                results.append({
                    "name": sector.get("f14", "未知板块"),
                    "change_pct": 0,
                    "rsi": 50,
                    "trend": "unknown",
                    "rating": "数据不足",
                    "signals": [],
                    "error": str(e),
                })
        return results

    def _calc_rsi_from_data(self, sector_data):
        """从板块数据估算RSI"""
        change_pct = sector_data.get("f3", 0) or 0

        # 简化RSI估算：基于涨跌幅和历史趋势
        if change_pct > 3:
            return 75
        elif change_pct > 2:
            return 68
        elif change_pct > 1:
            return 60
        elif change_pct > 0:
            return 55
        elif change_pct > -1:
            return 45
        elif change_pct > -2:
            return 38
        else:
            return 25

    def _determine_trend(self, sector_data):
        """判断趋势方向"""
        change_pct = sector_data.get("f3", 0) or 0
        change_amt = sector_data.get("f4", 0) or 0

        if change_pct > 1.5:
            return "uptrend"
        elif change_pct < -1.5:
            return "downtrend"
        else:
            return "sideways"

    def _calc_volume_ratio(self, sector_data):
        """计算成交量比率"""
        # 东方财富 f6 是换手率，直接用作参考
        turnover = sector_data.get("f6", 0) or 0
        
        # 根据换手率估算量比
        if turnover > 10:
            return 3.0
        elif turnover > 5:
            return 2.0
        elif turnover > 2:
            return 1.5
        elif turnover > 1:
            return 1.2
        elif turnover > 0.5:
            return 1.0
        else:
            return 0.8

    def _analyze_net_flow(self, sector_data):
        """分析资金流向"""
        # 东方财富数据中资金流向字段
        net_flow = sector_data.get("f62", 0) or sector_data.get("f21", 0) or 0

        # 转换为万元
        if net_flow != 0:
            return round(net_flow / 10000, 2)
        return 0

    def _calculate_rating(self, change_pct, rsi, trend, volume_ratio, net_flow):
        """
        计算综合评级

        Returns:
            {"rating": "评级", "score": 分数, "buy_suggestions": [], "sell_suggestions": []}
        """
        score = 50  # 基准分

        # 涨跌幅评分 (+/- 20)
        if change_pct >= 3:
            score += 20
        elif change_pct >= 1.5:
            score += 15
        elif change_pct >= 0.5:
            score += 10
        elif change_pct >= 0:
            score += 5
        elif change_pct >= -0.5:
            score -= 5
        elif change_pct >= -1.5:
            score -= 10
        else:
            score -= 20

        # RSI评分 (+/- 15)
        if rsi < 30:
            score += 15  # 超卖，可能反弹
        elif rsi < 40:
            score += 10
        elif rsi > 75:
            score -= 15  # 超买，可能回调
        elif rsi > 65:
            score -= 5

        # 趋势评分 (+/- 15)
        if trend == "uptrend":
            score += 15
        elif trend == "sideways":
            score += 5
        else:
            score -= 15

        # 成交量评分 (+/- 10)
        if volume_ratio > 2:
            score += 10
        elif volume_ratio > 1.5:
            score += 5

        # 资金流向评分 (+/- 10)
        if net_flow > 50000:
            score += 10
        elif net_flow > 10000:
            score += 5
        elif net_flow < -50000:
            score -= 10
        elif net_flow < -10000:
            score -= 5

        # 确定评级
        if score >= 75:
            rating = "strong_buy"
        elif score >= 60:
            rating = "buy"
        elif score >= 40:
            rating = "hold"
        elif score >= 25:
            rating = "cautious"
        else:
            rating = "avoid"

        # 生成买卖建议
        buy_suggestions = []
        sell_suggestions = []
        self._generate_suggestions(
            rating, change_pct, rsi, trend, net_flow,
            buy_suggestions, sell_suggestions,
        )

        return {
            "rating": rating,
            "score": score,
            "buy_suggestions": buy_suggestions,
            "sell_suggestions": sell_suggestions,
        }

    def _generate_suggestions(self, rating, change_pct, rsi, trend, net_flow, buy_sugs, sell_sugs):
        """生成具体买卖建议"""
        if rating in ("strong_buy", "buy"):
            if trend == "uptrend":
                buy_sugs.append("趋势向上，可考虑逢低买入")
            if net_flow > 0:
                buy_sugs.append("资金净流入，主力看好")
            if 40 < rsi < 65:
                buy_sugs.append("RSI处于合理区间，买入风险较低")

        if rating in ("cautious", "avoid"):
            if trend == "downtrend":
                sell_sugs.append("趋势向下，建议减仓或回避")
            if net_flow < 0:
                sell_sugs.append("资金净流出，主力撤离")
            if rsi > 65:
                sell_sugs.append("RSI偏高，注意回调风险")
            if change_pct < -2:
                sell_sugs.append("大幅下跌，短期可能继续走弱")

        if rating == "hold":
            buy_sugs.append("观望为主，等待明确方向")
            sell_sugs.append("持仓不动，观察后续走势")

    def get_rating_text(self, rating):
        """获取评级文字"""
        rating_map = {
            "strong_buy": "[强烈推荐]",
            "buy": "[推荐]",
            "hold": "[观望]",
            "cautious": "[谨慎]",
            "avoid": "[回避]",
        }
        return rating_map.get(rating, "⚪ 数据不足")

    def get_rating_emoji(self, rating):
        """获取评级表情"""
        rating_map = {
            "strong_buy": "🟢",
            "buy": "🟡",
            "hold": "⚪",
            "cautious": "🟠",
            "avoid": "🔴",
        }
        return rating_map.get(rating, "⚪")
