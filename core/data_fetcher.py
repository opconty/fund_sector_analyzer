"""数据抓取模块 - 支持多数据源切换"""

import time
from core.data_source_manager import DataSourceManager


class DataFetcher:
    """数据抓取器 - 自动切换数据源"""

    def __init__(self):
        self.manager = DataSourceManager()
        self._cache = {}
        self._cache_time = {}

    def _get_cached(self, key):
        """获取缓存数据"""
        if key in self._cache and (time.time() - self._cache_time.get(key, 0)) < 300:
            return self._cache[key]
        return None

    def _set_cache(self, key, data):
        """设置缓存"""
        self._cache[key] = data
        self._cache_time[key] = time.time()

    def fetch_top_gainers(self, limit=30):
        """获取涨幅前 N 的行业板块"""
        cache_key = f"gainers_{limit}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached

        try:
            df = self.manager.fetch_with_fallback(limit)
            if df is None:
                return []

            # 转换为统一格式
            result = []
            for _, row in df.head(limit).iterrows():
                name = str(row['板块名称']) if '板块名称' in row else str(row['name'])
                change = float(row['涨跌幅']) if '涨跌幅' in row else 0
                result.append({
                    'f14': name,
                    'f3': change,
                    'f4': 0,
                    'f5': 0,
                    'f6': 0,
                    'f62': 0,
                })

            self._set_cache(cache_key, result)
            return result
        except Exception as e:
            print(f"[警告] 获取涨幅板块失败: {e}")
            return []

    def fetch_top_losers(self, limit=30):
        """获取跌幅前 N 的行业板块"""
        cache_key = f"losers_{limit}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached

        try:
            df = self.manager.fetch_with_fallback(limit)
            if df is None:
                return []

            # 转换为统一格式
            result = []
            for _, row in df.nsmallest(limit, '涨跌幅').iterrows():
                name = str(row['板块名称']) if '板块名称' in row else str(row['name'])
                change = float(row['涨跌幅']) if '涨跌幅' in row else 0
                result.append({
                    'f14': name,
                    'f3': change,
                    'f4': 0,
                    'f5': 0,
                    'f6': 0,
                    'f62': 0,
                })

            self._set_cache(cache_key, result)
            return result
        except Exception as e:
            print(f"[警告] 获取跌幅板块失败: {e}")
            return []

    def get_all_sectors(self):
        """获取所有行业板块数据"""
        try:
            df = self.manager.fetch_with_fallback()
            if df is None:
                return []

            result = []
            for _, row in df.iterrows():
                name = str(row['板块名称']) if '板块名称' in row else str(row['name'])
                change = float(row['涨跌幅']) if '涨跌幅' in row else 0
                result.append({
                    'f14': name,
                    'f3': change,
                    'f4': 0,
                    'f5': 0,
                    'f6': 0,
                    'f62': 0,
                })

            return result
        except Exception as e:
            print(f"[错误] 获取所有板块失败: {e}")
            return []

    def fetch_sector_detail(self, secid):
        """获取板块详情（预留）"""
        return {}

    def fetch_fund_list(self, fund_type="etf", limit=100):
        """获取基金列表（预留）"""
        return []
