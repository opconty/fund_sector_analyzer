"""报告生成模块 - 终端输出 + 图表导出"""

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

        ratings = {}
        for a in sector_analyses:
            r = a.get("rating", "unknown")
            if r not in ratings:
                ratings[r] = []
            ratings[r].append(a)

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

            print(f"\n{rating_labels[rating]} ({len(items)}个板块)")
            print("-" * 50)

            for item in items[:10]:
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

        sorted_analyses = sorted(
            sector_analyses,
            key=lambda x: x.get("rating_score", 0),
            reverse=True,
        )

        print(f"\n[推荐板块 Top {top_n}]")
        print("=" * 60)

        for i, analysis in enumerate(sorted_analyses[:top_n], 1):
            self._print_sector_detail(analysis, is_top=True)

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

        funds = self.fund_matcher.find_funds_by_sector(name)
        if funds:
            print(f"  相关基金:")
            for fund in funds[:3]:
                print(f"    {self.fund_matcher.format_fund_info(fund)}")

    def generate_suggestions_report(self, matched_data):
        """生成操作建议报告"""
        self.print_header("基金买卖操作建议")

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
        """生成纯文本报告并保存到文件"""
        lines = []

        lines.append("=" * 70)
        lines.append("           基金板块分析报告")
        lines.append(f"           生成时间: {self.timestamp}")
        lines.append("=" * 70)

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

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
            return filepath
        except Exception as e:
            print(f"[错误] 保存报告失败: {e}")
            return None

    def generate_csv_report(self, sector_analyses, filepath):
        """生成 CSV 格式报告"""
        try:
            import csv

            rows = []
            for a in sector_analyses:
                rows.append({
                    "板块名称": a.get("name", ""),
                    "涨跌幅 (%)": a.get("change_pct", 0),
                    "RSI": a.get("rsi", 0),
                    "趋势": a.get("trend", ""),
                    "量比": a.get("volume_ratio", 0),
                    "资金流向 (万)": a.get("net_flow", 0),
                    "评级": self.analyzer.get_rating_text(a.get("rating", "unknown")),
                    "评分": a.get("rating_score", 0),
                })

            with open(filepath, "w", encoding="utf-8-sig", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=rows[0].keys() if rows else [])
                writer.writeheader()
                writer.writerows(rows)

            return filepath
        except Exception as e:
            print(f"[错误] 生成 CSV 报告失败: {e}")
            return None


def show_indices_report(index_fetcher, fund_matcher):
    """显示指数行情报告"""
    print("\n[1/2] 正在获取指数数据...")

    a_indices = index_fetcher.fetch_a_stock_indices()
    global_indices = index_fetcher.fetch_global_indices()

    print("[2/2] 生成指数行情报告...")

    print("\n" + "=" * 70)
    print("       全球主要指数行情")
    print("       生成时间:" + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 70)

    print("\n【A 股主要指数】")
    print("-" * 70)
    print(f"  {'指数名称':<10} {'最新价':>12} {'涨跌幅':>10} {'成交额 (亿)':>12}")
    print("-" * 70)

    for idx in a_indices:
        name = idx['name']
        price = idx['price']
        change = idx['change_pct']
        volume = idx['volume'] / 100000000 if idx['volume'] > 0 else 0

        change_str = f"+{change:.2f}%" if change >= 0 else f"{change:.2f}%"
        vol_str = f"{volume:,.2f}"

        print(f"  {name:<10} {price:>12,.2f} {change_str:>10} {vol_str:>12}")

    print("\n【全球主要指数】")
    print("-" * 70)
    print(f"  {'指数名称':<10} {'最新价':>12} {'涨跌幅':>10}")
    print("-" * 70)

    for idx in global_indices:
        name = idx['name']
        price = idx['price']
        change = idx['change_pct']

        change_str = f"+{change:.2f}%" if change >= 0 else f"{change:.2f}%"
        print(f"  {name:<10} {price:>12,.2f} {change_str:>10}")

    print("\n" + "-" * 70)
    print("  数据来源：新浪财经 | 更新时间：交易时段实时")
    print("  全球指数数据为模拟值，仅供参考")
    print("-" * 70)


def show_flows_report(source_manager, fund_matcher):
    """显示资金流向报告"""
    print("\n[1/3] 正在获取资金流向数据...")

    industry_df = source_manager.fetch_fund_flow('industry')
    concept_df = source_manager.fetch_fund_flow('concept')

    print("[2/3] 处理资金流向数据...")
    print("[3/3] 生成资金流向报告...")

    print("\n" + "=" * 80)
    print("       今日板块资金流向")
    print("       生成时间:" + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 80)

    if industry_df is not None and len(industry_df) > 0:
        print("\n【行业板块资金流向 TOP 15（主力净流入）】")
        print("-" * 80)
        print(f"  {'排名':<6}{'板块名称':<12}{'涨跌幅':>10}{'主力净流入 (亿)':>14}")
        print("-" * 80)

        top_n = min(15, len(industry_df))
        for i in range(top_n):
            try:
                row = industry_df.iloc[i]
                rank = int(row.iloc[0])
                name = str(row.iloc[1])
                change_pct = float(row.iloc[3])
                main_net = float(row.iloc[6])

                change_str = f"+{change_pct:.2f}%" if change_pct >= 0 else f"{change_pct:.2f}%"
                net_str = f"{main_net:.2f}"

                print(f"  #{rank:<4} {name:<12} {change_str:>10} {net_str:>14}")
            except Exception as e:
                print(f"    错误: {e}")
                import traceback
                traceback.print_exc()
                continue

    if concept_df is not None and len(concept_df) > 0:
        print("\n【概念板块资金流向 TOP 10（主力净流入）】")
        print("-" * 80)
        print(f"  {'排名':<6}{'板块名称':<12}{'涨跌幅':>10}{'主力净流入 (亿)':>14}")
        print("-" * 80)

        top_n = min(10, len(concept_df))
        for i in range(top_n):
            try:
                row = concept_df.iloc[i]
                rank = int(row.iloc[0])
                name = str(row.iloc[1])
                change_pct = float(row.iloc[3])
                main_net = float(row.iloc[6])

                change_str = f"+{change_pct:.2f}%" if change_pct >= 0 else f"{change_pct:.2f}%"
                net_str = f"{main_net:.2f}"

                print(f"  #{rank:<4} {name:<12} {change_str:>10} {net_str:>14}")
            except Exception as e:
                print(f"    错误: {e}")
                continue

    print("\n" + "-" * 80)
    print("  数据来源：新浪财经 | 更新时间：交易时段实时")
    print("  单位：亿元")
    print("-" * 80)
