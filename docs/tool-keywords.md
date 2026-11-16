# 工具关键词清单（生成文件）

> 此文件由 `node scripts/export-tool-keywords.mjs` 从 `dsh/index.ts` 生成，**不是源数据**。
> 关键词的唯一维护点是每个工具定义中的 `keywords` 字段；不要直接编辑本文件。

共 73 个工具。

| 工具 | 关键词 |
|---|---|
| `analyze_disclosure_changes` | 公告对比、财报对比、公告变更、财报差异、文本对比、披露变化、disclosure diff、filing comparison、10-K变化 |
| `analyze_event_study` | 事件研究、事件驱动、超额收益、事件窗口、基准比较、event study、abnormal return、CAR |
| `analyze_pattern` | K线形态、技术形态、十字星、锤子线、吞没形态、启明星、黄昏星、双底、形态识别、candlestick pattern |
| `analyze_portfolio_risk` | 组合风险、持仓风险、压力测试、集中度、汇率敞口、行业敞口、portfolio risk、stress test |
| `analyze_position_context` | 持仓分析、持仓成本、浮盈浮亏、止损距离、止盈止损、仓位建议、position context、PnL |
| `analyze_trend_strategy` | 趋势策略、月度轮动、右侧交易、趋势跟踪、动量策略、trend strategy、momentum |
| `backtest_rotation_allocation` | 行业轮动回测、配权回测、轮动配权、等权比较、rotation backtest、allocation backtest |
| `build_watchlist_context` | 自选股上下文、自选股日报、批量摘要、watchlist context、next tools |
| `calculate_ma` | 均线、MA、金叉、死叉、均线排列、偏离度、5日均线、20日均线、moving average |
| `calculate_position_size` | 仓位计算、头寸规模、买入数量、风险预算、止损仓位、position sizing、position size |
| `calculate_rotation_metrics` | 轮动指标、集中度、配权、历史成交计数、MC dropout、rotation metrics |
| `check_alert_rules` | 告警规则、预警、价格提醒、条件单、涨跌幅告警、alert rules、price alert |
| `check_trading_day` | 交易日、休市、节假日、今天开市吗、trading day、holiday |
| `compare_analysis_snapshots` | 快照比较、分析对比、新旧对比、差异、snapshot diff、compare snapshots |
| `compare_stocks` | 同行比较、股票对比、估值对比、财务对比、peer comparison、compare stocks |
| `detect_anomaly` | 异动、异常检测、放量异动、涨跌停异动、突破、技术异动、anomaly、unusual move |
| `detect_market_regime` | 市场状态、大盘趋势、震荡、高波动、市场阶段、regime、market trend |
| `diagnose_data_sources` | 数据源诊断、数据源排查、provider、缺数据、接口报错、diagnose、data source |
| `evaluate_signal` | 信号胜率、技术信号、历史准确率、信号评估、signal accuracy、backtest signal |
| `evaluate_signals` | 评估信号、到期信号、目标价命中、止损命中、signal evaluation、target hit |
| `extract_article` | 正文提取、文章提取、PDF提取、公告全文、网页正文、extract article、full text |
| `get_announcements` | 公告、披露、巨潮、SEC公告、8-K、10-K、年报、季报、filing、announcement |
| `get_capital_flow` | 资金流、主力资金、超大单、大单、净流入、板块资金流、capital flow、money flow |
| `get_chip_distribution` | 筹码、筹码分布、成本分布、获利比例、成本集中度、chip distribution |
| `get_dividends` | 分红、股息、除息、派息、股息率、dividend、dividend yield |
| `get_dragon_tiger` | 龙虎榜、上榜、净买额、游资、dragon tiger、top list |
| `get_earnings_calendar` | 财报日历、业绩披露、预约披露、财报日期、业绩预告、earnings calendar |
| `get_etf_details` | ETF、ETF详情、折溢价、规模、PCF、申赎篮子、跟踪误差、ETF holdings |
| `get_financials` | 财务、财报、营收、净利润、现金流、ROE、毛利率、financials、income statement、balance sheet |
| `get_fund_quote` | 场外基金、基金净值、公募基金、NAV、基金代码、fund quote、mutual fund |
| `get_fundamental_context` | 基本面、估值、PE、PB、市值、ROE、成长性、分红、fundamentals、valuation |
| `get_hot_stocks` | 人气榜、热搜、热门股、关注度、hot stocks、popular stocks |
| `get_index_valuation` | 指数估值、指数PE、指数PB、估值分位、沪深300估值、中证指数、index valuation |
| `get_insider_trades` | 内部人、高管交易、增减持、Form 4、insider trades、insider buying |
| `get_kline` | K线、日K、周K、月K、历史价格、OHLCV、kline、candlestick |
| `get_limit_up_pool` | 涨停、涨停池、连板、封板、炸板、涨停复盘、limit up、limit-up pool |
| `get_margin_trading` | 融资融券、两融、融资余额、融券余量、margin trading、securities lending |
| `get_market_capabilities` | 市场能力、支持工具、市场边界、能不能用、capabilities、market support |
| `get_market_indices` | 指数、大盘、上证指数、深证成指、创业板指、恒生指数、纳斯达克、标普500、market indices |
| `get_market_review` | 大盘复盘、复盘、市场总结、市场温度、策略建议、market review、daily review |
| `get_market_stats` | 涨跌家数、涨停跌停、市场宽度、成交额、市场情绪、market stats、market breadth |
| `get_news` | 新闻、快讯、个股新闻、财经新闻、news、headlines |
| `get_northbound_flow` | 北向资金、沪股通、深股通、外资流入、northbound、foreign flow |
| `get_quote` | 行情、报价、现价、涨跌幅、实时价格、盘口、quote、price |
| `get_review_history` | 复盘历史、归档、历史复盘、纵向对比、review history |
| `get_sector_constituents` | 板块成分、成分股、板块股票、行业成分、sector constituents、constituents |
| `get_sector_rankings` | 板块排行、行业涨幅、概念板块、领涨板块、板块轮动、sector ranking、sector performance |
| `get_shareholder_structure` | 股东、十大股东、股东户数、股权结构、北向持股、shareholder、ownership |
| `get_signal_summary` | 信号汇总、胜率统计、信号统计、交易信号、signal summary、win rate |
| `get_social_sentiment` | 情绪、舆情、股吧、雪球、Reddit、散户情绪、social sentiment、sentiment |
| `get_stock_info` | 股票信息、公司简介、行业分类、上市日期、总股本、stock info、company profile |
| `get_technical_analysis` | 技术分析、技术指标、MACD、RSI、KDJ、BOLL、买卖信号、支撑压力、technical analysis |
| `get_trading_days` | 交易日列表、未来交易日、交易日历、trading days、calendar |
| `get_trading_phase` | 交易时段、盘前、盘中、盘后、午间休市、trading session、market phase |
| `get_trending_sentiment` | 热门趋势、社交热度、热门股、trending、social buzz |
| `get_us_holdings` | 13F、机构持仓、基金持仓、持仓变动、institutional holdings、13F filings |
| `get_valuation_history` | 估值历史、历史PE、历史PB、估值分位、PE-TTM、valuation history |
| `get_volume_analysis` | 量价、成交量、放量、缩量、量价关系、volume analysis、volume |
| `get_watchlist` | 自选股、自选列表、watchlist |
| `parse_stock_list` | 解析股票列表、文本导入、CSV导入、自选股导入、parse stocks、symbol list |
| `plan_portfolio_rebalance` | 调仓、再平衡、目标权重、买卖清单、rebalance、portfolio rebalance |
| `record_signal` | 记录信号、交易建议、买入信号、卖出信号、record signal |
| `render_market_report` | 复盘报告、报告渲染、Markdown、market report、render report |
| `render_stock_report` | 股票报告、报告渲染、Markdown、stock report、render report |
| `resolve_stock_name` | 股票名称、代码解析、中文名查代码、拼音、ticker、name resolver、symbol lookup |
| `resolve_stock_sectors` | 个股板块、所属行业、概念板块、板块查询、sector lookup |
| `run_backtest` | 回测、策略回测、YAML策略、收益回撤、backtest、strategy backtest |
| `run_watchlist_analysis` | 自选股批量分析、批量分析、watchlist analysis |
| `screen_risk` | 风险筛查、排雷、减持、解禁、商誉、质押、risk screening、red flags |
| `screen_stocks` | 选股、股票筛选、多因子、条件选股、PE筛选、市值筛选、stock screener、screen |
| `search_comprehensive_intel` | 综合情报、深度调研、研报、全网搜索、六维情报、research、due diligence |
| `search_stock_news` | 新闻搜索、主题搜索、关键词搜索、Tavily、news search、web search |
| `validate_backtest` | 回测验证、稳健性、过拟合、滚动验证、walk-forward、backtest validation |
