"""多数据源管理器 - 支持东方财富、同花顺、新浪财经等，自动 fallback"""

import time
import pandas as pd


class DataSourceManager:
    """数据源管理器，支持多数据源切换和自动 fallback"""

    def __init__(self):
        # 数据源注册：名称 -> (函数，优先级，数据类别)
        # 优先级：数字越小越优先
        self._sources = {
            # ==================== 东方财富 ====================
            'eastmoney_industry': {
                'func': self._fetch_eastmoney_industry,
                'priority': 1,
                'category': 'sector',
            },
            'eastmoney_concept': {
                'func': self._fetch_eastmoney_concept,
                'priority': 1,
                'category': 'sector',
            },
            'eastmoney_industry_spot': {
                'func': self._fetch_eastmoney_industry_spot,
                'priority': 2,
                'category': 'sector',
            },
            'eastmoney_concept_spot': {
                'func': self._fetch_eastmoney_concept_spot,
                'priority': 2,
                'category': 'sector',
            },
            'eastmoney_etf_spot': {
                'func': self._fetch_eastmoney_etf_spot,
                'priority': 1,
                'category': 'etf',
            },
            'eastmoney_fund_hold': {
                'func': self._fetch_eastmoney_fund_hold,
                'priority': 1,
                'category': 'fund_hold',
            },
            'eastmoney_fund_allocation': {
                'func': self._fetch_eastmoney_fund_allocation,
                'priority': 1,
                'category': 'fund_allocation',
            },
            'eastmoney_fund_name': {
                'func': self._fetch_eastmoney_fund_name,
                'priority': 1,
                'category': 'fund_name',
            },
            'eastmoney_gpzy_industry': {
                'func': self._fetch_eastmoney_gpzy_industry,
                'priority': 1,
                'category': 'gpzy',
            },
            # ==================== 同花顺 ====================
            'ths_industry_summary': {
                'func': self._fetch_ths_industry_summary,
                'priority': 1,
                'category': 'sector',
            },
            'ths_industry': {
                'func': self._fetch_ths_industry,
                'priority': 3,
                'category': 'sector',
            },
            'ths_concept_summary': {
                'func': self._fetch_ths_concept_summary,
                'priority': 1,
                'category': 'sector',
            },
            'ths_concept': {
                'func': self._fetch_ths_concept,
                'priority': 3,
                'category': 'sector',
            },
            # ==================== 新浪财经 ====================
            'sina_fund_flow_industry': {
                'func': self._fetch_sina_fund_flow_industry,
                'priority': 1,
                'category': 'fund_flow',
            },
            'sina_fund_flow_concept': {
                'func': self._fetch_sina_fund_flow_concept,
                'priority': 1,
                'category': 'fund_flow',
            },
            'sina_index_spot': {
                'func': self._fetch_sina_index_spot,
                'priority': 1,
                'category': 'index',
            },
            'sina_index_daily': {
                'func': self._fetch_sina_index_daily,
                'priority': 1,
                'category': 'index',
            },
            # ==================== 外汇 ====================
            'fx_spot': {
                'func': self._fetch_fx_spot,
                'priority': 1,
                'category': 'fx',
            },
            'fx_pair': {
                'func': self._fetch_fx_pair,
                'priority': 2,
                'category': 'fx',
            },
            'fx_boc_safe': {
                'func': self._fetch_fx_boc_safe,
                'priority': 1,
                'category': 'fx',
            },
            # ==================== 宏观经济 ====================
            'macro_gdp': {
                'func': self._fetch_macro_gdp,
                'priority': 1,
                'category': 'macro',
            },
            'macro_cpi': {
                'func': self._fetch_macro_cpi,
                'priority': 1,
                'category': 'macro',
            },
            'macro_ppi': {
                'func': self._fetch_macro_ppi,
                'priority': 1,
                'category': 'macro',
            },
            'macro_money_supply': {
                'func': self._fetch_macro_money_supply,
                'priority': 1,
                'category': 'macro',
            },
            'macro_margin_sz': {
                'func': self._fetch_macro_margin_sz,
                'priority': 1,
                'category': 'macro',
            },
            'macro_margin_sh': {
                'func': self._fetch_macro_margin_sh,
                'priority': 1,
                'category': 'macro',
            },
            'macro_supply_of_money': {
                'func': self._fetch_macro_supply_of_money,
                'priority': 1,
                'category': 'macro',
            },
            'macro_hk_cpi': {
                'func': self._fetch_macro_hk_cpi,
                'priority': 1,
                'category': 'macro',
            },
            'macro_lpr': {
                'func': self._fetch_macro_lpr,
                'priority': 1,
                'category': 'macro',
            },
            'macro_shrzgm': {
                'func': self._fetch_macro_shrzgm,
                'priority': 1,
                'category': 'macro',
            },
            # ==================== 交易所 ====================
            'sse_summary': {
                'func': self._fetch_sse_summary,
                'priority': 1,
                'category': 'exchange',
            },
            # ==================== A 股实时 ====================
            'stock_zh_a_spot': {
                'func': self._fetch_stock_zh_a_spot,
                'priority': 1,
                'category': 'stock_spot',
            },
            'stock_info_a_code_name': {
                'func': self._fetch_stock_info_a_code_name,
                'priority': 1,
                'category': 'stock_info',
            },
            # ==================== 美股/全球指数 ====================
            'futures_global_spot': {
                'func': self._fetch_futures_global_spot,
                'priority': 1,
                'category': 'global_futures',
            },
            'macro_sox_index': {
                'func': self._fetch_macro_sox_index,
                'priority': 1,
                'category': 'global_index',
            },
            'index_global_name_table': {
                'func': self._fetch_index_global_name_table,
                'priority': 1,
                'category': 'global_index',
            },
            # ==================== 全球资讯 ====================
            'stock_info_global_em': {
                'func': self._fetch_stock_info_global_em,
                'priority': 1,
                'category': 'global_news',
            },
            'stock_info_global_sina': {
                'func': self._fetch_stock_info_global_sina,
                'priority': 1,
                'category': 'global_news',
            },
            'stock_info_global_ths': {
                'func': self._fetch_stock_info_global_ths,
                'priority': 1,
                'category': 'global_news',
            },
            'stock_info_global_futu': {
                'func': self._fetch_stock_info_global_futu,
                'priority': 1,
                'category': 'global_news',
            },
            'stock_info_global_cls': {
                'func': self._fetch_stock_info_global_cls,
                'priority': 1,
                'category': 'global_news',
            },
        }
        self._current_source = None

    # ==================== 东方财富 ====================

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

    def _fetch_eastmoney_industry_spot(self, limit=30):
        """东方财富 - 行业板块实时行情"""
        try:
            import akshare as ak
            print("  [东财] 获取行业板块实时行情...")
            df = ak.stock_board_industry_spot_em()
            if df is not None and len(df) > 0:
                print(f"  [东财] 行业板块实时行情: {len(df)} 个")
                return df.head(limit).copy()
            return None
        except Exception as e:
            print(f"  [东财] 实时行情失败: {e}")
            return None

    def _fetch_eastmoney_concept_spot(self, limit=30):
        """东方财富 - 概念板块实时行情"""
        try:
            import akshare as ak
            print("  [东财] 获取概念板块实时行情...")
            df = ak.stock_board_concept_spot_em()
            if df is not None and len(df) > 0:
                print(f"  [东财] 概念板块实时行情: {len(df)} 个")
                return df.head(limit).copy()
            return None
        except Exception as e:
            print(f"  [东财] 概念实时行情失败: {e}")
            return None

    def _fetch_eastmoney_etf_spot(self, limit=30):
        """东方财富 - ETF 实时行情（1528 只）"""
        try:
            import akshare as ak
            print("  [东财] 获取 ETF 实时行情...")
            df = ak.fund_etf_spot_em()
            if df is not None and len(df) > 0:
                print(f"  [东财] ETF 实时行情: {len(df)} 只")
                return df.head(limit).copy()
            return None
        except Exception as e:
            print(f"  [东财] ETF 实时行情失败: {e}")
            return None

    def _fetch_eastmoney_fund_hold(self, limit=30):
        """东方财富 - 基金持仓"""
        try:
            import akshare as ak
            print("  [东财] 获取基金持仓...")
            df = ak.fund_portfolio_hold_em(symbol="000001", date="2023")
            if df is not None and len(df) > 0:
                print(f"  [东财] 基金持仓: {len(df)} 条")
                return df.head(limit).copy()
            return None
        except Exception as e:
            print(f"  [东财] 基金持仓失败: {e}")
            return None

    def _fetch_eastmoney_fund_allocation(self, limit=30):
        """东方财富 - 基金资产配置"""
        try:
            import akshare as ak
            print("  [东财] 获取基金资产配置...")
            df = ak.fund_report_asset_allocation_cninfo(symbol="000001")
            if df is not None and len(df) > 0:
                print(f"  [东财] 基金资产配置: {len(df)} 条")
                return df.head(limit).copy()
            return None
        except Exception as e:
            print(f"  [东财] 基金资产配置失败: {e}")
            return None

    def _fetch_eastmoney_fund_name(self, limit=30):
        """东方财富 - 基金名称列表（27201 只）"""
        try:
            import akshare as ak
            print("  [东财] 获取基金名称列表...")
            df = ak.fund_name_em()
            if df is not None and len(df) > 0:
                print(f"  [东财] 基金名称: {len(df)} 只")
                return df.head(limit).copy()
            return None
        except Exception as e:
            print(f"  [东财] 基金名称失败: {e}")
            return None

    def _fetch_eastmoney_gpzy_industry(self, limit=30):
        """东方财富 - 股市质押行业"""
        try:
            import akshare as ak
            print("  [东财] 获取股市质押行业...")
            df = ak.stock_gpzy_industry_data_em()
            if df is not None and len(df) > 0:
                print(f"  [东财] 股市质押行业: {len(df)} 条")
                return df.head(limit).copy()
            return None
        except Exception as e:
            print(f"  [东财] 股市质押行业失败: {e}")
            return None

    # ==================== 同花顺 ====================

    def _fetch_ths_industry_summary(self, limit=30):
        """同花顺 - 行业板块汇总"""
        try:
            import akshare as ak
            print("  [同花顺] 获取行业板块汇总数据...")
            df = ak.stock_board_industry_summary_ths()
            if df is not None and len(df) > 0:
                print(f"  [同花顺] 行业板块汇总: {len(df)} 个")
                try:
                    df.columns = [c.encode('gbk', errors='ignore').decode('utf-8') for c in df.columns]
                except:
                    pass
                return df.head(limit).copy()
            return None
        except Exception as e:
            print(f"  [同花顺] 汇总数据失败: {e}")
            return None

    def _fetch_ths_industry(self, limit=30):
        """同花顺 - 行业板块名称"""
        try:
            import akshare as ak
            print("  [同花顺] 获取行业板块列表...")
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

    def _fetch_ths_concept_summary(self, limit=30):
        """同花顺 - 概念板块汇总"""
        try:
            import akshare as ak
            print("  [同花顺] 获取概念板块汇总数据...")
            df = ak.stock_board_concept_summary_ths()
            if df is not None and len(df) > 0:
                print(f"  [同花顺] 概念板块汇总: {len(df)} 个")
                try:
                    df.columns = [c.encode('gbk', errors='ignore').decode('utf-8') for c in df.columns]
                except:
                    pass
                return df.head(limit).copy()
            return None
        except Exception as e:
            print(f"  [同花顺] 概念汇总失败: {e}")
            return None

    def _fetch_ths_concept(self, limit=30):
        """同花顺 - 概念板块名称"""
        try:
            import akshare as ak
            print("  [同花顺] 获取概念板块列表...")
            df = ak.stock_board_concept_name_ths()
            if len(df) == 0:
                return None
            print(f"  [同花顺] 概念板块列表: {len(df)} 个")
            result = pd.DataFrame()
            result['name'] = df['name'].astype(str).head(limit).tolist()
            result['change'] = 0.0
            return result
        except Exception as e:
            print(f"  [同花顺] 失败: {e}")
            return None

    # ==================== 新浪财经 ====================

    def _fetch_sina_fund_flow_industry(self):
        """新浪财经 - 行业板块资金流向"""
        try:
            import akshare as ak
            print("  [新浪] 获取行业板块资金流向...")
            df = ak.stock_fund_flow_industry()
            if df is not None and len(df) > 0:
                print(f"  [新浪] 行业资金流向: {len(df)} 条")
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
                return df.copy()
            return None
        except Exception as e:
            print(f"  [新浪] 概念资金流向失败: {e}")
            return None

    def _fetch_sina_index_spot(self, limit=30):
        """新浪 - A 股指数实时行情（562 个）"""
        try:
            import akshare as ak
            print("  [新浪] 获取 A 股指数行情...")
            df = ak.stock_zh_index_spot_sina()
            if df is not None and len(df) > 0:
                print(f"  [新浪] A 股指数行情: {len(df)} 个")
                return df.head(limit).copy()
            return None
        except Exception as e:
            print(f"  [新浪] A 股指数行情失败: {e}")
            return None

    def _fetch_sina_index_daily(self, symbol="sh000001"):
        """新浪 - 指数历史日线数据"""
        try:
            import akshare as ak
            print("  [新浪] 获取指数历史数据...")
            df = ak.stock_zh_index_daily(symbol=symbol)
            if df is not None and len(df) > 0:
                print(f"  [新浪] 指数历史数据: {len(df)} 条")
                return df.head(30).copy()
            return None
        except Exception as e:
            print(f"  [新浪] 指数历史数据失败: {e}")
            return None

    # ==================== 外汇 ====================

    def _fetch_fx_spot(self, limit=10):
        """外汇 - 实时汇率（25 对）"""
        try:
            import akshare as ak
            print("  [外汇] 获取实时汇率...")
            df = ak.fx_spot_quote()
            if df is not None and len(df) > 0:
                print(f"  [外汇] 实时汇率: {len(df)} 对")
                return df.head(limit).copy()
            return None
        except Exception as e:
            print(f"  [外汇] 实时汇率失败: {e}")
            return None

    def _fetch_fx_pair(self, limit=10):
        """外汇 - 货币对汇率（16 对）"""
        try:
            import akshare as ak
            print("  [外汇] 获取货币对汇率...")
            df = ak.fx_pair_quote()
            if df is not None and len(df) > 0:
                print(f"  [外汇] 货币对汇率: {len(df)} 对")
                return df.head(limit).copy()
            return None
        except Exception as e:
            print(f"  [外汇] 货币对汇率失败: {e}")
            return None

    def _fetch_fx_boc_safe(self, limit=10):
        """外汇 - 央行汇率（7997 条）"""
        try:
            import akshare as ak
            print("  [外汇] 获取央行汇率...")
            df = ak.currency_boc_safe()
            if df is not None and len(df) > 0:
                print(f"  [外汇] 央行汇率: {len(df)} 条")
                return df.head(limit).copy()
            return None
        except Exception as e:
            print(f"  [外汇] 央行汇率失败: {e}")
            return None

    # ==================== 宏观经济 ====================

    def _fetch_macro_gdp(self, limit=10):
        """宏观 - GDP（81 条）"""
        try:
            import akshare as ak
            print("  [宏观] 获取 GDP 数据...")
            df = ak.macro_china_gdp()
            if df is not None and len(df) > 0:
                print(f"  [宏观] GDP: {len(df)} 条")
                return df.head(limit).copy()
            return None
        except Exception as e:
            print(f"  [宏观] GDP 失败: {e}")
            return None

    def _fetch_macro_cpi(self, limit=10):
        """宏观 - CPI（221 条）"""
        try:
            import akshare as ak
            print("  [宏观] 获取 CPI 数据...")
            df = ak.macro_china_cpi()
            if df is not None and len(df) > 0:
                print(f"  [宏观] CPI: {len(df)} 条")
                return df.head(limit).copy()
            return None
        except Exception as e:
            print(f"  [宏观] CPI 失败: {e}")
            return None

    def _fetch_macro_ppi(self, limit=10):
        """宏观 - PPI（245 条）"""
        try:
            import akshare as ak
            print("  [宏观] 获取 PPI 数据...")
            df = ak.macro_china_ppi()
            if df is not None and len(df) > 0:
                print(f"  [宏观] PPI: {len(df)} 条")
                return df.head(limit).copy()
            return None
        except Exception as e:
            print(f"  [宏观] PPI 失败: {e}")
            return None

    def _fetch_macro_money_supply(self, limit=10):
        """宏观 - 货币供应（221 条）"""
        try:
            import akshare as ak
            print("  [宏观] 获取货币供应数据...")
            df = ak.macro_china_money_supply()
            if df is not None and len(df) > 0:
                print(f"  [宏观] 货币供应: {len(df)} 条")
                return df.head(limit).copy()
            return None
        except Exception as e:
            print(f"  [宏观] 货币供应失败: {e}")
            return None

    def _fetch_macro_margin_sz(self, limit=10):
        """宏观 - 深市融资融券（3745 条）"""
        try:
            import akshare as ak
            print("  [宏观] 获取深市融资融券...")
            df = ak.macro_china_market_margin_sz()
            if df is not None and len(df) > 0:
                print(f"  [宏观] 深市融资融券: {len(df)} 条")
                return df.head(limit).copy()
            return None
        except Exception as e:
            print(f"  [宏观] 深市融资融券失败: {e}")
            return None

    def _fetch_macro_margin_sh(self, limit=10):
        """宏观 - 沪市融资融券（3943 条）"""
        try:
            import akshare as ak
            print("  [宏观] 获取沪市融资融券...")
            df = ak.macro_china_market_margin_sh()
            if df is not None and len(df) > 0:
                print(f"  [宏观] 沪市融资融券: {len(df)} 条")
                return df.head(limit).copy()
            return None
        except Exception as e:
            print(f"  [宏观] 沪市融资融券失败: {e}")
            return None

    def _fetch_macro_supply_of_money(self, limit=10):
        """宏观 - 货币供应量（581 条）"""
        try:
            import akshare as ak
            print("  [宏观] 获取货币供应量...")
            df = ak.macro_china_supply_of_money()
            if df is not None and len(df) > 0:
                print(f"  [宏观] 货币供应量: {len(df)} 条")
                return df.head(limit).copy()
            return None
        except Exception as e:
            print(f"  [宏观] 货币供应量失败: {e}")
            return None

    def _fetch_macro_hk_cpi(self, limit=10):
        """宏观 - 香港 CPI（172 条）"""
        try:
            import akshare as ak
            print("  [宏观] 获取香港 CPI...")
            df = ak.macro_china_hk_cpi()
            if df is not None and len(df) > 0:
                print(f"  [宏观] 香港 CPI: {len(df)} 条")
                return df.head(limit).copy()
            return None
        except Exception as e:
            print(f"  [宏观] 香港 CPI 失败: {e}")
            return None

    def _fetch_macro_lpr(self, limit=10):
        """宏观 - LPR（1573 条）"""
        try:
            import akshare as ak
            print("  [宏观] 获取 LPR...")
            df = ak.macro_china_lpr()
            if df is not None and len(df) > 0:
                print(f"  [宏观] LPR: {len(df)} 条")
                return df.head(limit).copy()
            return None
        except Exception as e:
            print(f"  [宏观] LPR 失败: {e}")
            return None

    def _fetch_macro_shrzgm(self, limit=10):
        """宏观 - 社会融资规模（136 条）"""
        try:
            import akshare as ak
            print("  [宏观] 获取社会融资规模...")
            df = ak.macro_china_shrzgm()
            if df is not None and len(df) > 0:
                print(f"  [宏观] 社会融资规模: {len(df)} 条")
                return df.head(limit).copy()
            return None
        except Exception as e:
            print(f"  [宏观] 社会融资规模失败: {e}")
            return None

    # ==================== 交易所 ====================

    def _fetch_sse_summary(self, limit=10):
        """上交所 - 每日概况（8 条）"""
        try:
            import akshare as ak
            print("  [上交所] 获取每日概况...")
            df = ak.stock_sse_summary()
            if df is not None and len(df) > 0:
                print(f"  [上交所] 每日概况: {len(df)} 条")
                return df.head(limit).copy()
            return None
        except Exception as e:
            print(f"  [上交所] 每日概况失败: {e}")
            return None

    # ==================== A 股实时 ====================

    def _fetch_stock_zh_a_spot(self, limit=30):
        """A 股实时行情（5527 只）"""
        try:
            import akshare as ak
            print("  [A 股] 获取实时行情...")
            df = ak.stock_zh_a_spot()
            if df is not None and len(df) > 0:
                print(f"  [A 股] 实时行情: {len(df)} 只")
                return df.head(limit).copy()
            return None
        except Exception as e:
            print(f"  [A 股] 实时行情失败: {e}")
            return None

    def _fetch_stock_info_a_code_name(self, limit=30):
        """A 股代码名称（5528 只）"""
        try:
            import akshare as ak
            print("  [A 股] 获取代码名称...")
            df = ak.stock_info_a_code_name()
            if df is not None and len(df) > 0:
                print(f"  [A 股] 代码名称: {len(df)} 只")
                return df.head(limit).copy()
            return None
        except Exception as e:
            print(f"  [A 股] 代码名称失败: {e}")
            return None

    # ==================== 美股/全球指数 ====================

    def _fetch_futures_global_spot(self, limit=30):
        """东方财富 - 全球期货实时行情（620 个合约，含标普/纳指期货）"""
        try:
            import akshare as ak
            print("  [全球期货] 获取全球期货实时行情...")
            df = ak.futures_global_spot_em()
            if df is not None and len(df) > 0:
                print(f"  [全球期货] 期货行情: {len(df)} 个合约")
                return df.head(limit).copy()
            return None
        except Exception as e:
            print(f"  [全球期货] 期货行情失败: {e}")
            return None

    def _fetch_macro_sox_index(self, limit=30):
        """SOX 费城半导体指数历史数据（8029 条）"""
        try:
            import akshare as ak
            print("  [SOX] 获取费城半导体指数...")
            df = ak.macro_global_sox_index()
            if df is not None and len(df) > 0:
                print(f"  [SOX] 半导体指数: {len(df)} 条")
                return df.tail(limit).copy()
            return None
        except Exception as e:
            print(f"  [SOX] 半导体指数失败: {e}")
            return None

    def _fetch_index_global_name_table(self, limit=30):
        """全球指数代码表（20 个指数）"""
        try:
            import akshare as ak
            print("  [全球指数] 获取指数代码表...")
            df = ak.index_global_name_table()
            if df is not None and len(df) > 0:
                print(f"  [全球指数] 代码表: {len(df)} 个指数")
                return df.head(limit).copy()
            return None
        except Exception as e:
            print(f"  [全球指数] 代码表失败: {e}")
            return None

    # ==================== 全球资讯 ====================

    def _fetch_stock_info_global_em(self, limit=30):
        """东方财富 - 全球财经资讯"""
        try:
            import akshare as ak
            print("  [东财] 获取全球财经资讯...")
            df = ak.stock_info_global_em()
            if df is not None and len(df) > 0:
                print(f"  [东财] 全球资讯: {len(df)} 条")
                return df.head(limit).copy()
            return None
        except Exception as e:
            print(f"  [东财] 全球资讯失败: {e}")
            return None

    def _fetch_stock_info_global_sina(self, limit=30):
        """新浪财经 - 全球财经资讯"""
        try:
            import akshare as ak
            print("  [新浪] 获取全球财经资讯...")
            df = ak.stock_info_global_sina()
            if df is not None and len(df) > 0:
                print(f"  [新浪] 全球资讯: {len(df)} 条")
                return df.head(limit).copy()
            return None
        except Exception as e:
            print(f"  [新浪] 全球资讯失败: {e}")
            return None

    def _fetch_stock_info_global_ths(self, limit=30):
        """同花顺 - 全球财经资讯"""
        try:
            import akshare as ak
            print("  [同花顺] 获取全球财经资讯...")
            df = ak.stock_info_global_ths()
            if df is not None and len(df) > 0:
                print(f"  [同花顺] 全球资讯: {len(df)} 条")
                return df.head(limit).copy()
            return None
        except Exception as e:
            print(f"  [同花顺] 全球资讯失败: {e}")
            return None

    def _fetch_stock_info_global_futu(self, limit=30):
        """富途 - 全球财经资讯"""
        try:
            import akshare as ak
            print("  [富途] 获取全球财经资讯...")
            df = ak.stock_info_global_futu()
            if df is not None and len(df) > 0:
                print(f"  [富途] 全球资讯: {len(df)} 条")
                return df.head(limit).copy()
            return None
        except Exception as e:
            print(f"  [富途] 全球资讯失败: {e}")
            return None

    def _fetch_stock_info_global_cls(self, limit=30, symbol="要闻"):
        """财联社 - 全球财经资讯"""
        try:
            import akshare as ak
            print("  [财联社] 获取全球财经资讯...")
            df = ak.stock_info_global_cls(symbol=symbol)
            if df is not None and len(df) > 0:
                print(f"  [财联社] 全球资讯: {len(df)} 条")
                return df.head(limit).copy()
            return None
        except Exception as e:
            print(f"  [财联社] 全球资讯失败: {e}")
            return None

    # ==================== 通用方法 ====================

    def fetch_with_fallback(self, limit=30, category='sector'):
        """按优先级尝试各数据源获取数据，自动 fallback"""
        available_sources = [
            (name, info) for name, info in self._sources.items()
            if info['category'] == category
        ]
        available_sources.sort(key=lambda x: x[1]['priority'])
        
        success_sources = []
        for source_name, info in available_sources:
            print(f"[数据源] 尝试 {source_name}...")
            try:
                df = info['func'](limit)
                if df is not None and len(df) > 0:
                    print(f"[数据源] {source_name} 获取成功，{len(df)} 条记录")
                    self._current_source = source_name
                    success_sources.append(source_name)
                    return df
            except Exception as e:
                print(f"[数据源] {source_name} 异常: {e}")
                continue
        
        if success_sources:
            print(f"[提示] 主数据源失败，使用备用数据源: {', '.join(success_sources)}")
        
        print("[数据源] 所有数据源获取失败")
        return None

    def fetch_fund_flow(self, flow_type='industry', category='fund_flow'):
        """获取资金流向数据，支持自动 fallback"""
        available_sources = [
            (name, info) for name, info in self._sources.items()
            if info['category'] == category
        ]
        available_sources.sort(key=lambda x: x[1]['priority'])
        
        for source_name, info in available_sources:
            print(f"[数据源] 尝试 {source_name}...")
            try:
                df = info['func']()
                if df is not None:
                    self._current_source = source_name
                    return df
            except Exception as e:
                print(f"[数据源] {source_name} 异常: {e}")
                continue
        
        print("[数据源] 资金流向获取失败")
        return None

    def fetch_multi_source(self, limit=30, category='sector'):
        """从多个数据源获取数据并合并"""
        available_sources = [
            (name, info) for name, info in self._sources.items()
            if info['category'] == category
        ]
        available_sources.sort(key=lambda x: x[1]['priority'])
        
        all_data = []
        success_sources = []
        
        for source_name, info in available_sources:
            print(f"[数据源] 尝试 {source_name}...")
            try:
                df = info['func'](limit)
                if df is not None and len(df) > 0:
                    print(f"[数据源] {source_name} 获取成功，{len(df)} 条记录")
                    self._current_source = source_name
                    success_sources.append(source_name)
                    all_data.append(df)
            except Exception as e:
                print(f"[数据源] {source_name} 异常: {e}")
                continue
        
        if all_data:
            print(f"[提示] 成功获取 {len(all_data)} 个数据源: {', '.join(success_sources)}")
            if len(all_data) > 1:
                combined = pd.concat(all_data, ignore_index=True, sort=False)
                name_col = None
                for col in ['name', '板块名称', '板块', '行业']:
                    if col in combined.columns:
                        name_col = col
                        break
                if name_col:
                    combined = combined.drop_duplicates(subset=[name_col], keep='first')
                return combined
            return all_data[0]
        
        print("[数据源] 所有数据源获取失败")
        return None

    def get_current_source(self):
        """获取当前使用的数据源"""
        return self._current_source

    def get_available_sources(self):
        """获取所有可用数据源列表"""
        result = []
        for name, info in self._sources.items():
            result.append({
                'name': name,
                'category': info['category'],
                'priority': info['priority'],
            })
        return result
