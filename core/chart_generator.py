"""图表生成模块 - 生成各类分析图表"""

import os
from datetime import datetime

from config.settings import OUTPUT_CONFIG


class ChartGenerator:
    """图表生成器"""

    def __init__(self):
        import matplotlib
        matplotlib.use("Agg")  # 非交互式后端
        import matplotlib.pyplot as plt
        import matplotlib

        self.plt = plt
        self.matplotlib = matplotlib

        # 设置中文字体
        self._setup_font()

    def _setup_font(self):
        """设置中文字体"""
        try:
            # Windows系统字体路径
            font_paths = [
                "C:/Windows/Fonts/msyh.ttc",   # 微软雅黑
                "C:/Windows/Fonts/simhei.ttf",  # 黑体
                "C:/Windows/Fonts/simfang.ttf", # 仿宋
            ]

            for fp in font_paths:
                if os.path.exists(fp):
                    self.matplotlib.rcParams["font.sans-serif"] = ["Microsoft YaHei"]
                    break
        except Exception:
            self.matplotlib.rcParams["font.sans-serif"] = ["Microsoft YaHei"]

        self.matplotlib.rcParams["axes.unicode_minus"] = False

    def generate_sector_comparison(self, sector_analyses, output_path):
        """
        生成板块涨跌对比图

        Args:
            sector_analyses: 板块分析结果列表
            output_path: 输出路径

        Returns:
            输出文件路径
        """
        try:
            import matplotlib.pyplot as plt

            # 取前15个板块
            top_sectors = sorted(
                sector_analyses,
                key=lambda x: x.get("change_pct", 0),
                reverse=True,
            )[:15]

            names = [s.get("name", "")[-6:] for s in top_sectors]  # 截取后6个字符
            changes = [s.get("change_pct", 0) for s in top_sectors]

            # 颜色：涨红跌绿（A股习惯）
            colors = ["#ef4444" if c >= 0 else "#22c55e" for c in changes]

            fig, ax = plt.subplots(
                figsize=(OUTPUT_CONFIG["chart_width"], OUTPUT_CONFIG["chart_height"]),
                dpi=OUTPUT_CONFIG["chart_dpi"],
            )

            bars = ax.barh(names, changes, color=colors, edgecolor="white", height=0.6)

            # 添加数值标签
            for bar, change in zip(bars, changes):
                ax.text(
                    bar.get_width() + (0.05 if change >= 0 else -0.05),
                    bar.get_y() + bar.get_height() / 2,
                    f"{change:+.2f}%",
                    va="center",
                    fontsize=9,
                )

            ax.set_xlabel("涨跌幅 (%)", fontsize=12)
            ax.set_title("板块涨跌幅排名 TOP 15", fontsize=14, fontweight="bold")
            ax.axvline(x=0, color="gray", linewidth=0.8)

            # 添加图例
            ax.legend(
                ["上涨", "下跌"],
                loc="lower right",
                facecolor="white",
                edgecolor="gray",
            )

            plt.tight_layout()
            plt.savefig(output_path, bbox_inches="tight")
            plt.close()

            return output_path

        except Exception as e:
            print(f"[错误] 生成板块对比图失败: {e}")
            return None

    def generate_rating_distribution(self, sector_analyses, output_path):
        """
        生成评级分布饼图

        Args:
            sector_analyses: 板块分析结果列表
            output_path: 输出路径

        Returns:
            输出文件路径
        """
        try:
            import matplotlib.pyplot as plt

            ratings = {}
            for a in sector_analyses:
                r = a.get("rating", "unknown")
                ratings[r] = ratings.get(r, 0) + 1

            if not ratings:
                return None

            labels = ["强烈推荐", "推荐", "观望", "谨慎", "回避"]
            rating_keys = ["strong_buy", "buy", "hold", "cautious", "avoid"]
            sizes = [ratings.get(k, 0) for k in rating_keys]
            colors = ["#22c55e", "#eab308", "#94a3b8", "#f97316", "#ef4444"]

            # 过滤掉0大小的
            filtered_labels = []
            filtered_sizes = []
            filtered_colors = []
            for l, s, c in zip(labels, sizes, colors):
                if s > 0:
                    filtered_labels.append(l)
                    filtered_sizes.append(s)
                    filtered_colors.append(c)

            fig, ax = plt.subplots(
                figsize=(OUTPUT_CONFIG["chart_width"], OUTPUT_CONFIG["chart_height"]),
                dpi=OUTPUT_CONFIG["chart_dpi"],
            )

            wedges, texts, autotexts = ax.pie(
                filtered_sizes,
                labels=filtered_labels,
                colors=filtered_colors,
                autopct="%1.1f%%",
                startangle=90,
                textprops={"fontsize": 11},
            )

            ax.set_title("板块评级分布", fontsize=14, fontweight="bold")

            plt.tight_layout()
            plt.savefig(output_path, bbox_inches="tight")
            plt.close()

            return output_path

        except Exception as e:
            print(f"[错误] 生成评级分布图失败: {e}")
            return None

    def generate_rsi_distribution(self, sector_analyses, output_path):
        """
        生成RSI分布图

        Args:
            sector_analyses: 板块分析结果列表
            output_path: 输出路径

        Returns:
            输出文件路径
        """
        try:
            import matplotlib.pyplot as plt

            rsis = [a.get("rsi", 50) for a in sector_analyses if a.get("rsi")]

            if not rsis:
                return None

            fig, ax = plt.subplots(
                figsize=(OUTPUT_CONFIG["chart_width"], OUTPUT_CONFIG["chart_height"]),
                dpi=OUTPUT_CONFIG["chart_dpi"],
            )

            ax.hist(rsis, bins=20, color="#3b82f6", edgecolor="white", alpha=0.8)

            # 标注超买超卖区域
            ax.axvline(x=70, color="#ef4444", linestyle="--", label="超买线(70)")
            ax.axvline(x=30, color="#22c55e", linestyle="--", label="超卖线(30)")

            ax.set_xlabel("RSI值", fontsize=12)
            ax.set_ylabel("板块数量", fontsize=12)
            ax.set_title("板块RSI分布图", fontsize=14, fontweight="bold")
            ax.legend()

            plt.tight_layout()
            plt.savefig(output_path, bbox_inches="tight")
            plt.close()

            return output_path

        except Exception as e:
            print(f"[错误] 生成RSI分布图失败: {e}")
            return None

    def generate_net_flow_chart(self, sector_analyses, top_n=10, output_path=None):
        """
        生成资金流向图

        Args:
            sector_analyses: 板块分析结果列表
            top_n: 显示前N个
            output_path: 输出路径

        Returns:
            输出文件路径
        """
        try:
            import matplotlib.pyplot as plt

            # 按资金流向排序
            sorted_sectors = sorted(
                sector_analyses,
                key=lambda x: x.get("net_flow", 0),
                reverse=True,
            )[:top_n]

            names = [s.get("name", "")[-6:] for s in sorted_sectors]
            flows = [s.get("net_flow", 0) for s in sorted_sectors]

            colors = ["#ef4444" if f >= 0 else "#22c55e" for f in flows]

            fig, ax = plt.subplots(
                figsize=(OUTPUT_CONFIG["chart_width"], OUTPUT_CONFIG["chart_height"]),
                dpi=OUTPUT_CONFIG["chart_dpi"],
            )

            bars = ax.barh(names, [f / 10000 for f in flows], color=colors, edgecolor="white", height=0.6)

            for bar, flow in zip(bars, flows):
                ax.text(
                    bar.get_width() + (0.05 if flow >= 0 else -0.05),
                    bar.get_y() + bar.get_height() / 2,
                    f"{flow/10000:+.1f}亿",
                    va="center",
                    fontsize=9,
                )

            ax.set_xlabel("资金流向 (亿元)", fontsize=12)
            ax.set_title(f"资金净流入 TOP {top_n}", fontsize=14, fontweight="bold")
            ax.axvline(x=0, color="gray", linewidth=0.8)

            plt.tight_layout()
            plt.savefig(output_path, bbox_inches="tight")
            plt.close()

            return output_path

        except Exception as e:
            print(f"[错误] 生成资金流向图失败: {e}")
            return None

    def generate_all_charts(self, sector_analyses, output_dir):
        """
        生成所有图表

        Args:
            sector_analyses: 板块分析结果列表
            output_dir: 输出目录

        Returns:
            生成的图表文件路径列表
        """
        os.makedirs(output_dir, exist_ok=True)

        charts = []
        base_time = datetime.now().strftime("%Y%m%d_%H%M%S")

        # 1. 板块涨跌对比图
        path1 = os.path.join(output_dir, f"sector_comparison_{base_time}.png")
        result = self.generate_sector_comparison(sector_analyses, path1)
        if result:
            charts.append(result)

        # 2. 评级分布图
        path2 = os.path.join(output_dir, f"rating_distribution_{base_time}.png")
        result = self.generate_rating_distribution(sector_analyses, path2)
        if result:
            charts.append(result)

        # 3. RSI分布图
        path3 = os.path.join(output_dir, f"rsi_distribution_{base_time}.png")
        result = self.generate_rsi_distribution(sector_analyses, path3)
        if result:
            charts.append(result)

        # 4. 资金流向图
        path4 = os.path.join(output_dir, f"net_flow_{base_time}.png")
        result = self.generate_net_flow_chart(sector_analyses, output_path=path4)
        if result:
            charts.append(result)

        return charts
