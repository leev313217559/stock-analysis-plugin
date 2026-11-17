# 工具关键词清单（生成文件）

> 此文件由 `node scripts/export-tool-keywords.mjs` 从 `dsh/index.ts` 生成，**不是源数据**。
> 关键词的唯一维护点是每个工具定义中的 `keywords` 字段；不要直接编辑本文件。

共 75 个工具。

| 工具 | 关键词 |
|---|---|
| `analyze_disclosure_changes` | 公告对比、财报对比、公告变更、财报差异、文本对比、披露变化、disclosure diff、filing comparison、10-K变化、同比变化、环比变化、公告前后、财报变脸、会计变更 |
| `analyze_event_study` | 事件研究、事件驱动、超额收益、事件窗口、基准比较、event study、abnormal return、CAR、事件冲击、公告后走势、业绩后表现、利好利空、窗口收益 |
| `analyze_pattern` | K线形态、技术形态、十字星、锤子线、吞没形态、启明星、黄昏星、双底、形态识别、candlestick pattern、反转形态、早晨之星、缺口、红三兵、岛形反转 |
| `analyze_portfolio_risk` | 组合风险、持仓风险、压力测试、集中度、汇率敞口、行业敞口、portfolio risk、stress test、组合回撤、行业集中、相关性、风险敞口、VaR、压力情景 |
| `analyze_position_context` | 持仓分析、持仓成本、浮盈浮亏、止损距离、止盈止损、仓位建议、position context、PnL、套牢、回本、补仓、减仓、加仓、盈亏比、成本线 |
| `analyze_trend_strategy` | 趋势策略、月度轮动、右侧交易、趋势跟踪、动量策略、trend strategy、momentum、趋势股、月线、动量、持有、退出、右侧 |
| `backtest_rotation_allocation` | 行业轮动回测、配权回测、轮动配权、等权比较、rotation backtest、allocation backtest、行业轮动、资金分配、等权配置、轮动策略、配权 |
| `build_watchlist_context` | 自选股上下文、自选股日报、批量摘要、watchlist context、next tools、自选股摘要、盘前、盘后、批量自选 |
| `calculate_dcf_valuation` | DCF、现金流折现、内在价值、FCFF、WACC、永续增长、企业价值、股权价值、discounted cash flow、intrinsic value |
| `calculate_ma` | 均线、MA、金叉、死叉、均线排列、偏离度、5日均线、20日均线、moving average、5日线、10日线、20日线、60日线、120日线、250日线、年线、半年线、季线 |
| `calculate_position_size` | 仓位计算、头寸规模、买入数量、风险预算、止损仓位、position sizing、position size、买多少、资金管理、整手、仓位控制、风险敞口 |
| `calculate_rotation_metrics` | 轮动指标、集中度、配权、历史成交计数、MC dropout、rotation metrics、轮动、样本、历史成交 |
| `check_alert_rules` | 告警规则、预警、价格提醒、条件单、涨跌幅告警、alert rules、price alert、提醒、价格到、跌破、涨到、条件触发 |
| `check_trading_day` | 交易日、休市、节假日、今天开市吗、trading day、holiday、今天交易吗、周末、调休 |
| `compare_analysis_snapshots` | 快照比较、分析对比、新旧对比、差异、snapshot diff、compare snapshots、变化、分析结果对比、回归 |
| `compare_stocks` | 同行比较、股票对比、估值对比、财务对比、peer comparison、compare stocks、竞品、谁更好、哪个好、横评、对比 |
| `detect_anomaly` | 异动、异常检测、放量异动、涨跌停异动、突破、技术异动、anomaly、unusual move、放量、缩量、超买、超卖、资金异动 |
| `detect_market_regime` | 市场状态、大盘趋势、震荡、高波动、市场阶段、regime、market trend、牛市、熊市、择时、仓位建议、市场温度 |
| `diagnose_data_sources` | 数据源诊断、数据源排查、provider、缺数据、接口报错、diagnose、data source、报错、token、配置、接口、环境、检查 |
| `evaluate_signal` | 信号胜率、技术信号、历史准确率、信号评估、signal accuracy、backtest signal、胜率、历史表现、金叉、死叉、突破 |
| `evaluate_signals` | 评估信号、到期信号、目标价命中、止损命中、signal evaluation、target hit、目标价、止损、收益、复盘、胜率 |
| `extract_article` | 正文提取、文章提取、PDF提取、公告全文、网页正文、extract article、full text、全文、研报、网页、链接 |
| `get_announcements` | 公告、披露、巨潮、SEC公告、8-K、10-K、年报、季报、filing、announcement、最新公告、公告查询、巨潮资讯、财报公告、业绩公告、港股公告、HKEX |
| `get_capital_flow` | 资金流、主力资金、超大单、大单、净流入、板块资金流、capital flow、money flow、资金流向、主力动向、抢筹、出逃、大单净额、资金进出、净卖出、smart money |
| `get_cds_index` | CDS、信用风险、信用利差、CDX、iTraxx、信用违约互换、credit spread、credit risk、民企CDS、高等级CDS |
| `get_chip_distribution` | 筹码、筹码分布、成本分布、获利比例、成本集中度、chip distribution、获利盘、套牢盘、筹码峰、成本线、筹码集中度 |
| `get_dividends` | 分红、股息、除息、派息、股息率、dividend、dividend yield、除权除息、分红记录、连续分红、派息率、分红方案、除息日、股息政策 |
| `get_dragon_tiger` | 龙虎榜、上榜、净买额、游资、dragon tiger、top list、席位、营业部、净买入、打板、龙虎榜数据、上榜原因、资金席位、游资动向 |
| `get_earnings_calendar` | 财报日历、业绩披露、预约披露、财报日期、业绩预告、earnings calendar、业绩快报、披露时间、财报季、业绩发布、财报披露日、业绩说明会 |
| `get_etf_details` | ETF、ETF详情、折溢价、规模、PCF、申赎篮子、跟踪误差、ETF holdings、ETF基金、净值、成分股、规模变动、跟踪指数 |
| `get_financials` | 财务、财报、营收、净利润、现金流、ROE、毛利率、financials、income statement、balance sheet、利润表、资产负债表、业绩、增速、净利率、财报解读、DCF输入、DCF、自由现金流 |
| `get_fund_quote` | 场外基金、基金净值、公募基金、NAV、基金代码、fund quote、mutual fund、估算净值、累计净值、开放式基金、场外公募 |
| `get_fundamental_context` | 基本面、估值、PE、PB、市值、ROE、成长性、分红、fundamentals、valuation、公司质地、盈利能力、股息率、估值水平 |
| `get_hot_stocks` | 人气榜、热搜、热门股、关注度、hot stocks、popular stocks、讨论热度、散户、龙头、热门榜、人气排名 |
| `get_index_valuation` | 指数估值、指数PE、指数PB、估值分位、沪深300估值、中证指数、index valuation、估值百分位、历史分位、中证500、创业板指、上证50 |
| `get_insider_trades` | 内部人、高管交易、增减持、Form 4、insider trades、insider buying、持股变动、13D、13G、高管增持、内部人买卖 |
| `get_kline` | K线、日K、周K、月K、历史价格、OHLCV、kline、candlestick、历史行情、蜡烛图、前复权、后复权、日线、周线、月线 |
| `get_limit_up_pool` | 涨停、涨停池、连板、封板、炸板、涨停复盘、limit up、limit-up pool、涨停板、首板、二板、打板、封单、晋级、龙头、涨停原因、连板高度 |
| `get_margin_trading` | 融资融券、两融、融资余额、融券余量、margin trading、securities lending、融资买入、融券卖出、杠杆资金、两融余额、融资净买入 |
| `get_market_capabilities` | 市场能力、支持工具、市场边界、能不能用、capabilities、market support、工具支持、市场限制、能力查询、可用工具 |
| `get_market_indices` | 指数、大盘、上证指数、深证成指、创业板指、恒生指数、纳斯达克、标普500、market indices、大盘指数、恒指、纳指、道指、日经、KOSPI、台股加权 |
| `get_market_review` | 大盘复盘、复盘、市场总结、市场温度、策略建议、market review、daily review、收评、复盘报告、明日策略、赚钱效应、情绪周期 |
| `get_market_stats` | 涨跌家数、涨停跌停、市场宽度、成交额、市场情绪、market stats、market breadth、赚钱效应、市场温度、跌停家数、涨停家数、涨跌分布、市场热度、涨停数、跌停数、港股宽度、美股宽度 |
| `get_news` | 新闻、快讯、个股新闻、财经新闻、news、headlines、最新消息、资讯、个股资讯、公告新闻、财经快讯、新闻速递、最新报道、个股消息 |
| `get_northbound_flow` | 北向资金、沪股通、深股通、外资流入、northbound、foreign flow、陆股通、北向净流入、外资持股 |
| `get_quote` | 行情、报价、现价、涨跌幅、实时价格、盘口、quote、price、股价、最新价、实时行情、五档 |
| `get_review_history` | 复盘历史、归档、历史复盘、纵向对比、review history、复盘记录、归档记录、复盘归档 |
| `get_sector_constituents` | 板块成分、成分股、板块股票、行业成分、sector constituents、constituents、板块有哪些股票、行业成分股、概念股、成分股列表、板块个股、概念成分、行业个股 |
| `get_sector_rankings` | 板块排行、行业涨幅、概念板块、领涨板块、板块轮动、sector ranking、sector performance、热点板块、概念排行、板块强度、板块涨跌、行业排名、概念板块排行、美股行业、SPDR、行业ETF |
| `get_shareholder_structure` | 股东、十大股东、股东户数、股权结构、北向持股、shareholder、ownership、大股东、机构持股、股东变化 |
| `get_signal_summary` | 信号汇总、胜率统计、信号统计、交易信号、signal summary、win rate、平均收益、复盘 |
| `get_social_sentiment` | 情绪、舆情、股吧、雪球、Reddit、散户情绪、social sentiment、sentiment、讨论热度、社交情绪、舆情热度 |
| `get_stock_info` | 股票信息、公司简介、行业分类、上市日期、总股本、stock info、company profile、公司资料、主营业务、所属行业、上市时间 |
| `get_technical_analysis` | 技术分析、技术指标、MACD、RSI、KDJ、BOLL、金叉、死叉、超买超卖、买卖信号、支撑压力、technical analysis、技术面、支撑位、压力位、买卖点 |
| `get_trading_days` | 交易日列表、未来交易日、交易日历、trading days、calendar、休市日、节假日、交易日查询 |
| `get_trading_phase` | 交易时段、盘前、盘中、盘后、午间休市、trading session、market phase、开市、午休、交易中、盘前盘后 |
| `get_trending_sentiment` | 热门趋势、社交热度、热门股、trending、social buzz、趋势榜、讨论榜、热点 |
| `get_us_holdings` | 13F、机构持仓、基金持仓、持仓变动、institutional holdings、13F filings、13F文件、机构持股、持仓变化 |
| `get_valuation_history` | 估值历史、历史PE、历史PB、估值分位、PE-TTM、valuation history、估值区间、历史分位、百分位、估值百分位、历史估值分位、PE历史、PB历史、美股估值 |
| `get_volume_analysis` | 量价、成交量、放量、缩量、量价关系、volume analysis、volume、量能、量价背离、放量上涨、缩量回调 |
| `get_watchlist` | 自选股、自选列表、watchlist、我的自选、自选池、自选股列表、自选行情、自选管理 |
| `parse_stock_list` | 解析股票列表、文本导入、CSV导入、自选股导入、parse stocks、symbol list、股票列表、文本解析、CSV、批量导入 |
| `plan_portfolio_rebalance` | 调仓、再平衡、目标权重、买卖清单、rebalance、portfolio rebalance、目标仓位、仓位调整、调仓计划 |
| `record_signal` | 记录信号、交易建议、买入信号、卖出信号、record signal、交易计划、记录建议、信号记录 |
| `render_market_report` | 复盘报告、报告渲染、Markdown、market report、render report、复盘模板、报告模板、Markdown报告 |
| `render_stock_report` | 股票报告、报告渲染、Markdown、stock report、render report、股票模板、报告模板、Markdown报告 |
| `resolve_stock_name` | 股票名称、代码解析、中文名查代码、拼音、ticker、name resolver、symbol lookup、查股票代码、拼音查股票、股票代码查询 |
| `resolve_stock_sectors` | 个股板块、所属行业、概念板块、板块查询、sector lookup、板块归属、个股概念、行业分类 |
| `run_backtest` | 回测、策略回测、YAML策略、收益回撤、backtest、strategy backtest、历史模拟、收益率、回撤、胜率 |
| `run_watchlist_analysis` | 自选股批量分析、批量分析、watchlist analysis、自选股分析、批量跑自选、自选股日报、全部自选、自选股批量 |
| `screen_risk` | 风险筛查、排雷、减持、解禁、商誉、质押、risk screening、red flags、踩雷、立案、问询、退市、风险股、财务造假、违规、诉讼 |
| `screen_stocks` | 选股、股票筛选、多因子、条件选股、PE筛选、市值筛选、stock screener、screen、股票池、换手率、涨幅筛选、低估值 |
| `search_comprehensive_intel` | 综合情报、深度调研、研报、全网搜索、六维情报、research、due diligence、个股研究、基本面研究、公告新闻、行业研究、深度研究、全网情报、公告研报 |
| `search_stock_news` | 新闻搜索、主题搜索、关键词搜索、Tavily、news search、web search、最新消息、资讯搜索、全网新闻、关键词新闻、新闻检索、资讯检索、主题新闻 |
| `validate_backtest` | 回测验证、稳健性、过拟合、滚动验证、walk-forward、backtest validation、参数稳健、走查、样本外、回测审计 |
