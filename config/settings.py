"""
基金板块分析助手 - 配置管理
"""

import os

# 项目根目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# API配置
EASTMONEY_API = {
    "sector_list_url": "http://push2.eastmoney.com/api/qt/clist/get",
    "sector_detail_url": "http://push2.eastmoney.com/api/qt/stock/get",
    "fund_list_url": "http://push2.eastmoney.com/api/qt/clist/get",
}

# 板块字段映射
SECTOR_FIELDS = "f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f14,f15,f16,f17,f18,f20,f21,f23"

# 板块类型
SECTOR_TYPES = {
    "1": "行业板块",
    "2": "概念板块",
    "3": "地域板块",
}

# 分析参数
ANALYSIS_PARAMS = {
    "short_ma": 5,
    "medium_ma": 20,
    "long_ma": 60,
    "rsi_period": 14,
    "overbought_threshold": 70,
    "oversold_threshold": 30,
    "volume_change_threshold": 1.5,  # 成交量放大倍数
}

# 评级阈值
RATING_THRESHOLDS = {
    "strong_buy": {"min_change": 1.5, "min_volume_flow": 0, "max_rsi": 75},
    "buy": {"min_change": 0.5, "min_volume_flow": 0, "max_rsi": 80},
    "hold": {"min_change": -0.5, "min_volume_flow": -10000, "max_rsi": 85},
    "cautious": {"min_change": -2.0, "min_volume_flow": -50000, "max_rsi": 90},
    "avoid": {"min_change": -999, "min_volume_flow": -999999, "max_rsi": 100},
}

# 基金库路径
FUND_LIBRARY_PATH = os.path.join(BASE_DIR, "data", "fund_library.json")

# 输出配置
OUTPUT_CONFIG = {
    "chart_format": "png",
    "chart_dpi": 150,
    "chart_width": 12,
    "chart_height": 8,
    "chart_font_path": None,  # Windows可能需要指定中文字体路径
}

# 缓存配置
CACHE_CONFIG = {
    "ttl": 300,  # 缓存过期时间（秒）
    "cache_dir": os.path.join(BASE_DIR, "data", "cache"),
}

# 确保缓存目录存在
os.makedirs(CACHE_CONFIG["cache_dir"], exist_ok=True)
