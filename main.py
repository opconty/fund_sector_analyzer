"""基金板块分析助手 - 主程序入口"""

import argparse
import sys
import os
import io

# 设置控制台编码为 UTF-8
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from datetime import datetime

from core.data_fetcher import DataFetcher
from core.analyzer import SectorAnalyzer
from core.fund_matcher import FundMatcher
from core.reporter import ReportGenerator
from core.chart_generator import ChartGenerator


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="基金板块分析助手 - 辅助基金买卖决策",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python main.py                          # 快速概览
  python main.py --full-report            # 详细分析报告
  python main.py --suggestions            # 买卖建议
  python main.py --sector 半导体          # 查看指定板块
  python main.py --watch --interval 60    # 实时监控(60秒刷新)
  python main.py --output report.txt      # 导出文本报告
  python main.py --csv output.csv         # 导出CSV报告
  python main.py --charts ./charts        # 生成图表
  python main.py --full-report --charts ./charts --output report.txt  # 完整模式
        """,
    )

    parser.add_argument(
        "--full-report",
        action="store_true",
        help="生成详细分析报告",
    )
    parser.add_argument(
        "--suggestions",
        action="store_true",
        help="生成买卖操作建议",
    )
    parser.add_argument(
        "--sector",
        type=str,
        help="查看指定板块详情",
    )
    parser.add_argument(
        "--watch",
        action="store_true",
        help="实时监控模式",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=60,
        help="监控刷新间隔(秒)，默认60秒",
    )
    parser.add_argument(
        "--output",
        type=str,
        help="导出文本报告文件路径",
    )
    parser.add_argument(
        "--csv",
        type=str,
        help="导出CSV报告文件路径",
    )
    parser.add_argument(
        "--charts",
        type=str,
        help="导出图表目录路径",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=20,
        help="显示板块数量，默认20个",
    )

    return parser.parse_args()


def run_once(fetcher, analyzer, fund_matcher, reporter, chart_gen, args):
    """执行一次完整分析"""
    print("\n[1/4] 正在获取板块数据...")

    # 获取板块数据
    if args.sector:
        # 查找指定板块
        all_sectors = fetcher.get_all_sectors()
        target = None
        for s in all_sectors:
            if args.sector in s.get("f14", ""):
                target = s
                break

        if target:
            analyses = [analyzer.analyze(target)]
        else:
            print(f"[错误] 未找到板块: {args.sector}")
            print("[提示] 使用模拟行业板块数据")
            analyses = [analyzer.analyze({
                "f14": args.sector, "f3": 0, "f4": 0, "f5": 0, "f6": 1, "f62": 0
            })]
    else:
        # 获取行业板块涨跌排名
        print("[1/4] 正在通过 AKShare 获取行业板块数据...")
        gainers = fetcher.fetch_top_gainers(limit=args.top // 2)
        losers = fetcher.fetch_top_losers(limit=args.top // 2)
        all_sectors = gainers + losers
        
        if not all_sectors:
            print("[警告] AKShare 获取失败，使用模拟数据")
            all_sectors = [
                {"f14": "半导体", "f3": 3.25, "f4": 2.15},
                {"f14": "创新药", "f3": 2.80, "f4": 1.95},
                {"f14": "券商", "f3": 2.15, "f4": 1.45},
                {"f14": "新能源", "f3": 1.85, "f4": 1.20},
                {"f14": "人工智能", "f3": 1.50, "f4": 0.98},
                {"f14": "银行", "f3": 0.50, "f4": 0.32},
                {"f14": "白酒", "f3": 0.25, "f4": 0.18},
                {"f14": "煤炭", "f3": -1.20, "f4": -0.85},
                {"f14": "房地产", "f3": -2.15, "f4": -1.50},
                {"f14": "有色金属", "f3": -2.80, "f4": -1.95},
                {"f14": "军工", "f3": -3.50, "f4": -2.45},
            ]
        
        analyses = analyzer.analyze_batch(all_sectors)

    if not analyses:
        print("\n[提示] 无法获取数据，使用模拟行业板块数据")
        analyses = [
            {"name": "半导体", "change_pct": 3.25, "rsi": 68, "trend": "uptrend", 
             "volume_ratio": 2.1, "net_flow": 120000, "rating": "strong_buy", "rating_score": 85,
             "signals": [], "buy_suggestions": ["趋势向上，可考虑逢低买入", "资金净流入，主力看好"], "sell_suggestions": []},
            {"name": "创新药", "change_pct": 2.80, "rsi": 62, "trend": "uptrend",
             "volume_ratio": 1.8, "net_flow": 85000, "rating": "strong_buy", "rating_score": 82,
             "signals": [], "buy_suggestions": ["底部特征明显，资金持续流入"], "sell_suggestions": []},
            {"name": "券商", "change_pct": 2.15, "rsi": 58, "trend": "uptrend",
             "volume_ratio": 2.5, "net_flow": 65000, "rating": "buy", "rating_score": 78,
             "signals": [], "buy_suggestions": ["估值偏低，有修复空间"], "sell_suggestions": []},
            {"name": "新能源", "change_pct": 1.85, "rsi": 55, "trend": "uptrend",
             "volume_ratio": 1.5, "net_flow": 42000, "rating": "buy", "rating_score": 72,
             "signals": [], "buy_suggestions": ["行业利好不断"], "sell_suggestions": []},
            {"name": "人工智能", "change_pct": 1.50, "rsi": 65, "trend": "uptrend",
             "volume_ratio": 1.9, "net_flow": 38000, "rating": "buy", "rating_score": 70,
             "signals": [], "buy_suggestions": ["中长期看好"], "sell_suggestions": []},
            {"name": "消费电子", "change_pct": 0.85, "rsi": 52, "trend": "sideways",
             "volume_ratio": 1.2, "net_flow": 15000, "rating": "hold", "rating_score": 55,
             "signals": [], "buy_suggestions": ["观望为主"], "sell_suggestions": ["等待明确方向"]},
            {"name": "银行", "change_pct": 0.50, "rsi": 48, "trend": "sideways",
             "volume_ratio": 0.8, "net_flow": 9500, "rating": "hold", "rating_score": 52,
             "signals": [], "buy_suggestions": ["防御性配置"], "sell_suggestions": []},
            {"name": "白酒", "change_pct": 0.25, "rsi": 45, "trend": "sideways",
             "volume_ratio": 1.1, "net_flow": 12000, "rating": "hold", "rating_score": 50,
             "signals": [], "buy_suggestions": [], "sell_suggestions": []},
            {"name": "煤炭", "change_pct": -1.20, "rsi": 38, "trend": "downtrend",
             "volume_ratio": 1.5, "net_flow": -28000, "rating": "cautious", "rating_score": 35,
             "signals": [], "buy_suggestions": [], "sell_suggestions": ["趋势向下，建议减仓"]},
            {"name": "房地产", "change_pct": -2.15, "rsi": 32, "trend": "downtrend",
             "volume_ratio": 1.8, "net_flow": -45000, "rating": "cautious", "rating_score": 28,
             "signals": [], "buy_suggestions": [], "sell_suggestions": ["政策尚未明朗，谨慎参与"]},
            {"name": "有色金属", "change_pct": -2.80, "rsi": 28, "trend": "downtrend",
             "volume_ratio": 2.2, "net_flow": -52000, "rating": "avoid", "rating_score": 22,
             "signals": [], "buy_suggestions": [], "sell_suggestions": ["空头排列，回避"]},
            {"name": "军工", "change_pct": -3.50, "rsi": 25, "trend": "downtrend",
             "volume_ratio": 2.5, "net_flow": -68000, "rating": "avoid", "rating_score": 18,
             "signals": [], "buy_suggestions": [], "sell_suggestions": ["资金持续流出，建议回避"]},
        ]
    else:
        print(f"[2/4] 分析完成，共分析 {len(analyses)} 个板块")

    # 匹配基金
    print("[3/4] 匹配相关基金...")
    matched = fund_matcher.match_and_rank(analyses)

    # 生成报告
    print("[4/4] 生成报告...")

    # 终端输出
    if args.sector and analyses:
        reporter.print_header(f"板块详情: {analyses[0].get('name', '')}")
        reporter._print_sector_detail(analyses[0], is_top=True)
        reporter.print_footer()
    elif args.full_report:
        reporter.generate_detailed_report(analyses, top_n=5)
    elif args.suggestions:
        reporter.generate_suggestions_report(matched)
    else:
        reporter.generate_overview(analyses)

    # 导出文本报告
    if args.output:
        print(f"\n[导出] 文本报告: {args.output}")
        path = reporter.generate_text_report(analyses, matched, args.output)
        if path:
            print(f"      保存成功: {path}")

    # 导出CSV
    if args.csv:
        print(f"\n[导出] CSV报告: {args.csv}")
        path = reporter.generate_csv_report(analyses, args.csv)
        if path:
            print(f"      保存成功: {path}")

    # 生成图表
    if args.charts:
        print(f"\n[导出] 图表目录: {args.charts}")
        charts = chart_gen.generate_all_charts(analyses, args.charts)
        if charts:
            for c in charts:
                print(f"      已生成: {os.path.basename(c)}")

    return analyses


def main():
    """主函数"""
    args = parse_args()

    # 初始化模块
    fetcher = DataFetcher()
    analyzer = SectorAnalyzer()
    fund_matcher = FundMatcher()
    reporter = ReportGenerator(analyzer, fund_matcher)
    chart_gen = ChartGenerator()

    # 显示启动信息
    print("\n" + "=" * 60)
    print("       基金板块分析助手")
    print("       数据来源: 东方财富API")
    print("=" * 60)

    # 显示基金库覆盖情况
    sector_count = fund_matcher.get_sector_fund_count()
    print(f"       基金库覆盖: {sector_count} 个板块")

    if args.watch:
        # 监控模式
        print(f"\n[监控模式] 每 {args.interval} 秒刷新一次")
        print("[按 Ctrl+C 退出]\n")

        try:
            while True:
                run_once(fetcher, analyzer, fund_matcher, reporter, chart_gen, args)
                print(f"\n[下次刷新: {args.interval}秒后...]")
                try:
                    import time
                    time.sleep(args.interval)
                except KeyboardInterrupt:
                    print("\n[退出监控模式]")
                    break
        except KeyboardInterrupt:
            print("\n[退出监控模式]")
    else:
        # 单次运行
        run_once(fetcher, analyzer, fund_matcher, reporter, chart_gen, args)


if __name__ == "__main__":
    main()
