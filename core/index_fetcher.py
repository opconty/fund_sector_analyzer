"""指数行情数据获取模块"""

import pandas as pd


class IndexFetcher:
    """指数行情数据获取器"""

    def __init__(self):
        self._sources = {
            'sina': self._fetch_sina,
        }
        self._current_source = None

    def _fetch_sina(self):
        """新浪财经 - A 股指数"""
        try:
            import akshare as ak
            print("  [新浪] 获取 A 股指数...")
            df = ak.stock_zh_index_spot_sina()
            return df
        except Exception as e:
            print(f"  [新浪] 失败: {e}")
            return None

    def fetch_a_stock_indices(self):
        """获取 A 股主要指数"""
        df = self._fetch_sina()
        if df is None:
            return []

        majors = ['上证指数', '深证成指', '创业板指', '科创 50', '沪深 300']
        df_majors = df[df['名称'].isin(majors)]

        result = []
        for _, row in df_majors.iterrows():
            result.append({
                'name': str(row['名称']),
                'price': float(row['最新价']),
                'change_pct': float(row['涨跌幅']),
                'volume': float(row['成交额']) if '成交额' in row else 0,
            })

        return result

    def fetch_global_indices(self):
        """获取全球主要指数（模拟数据，因网络限制）"""
        print("[数据源] 全球指数获取受限，使用模拟数据")
        return [
            {'name': '标普 500', 'price': 5200.00, 'change_pct': 0.50, 'volume': 0},
            {'name': '纳斯达克', 'price': 16500.00, 'change_pct': 1.20, 'volume': 0},
            {'name': '道琼斯', 'price': 41000.00, 'change_pct': 0.30, 'volume': 0},
            {'name': '恒生指数', 'price': 21000.00, 'change_pct': -0.15, 'volume': 0},
            {'name': '日经 225', 'price': 38500.00, 'change_pct': 0.80, 'volume': 0},
        ]
