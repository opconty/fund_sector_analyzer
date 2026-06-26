"""多数据源管理器 - 支持东方财富、同花顺、新浪财经等"""

import time
import pandas as pd


class DataSourceManager:
    """数据源管理器，支持多数据源切换"""

    def __init__(self):
        self._sources = {
            'eastmoney_industry': self._fetch_eastmoney_industry,
            'eastmoney_concept': self._fetch_eastmoney_concept,
            'ths_industry': self._fetch_ths_industry,
            'ths_concept': self._fetch_ths_concept,
            'sina_fund_flow_industry': self._fetch_sina_fund_flow_industry,
            'sina_fund_flow_concept': self._fetch_sina_fund_flow_concept,
        }
        self._current_source = None

    def _fetch_eastmoney_industry(self, limit=30):
        """东方财富 - 行业板块"""
        try:
            import akshare as ak
            print("  [东财] 获取行业板块...")
            df = ak.stock_board_industry_name_em()
            df = df.rename(columns={'板块名称': 'name', '涨跌幅': 'change'})
            return df
        except Exception as e:
            print(f"  [东财] 失败: {e}")
            return None

    def _fetch_eastmoney_concept(self, limit=30):
        """东方财富 - 概念板块"""
        try:
            import akshare as ak
            print("  [东财] 获取概念板块...")
            df = ak.stock_board_concept_name_em()
            df = df.rename(columns={'板块名称': 'name', '涨跌幅': 'change'})
            return df
        except Exception as e:
            print(f"  [东财] 失败: {e}")
            return None

    def _fetch_ths_industry(self, limit=30):
        """同花顺 - 行业板块"""
        try:
            import akshare as ak
            print("  [同花顺] 获取行业板块...")
            df = ak.stock_board_industry_name_ths()
            if len(df) == 0:
                return None
            print(f"  [同花顺] 板块列表: {len(df)} 个")
            result = pd.DataFrame()
            result['name'] = df['name'].astype(str).head(limit).tolist()
            result['change'] = 0.0
            return result
        except Exception as e:
            print(f"  [同花顺] 失败: {e}")
            return None

    def _fetch_ths_concept(self, limit=30):
        """同花顺 - 概念板块"""
        try:
            import akshare as ak
            print("  [同花顺] 获取概念板块...")
            df = ak.stock_board_concept_name_ths()
            if len(df) == 0:
                return None
            print(f"  [同花顺] 板块列表: {len(df)} 个")
            result = pd.DataFrame()
            result['name'] = df['name'].astype(str).head(limit).tolist()
            result['change'] = 0.0
            return result
        except Exception as e:
            print(f"  [同花顺] 失败: {e}")
            return None

    def _fetch_sina_fund_flow_industry(self):
        """新浪财经 - 行业板块资金流向"""
        try:
            import akshare as ak
            print("  [新浪] 获取行业板块资金流向...")
            df = ak.stock_fund_flow_industry()
            if df is not None and len(df) > 0:
                print(f"  [新浪] 行业资金流向: {len(df)} 条")
                # 不修改原始数据，直接返回
                return df.copy()
            return None
        except Exception as e:
            print(f"  [新浪] 行业资金流向失败: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _fetch_sina_fund_flow_concept(self):
        """新浪财经 - 概念板块资金流向"""
        try:
            import akshare as ak
            print("  [新浪] 获取概念板块资金流向...")
            df = ak.stock_fund_flow_concept()
            if df is not None and len(df) > 0:
                print(f"  [新浪] 概念资金流向: {len(df)} 条")
                # 不修改原始数据，直接返回
                return df.copy()
            return None
        except Exception as e:
            print(f"  [新浪] 概念资金流向失败: {e}")
            return None

    def fetch_with_fallback(self, limit=30):
        """按优先级尝试各数据源获取板块数据"""
        sources = ['eastmoney_industry', 'eastmoney_concept', 'ths_industry', 'ths_concept']
        for source_name in sources:
            if source_name not in self._sources:
                continue
            print(f"[数据源] 尝试 {source_name}...")
            try:
                df = self._sources[source_name](limit)
                if df is not None and len(df) > 0:
                    print(f"[数据源] {source_name} 获取成功，{len(df)} 条记录")
                    self._current_source = source_name
                    return df
            except Exception as e:
                print(f"[数据源] {source_name} 异常: {e}")
                continue
        print("[数据源] 所有数据源获取失败")
        return None

    def fetch_fund_flow(self, flow_type='industry'):
        """获取资金流向数据"""
        if flow_type == 'industry':
            source_name = 'sina_fund_flow_industry'
        else:
            source_name = 'sina_fund_flow_concept'

        print(f"[数据源] 尝试 {source_name}...")
        try:
            df = self._sources[source_name]()
            if df is not None:
                self._current_source = source_name
                return df
        except Exception as e:
            print(f"[数据源] {source_name} 异常: {e}")
        print("[数据源] 资金流向获取失败")
        return None

    def get_current_source(self):
        """获取当前使用的数据源"""
        return self._current_source
