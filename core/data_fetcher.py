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

    def _normalize_column_name(self, row, possible_names, default=0):
        """统一获取列值，支持多种列名"""
        for name in possible_names:
            if name in row:
                return row[name]
        return default

    def _normalize_dataframe(self, df):
        """统一 DataFrame 列名格式"""
        if df is None:
            return None
        
        # 东方财富使用'板块名称'，同花顺使用'板块'
        for col in ['板块名称', '板块', 'name']:
            if col in df.columns:
                df = df.rename(columns={col: '板块名称'})
                break
        
        # 涨跌幅统一
        for col in ['涨跌幅', 'change', '行业 - 涨跌幅', '行业 - 涨跌幅']:
            if col in df.columns:
                df = df.rename(columns={col: '涨跌幅'})
                break
        
        # 资金流向统一
        for col in ['净流入', '主力净流入', '净额', 'net_flow']:
            if col in df.columns:
                df = df.rename(columns={col: '资金流向'})
                break
        
        return df

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

            df = self._normalize_dataframe(df)
            if df is None or len(df) == 0:
                return []

            # 转换为目标格式
            result = []
            for _, row in df.head(limit).iterrows():
                name = str(row.get('板块名称', row.get('name', '未知')))
                change = float(row.get('涨跌幅', 0))
                
                # 尝试获取资金流向
                net_flow = self._normalize_column_name(row, ['资金流向', '净流入', '净额', '主力净流入'], 0)
                
                result.append({
                    'f14': name,
                    'f3': change,
                    'f4': float(net_flow) if net_flow else 0,
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

            df = self._normalize_dataframe(df)
            if df is None or len(df) == 0:
                return []

            result = []
            for _, row in df.nsmallest(limit, '涨跌幅').iterrows():
                name = str(row.get('板块名称', row.get('name', '未知')))
                change = float(row.get('涨跌幅', 0))
                
                net_flow = self._normalize_column_name(row, ['资金流向', '净流入', '净额', '主力净流入'], 0)
                
                result.append({
                    'f14': name,
                    'f3': change,
                    'f4': float(net_flow) if net_flow else 0,
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

            df = self._normalize_dataframe(df)
            if df is None:
                return []

            result = []
            for _, row in df.iterrows():
                name = str(row.get('板块名称', row.get('name', '未知')))
                change = float(row.get('涨跌幅', 0))
                
                net_flow = self._normalize_column_name(row, ['资金流向', '净流入', '净额', '主力净流入'], 0)
                
                result.append({
                    'f14': name,
                    'f3': change,
                    'f4': float(net_flow) if net_flow else 0,
                    'f5': 0,
                    'f6': 0,
                    'f62': 0,
                })

            return result
        except Exception as e:
            print(f"[错误] 获取所有板块失败: {e}")
            return []

    def get_multi_source_data(self, limit=50):
        """从多个数据源获取数据（更全面的版本）
        
        返回统一格式的数据列表
        """
        try:
            df = self.manager.fetch_multi_source(limit)
            if df is None or len(df) == 0:
                return []

            df = self._normalize_dataframe(df)
            if df is None:
                return []

            result = []
            for _, row in df.iterrows():
                name = str(row.get('板块名称', row.get('name', '未知')))
                change = float(row.get('涨跌幅', 0))
                
                net_flow = self._normalize_column_name(row, ['资金流向', '净流入', '净额', '主力净流入'], 0)
                
                result.append({
                    'f14': name,
                    'f3': change,
                    'f4': float(net_flow) if net_flow else 0,
                    'f5': 0,
                    'f6': 0,
                    'f62': 0,
                })

            return result
        except Exception as e:
            print(f"[错误] 多数据源获取失败: {e}")
            return []

    def fetch_sector_detail(self, secid):
        """获取板块详情（预留）"""
        return {}

    def fetch_fund_list(self, fund_type="etf", limit=100):
        """获取基金列表（预留）"""
        return []
