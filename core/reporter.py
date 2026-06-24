"""报告生成模块 - 终端输出+图表导出"""

import os
from datetime import datetime

from tabulate import tabulate
from colorama import init, Fore, Style

from config.settings import OUTPUT_CONFIG
from core.analyzer import SectorAnalyzer

init(autoreset=True)


class ReportGenerator:
    """报告生成器"""

    def __init__(self, analyzer, fund_matcher):
        self.analyzer = analyzer
        self.fund_matcher = fund_matcher
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def print_header(self, title):
        """打印报告标题"""
        width = 60
        print("\n" + "=" * width)
        print(f"  {title}")
        print(f"  生成时间: {self.timestamp}")
        print("=" * width)

    def print_footer(self):
        """打印报告页脚"""
        print("\n" + "-" * 60)
        print("  本报告仅供参考，不构成投资建议")
        print("  数据来源：东方财富 | 更新时间：交易时段实时")
        print("-" * 60)

    def generate_overview(self, sector_analyses):
        """生成概览报告"""
        self.print_header("基金板块分析报告 - 总览")

        # 按评级分组
        ratings = {}
        for a in sector_analyses:
            r = a.get("rating", "unknown")
            if r not in ratings:
                ratings[r] = []
            ratings[r].append(a)

        # 打印各评级板块
        rating_order = ["strong_buy", "buy", "hold", "cautious", "avoid"]
        rating_labels = {
            "strong_buy": "[强烈推荐]",
            "buy": "[推荐关注]",
            "hold": "[观望]",
            "cautious": "[谨慎对待]",
            "avoid": "[回避]",
        }

        for rating in rating_order:
            items = ratings.get(rating, [])
            if not items:
                continue

            print(f"\n[强烈推荐] ({len(items)}个板块)")
            print("-" * 50)

            for item in items[:10]:  # 每个评级最多显示10个
                name = item.get("name", "未知")
                change = item.get("change_pct", 0)
                rsi = item.get("rsi", 0)
                trend = item.get("trend", "unknown")
                net_flow = item.get("net_flow", 0)

                change_str = f"+{change}%" if change >= 0 else f"{change}%"
                flow_str = f"+{net_flow:.0f}万" if net_flow >= 0 else f"{net_flow:.0f}万"

                trend_icon = {"uptrend": "[上升]", "downtrend": "[下降]", "sideways": "[震荡]"}.get(trend, "[未知]")

                print(
                    f"  {trend_icon} {name:<12} "
                    f"涨跌: {change_str:>7} | "
                    f"RSI: {rsi:>4} | "
                    f"资金: {flow_str:>8}"
                )

        self.print_footer()

    def generate_detailed_report(self, sector_analyses, top_n=5):
        """生成详细分析报告"""
        self.print_header("基金板块详细分析报告")

        # 排序
        sorted_analyses = sorted(
            sector_analyses,
            key=lambda x: x.get("rating_score", 0),
            reverse=True,
        )

        # 推荐板块
        print(f"\n[推荐板块 Top {top_n}]")
        print("=" * 60)

        for i, analysis in enumerate(sorted_analyses[:top_n], 1):
            self._print_sector_detail(analysis, is_top=True)

        # 回避板块
        print(f"\n[建议回避板块 Top {top_n}]")
        print("=" * 60)

        avoid_analyses = sorted(
            [a for a in sorted_analyses if a.get("rating") in ("cautious", "avoid")],
            key=lambda x: x.get("rating_score", 0),
        )
        for i, analysis in enumerate(avoid_analyses[:top_n], 1):
            self._print_sector_detail(analysis, is_top=False)

        self.print_footer()

    def _print_sector_detail(self, analysis, is_top=True):
        """打印单个板块详情"""
        name = analysis.get("name", "未知")
        rating = analysis.get("rating", "unknown")
        score = analysis.get("rating_score", 0)
        change = analysis.get("change_pct", 0)
        rsi = analysis.get("rsi", 0)
        trend = analysis.get("trend", "unknown")
        volume_ratio = analysis.get("volume_ratio", 0)
        net_flow = analysis.get("net_flow", 0)
        signals = analysis.get("signals", [])
        buy_sugs = analysis.get("buy_suggestions", [])
        sell_sugs = analysis.get("sell_suggestions", [])

        rating_text = self.analyzer.get_rating_text(rating)

        print(f"\n  #{'1' if is_top else 'X'} {name}")
        print(f"  评级: {rating_text} (得分: {score})")
        print(f"  涨跌: {'+' if change >= 0 else ''}{change}%  "
              f"RSI: {rsi}  "
               f"趋势: {'[上升]' if trend == 'uptrend' else '[下降]' if trend == 'downtrend' else '[震荡]'}")
        print(f"  量比: {volume_ratio}  "
              f"资金: {'+' if net_flow >= 0 else ''}{net_flow:.0f}万")

        if buy_sugs:
            print(f"  买入建议:")
            for s in buy_sugs:
                print(f"    • {s}")

        if sell_sugs:
            print(f"  卖出建议:")
            for s in sell_sugs:
                print(f"    • {s}")

        # 匹配基金
        funds = self.fund_matcher.find_funds_by_sector(name)
        if funds:
            print(f"  相关基金:")
            for fund in funds[:3]:
                print(f"    {self.fund_matcher.format_fund_info(fund)}")

    def generate_suggestions_report(self, matched_data):
        """生成操作建议报告"""
        self.print_header("基金买卖操作建议")

        # 买入推荐
        buy_items = [
            m for m in matched_data
            if m["analysis"].get("rating") in ("strong_buy", "buy")
        ]

        if buy_items:
            print(f"\n[推荐买入]")
            print("-" * 60)
            for item in buy_items:
                analysis = item["analysis"]
                funds = item["funds"]
                print(f"\n  板块: {analysis['name']}")
                print(f"  评级: {self.analyzer.get_rating_text(analysis['rating'])}")
                print(f"  涨跌: {'+' if analysis['change_pct'] >= 0 else ''}{analysis['change_pct']}%")

                if funds:
                    print(f"  推荐基金:")
                    for fund in funds[:2]:
                        print(f"    {self.fund_matcher.format_fund_info(fund)}")

        # 卖出/回避
        sell_items = [
            m for m in matched_data
            if m["analysis"].get("rating") in ("cautious", "avoid")
        ]

        if sell_items:
            print(f"\n[建议减仓/回避]")
            print("-" * 60)
            for item in sell_items:
                analysis = item["analysis"]
                funds = item["funds"]
                print(f"\n  板块: {analysis['name']}")
                print(f"  评级: {self.analyzer.get_rating_text(analysis['rating'])}")
                print(f"  涨跌: {'+' if analysis['change_pct'] >= 0 else ''}{analysis['change_pct']}%")

                if funds:
                    print(f"  相关基金:")
                    for fund in funds[:2]:
                        print(f"    {self.fund_matcher.format_fund_info(fund)}")

        # 观望
        hold_items = [
            m for m in matched_data
            if m["analysis"].get("rating") == "hold"
        ]

        if hold_items:
            print(f"\n[建议观望]")
            print("-" * 60)
            for item in hold_items[:5]:
                analysis = item["analysis"]
                print(f"  {analysis['name']} - {self.analyzer.get_rating_text(analysis['rating'])} "
                      f"({'+' if analysis['change_pct'] >= 0 else ''}{analysis['change_pct']}%)")

        self.print_footer()

    def generate_text_report(self, sector_analyses, matched_data, filepath):
        """
        生成纯文本报告并保存到文件

        Args:
            sector_analyses: 板块分析结果
            matched_data: 匹配的板块-基金数据
            filepath: 保存路径
        """
        lines = []

        lines.append("=" * 70)
        lines.append("           基金板块分析报告")
        lines.append(f"           生成时间: {self.timestamp}")
        lines.append("=" * 70)

        # 排序
        sorted_analyses = sorted(
            sector_analyses,
            key=lambda x: x.get("rating_score", 0),
            reverse=True,
        )

        lines.append("\n【推荐板块 TOP 10】")
        lines.append("-" * 70)
        for i, a in enumerate(sorted_analyses[:10], 1):
            name = a.get("name", "未知")
            rating = self.analyzer.get_rating_text(a.get("rating", "unknown"))
            change = f"+{a['change_pct']}%" if a["change_pct"] >= 0 else f"{a['change_pct']}%"
            lines.append(f"  {i:2d}. {name:<15} {rating:<12} 涨跌: {change}")

        lines.append("\n【回避板块 TOP 5】")
        lines.append("-" * 70)
        for i, a in enumerate(
            sorted([x for x in sorted_analyses if x.get("rating") in ("cautious", "avoid")],
                   key=lambda x: x.get("rating_score", 0))[:5], 1
        ):
            name = a.get("name", "未知")
            rating = self.analyzer.get_rating_text(a.get("rating", "unknown"))
            change = f"+{a['change_pct']}%" if a["change_pct"] >= 0 else f"{a['change_pct']}%"
            lines.append(f"  {i:2d}. {name:<15} {rating:<12} 涨跌: {change}")

        lines.append("\n【操作建议】")
        lines.append("-" * 70)
        for item in matched_data:
            a = item["analysis"]
            if a.get("rating") in ("strong_buy", "buy"):
                funds = item["funds"]
                fund_names = ", ".join([f.get("name", "") for f in funds[:2]])
                lines.append(f"  ✅ 买入: {a['name']} -> {fund_names}")
            elif a.get("rating") in ("cautious", "avoid"):
                funds = item["funds"]
                fund_names = ", ".join([f.get("name", "") for f in funds[:2]])
                lines.append(f"  ❌ 回避: {a['name']} -> {fund_names}")

        lines.append("\n" + "=" * 70)
        lines.append("⚠️ 本报告仅供参考，不构成投资建议")

        # 写入文件
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
            return filepath
        except Exception as e:
            print(f"[错误] 保存报告失败: {e}")
            return None

    def generate_csv_report(self, sector_analyses, filepath):
        """生成CSV格式报告"""
        try:
            import csv

            rows = []
            for a in sector_analyses:
                rows.append({
                    "板块名称": a.get("name", ""),
                    "涨跌幅(%)": a.get("change_pct", 0),
                    "RSI": a.get("rsi", 0),
                    "趋势": a.get("trend", ""),
                    "量比": a.get("volume_ratio", 0),
                    "资金流向(万)": a.get("net_flow", 0),
                    "评级": self.analyzer.get_rating_text(a.get("rating", "unknown")),
                    "评分": a.get("rating_score", 0),
                })

            with open(filepath, "w", encoding="utf-8-sig", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=rows[0].keys() if rows else [])
                writer.writeheader()
                writer.writerows(rows)

            return filepath
        except Exception as e:
            print(f"[错误] 生成CSV报告失败: {e}")
            return None
