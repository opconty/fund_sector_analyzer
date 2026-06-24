"""基金匹配模块 - 将板块与基金关联"""

import json
import os
from config.settings import FUND_LIBRARY_PATH


class FundMatcher:
    """基金匹配器"""

    def __init__(self, library_path=None):
        self.library_path = library_path or FUND_LIBRARY_PATH
        self.fund_library = {}
        self.sector_fund_map = {}
        self._load_library()

    def _load_library(self):
        """加载基金库"""
        try:
            if os.path.exists(self.library_path):
                with open(self.library_path, "r", encoding="utf-8") as f:
                    self.fund_library = json.load(f)
                self._build_sector_map()
            else:
                print(f"[警告] 基金库文件不存在: {self.library_path}")
                self.fund_library = {}
        except Exception as e:
            print(f"[错误] 加载基金库失败: {e}")
            self.fund_library = {}

    def _build_sector_map(self):
        """建立板块到基金的映射"""
        self.sector_fund_map = {}
        for sector_code, sector_info in self.fund_library.items():
            sector_name = sector_info.get("name", "")
            funds = sector_info.get("funds", [])
            self.sector_fund_map[sector_name] = funds
            self.sector_fund_map[sector_code] = funds

    def reload(self):
        """重新加载基金库"""
        self.fund_library = {}
        self.sector_fund_map = {}
        self._load_library()

    def find_funds_by_sector(self, sector_name):
        """
        根据板块名称查找相关基金

        Args:
            sector_name: 板块名称

        Returns:
            基金列表
        """
        # 直接匹配
        if sector_name in self.sector_fund_map:
            return self.sector_fund_map[sector_name]

        # 模糊匹配
        for key, funds in self.sector_fund_map.items():
            if sector_name in key or key in sector_name:
                return funds

        return []

    def find_funds_by_code(self, sector_code):
        """
        根据板块代码查找相关基金

        Args:
            sector_code: 板块代码

        Returns:
            基金列表
        """
        return self.sector_fund_map.get(sector_code, [])

    def get_all_sectors(self):
        """获取所有有基金覆盖的板块"""
        return list(self.fund_library.keys())

    def get_sector_fund_count(self):
        """获取有基金覆盖的板块数量"""
        return len(self.fund_library)

    def format_fund_info(self, fund):
        """格式化基金信息"""
        lines = []
        fund_type = fund.get("type", "未知")
        code = fund.get("code", "未知")
        name = fund.get("name", "未知")
        scale = fund.get("scale", "未知")
        expense = fund.get("expense", "未知")
        tracker = fund.get("tracker", "")

        type_icon = "[ETF]" if fund_type == "ETF" else "[场外]"
        line = f"  {type_icon} {name} ({code})"
        lines.append(line)
        if tracker:
            lines.append(f"     跟踪: {tracker}")
        lines.append(f"     规模: {scale} | 费率: {expense}")

        return "\n".join(lines)

    def match_and_rank(self, sector_analyses):
        """
        将板块分析与基金匹配并排序

        Args:
            sector_analyses: 板块分析结果列表

        Returns:
            匹配的板块-基金列表，按评级排序
        """
        matched = []
        for analysis in sector_analyses:
            sector_name = analysis.get("name", "")
            funds = self.find_funds_by_sector(sector_name)

            if funds:
                matched.append({
                    "analysis": analysis,
                    "funds": funds,
                })

        # 按评级分数排序
        matched.sort(
            key=lambda x: x["analysis"].get("rating_score", 0),
            reverse=True,
        )

        return matched

    def get_top_recommendations(self, limit=10):
        """获取推荐基金列表"""
        recommendations = []
        for sector_code, sector_info in self.fund_library.items():
            for fund in sector_info.get("funds", []):
                recommendations.append({
                    "sector": sector_info.get("name", sector_code),
                    **fund,
                })
        return recommendations[:limit]
