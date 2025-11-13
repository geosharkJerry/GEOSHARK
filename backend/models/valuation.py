"""
RWA资产估值模型
支持多种估值方法：DCF、市场比较法、清算价值法、成本法等
"""

from datetime import datetime
from enum import Enum
from typing import Optional, Dict, List
from pydantic import BaseModel, Field


class ValuationMethod(str, Enum):
    """估值方法枚举"""
    DCF = "dcf"  # Discounted Cash Flow 折现现金流法
    MARKET_COMPARISON = "market_comparison"  # 市场比较法
    LIQUIDATION = "liquidation"  # 清算价值法
    COST = "cost"  # 成本法
    INCOME = "income"  # 收益法
    AI_MODEL = "ai_model"  # AI智能估值
    HYBRID = "hybrid"  # 混合估值法


class ValuationRequest(BaseModel):
    """估值请求"""
    asset_id: str = Field(..., description="资产ID")
    method: ValuationMethod = Field(..., description="估值方法")
    parameters: Dict = Field(default_factory=dict, description="估值参数")
    requester: Optional[str] = Field(None, description="请求人")


class DCFParameters(BaseModel):
    """DCF估值参数"""
    projected_cash_flows: List[float] = Field(..., description="预测现金流（按年）")
    discount_rate: float = Field(..., ge=0, le=1, description="折现率")
    terminal_growth_rate: Optional[float] = Field(0.02, description="永续增长率")
    years: int = Field(default=5, description="预测年数")


class MarketComparisonParameters(BaseModel):
    """市场比较法参数"""
    comparable_assets: List[Dict] = Field(..., description="可比资产列表")
    adjustment_factors: Dict[str, float] = Field(default_factory=dict, description="调整因子")
    market_premium: float = Field(default=0.0, description="市场溢价率")


class LiquidationParameters(BaseModel):
    """清算价值法参数"""
    forced_sale_discount: float = Field(default=0.3, ge=0, le=0.9, description="强制出售折扣率")
    liquidation_costs: float = Field(default=0.0, description="清算成本")
    estimated_time_to_sell: int = Field(default=90, description="预计出售天数")


class CostParameters(BaseModel):
    """成本法参数"""
    replacement_cost: float = Field(..., gt=0, description="重置成本")
    depreciation_rate: float = Field(default=0.0, ge=0, le=1, description="折旧率")
    age_of_asset: int = Field(default=0, description="资产年龄（年）")
    obsolescence_factor: float = Field(default=0.0, ge=0, le=1, description="过时因子")


class IncomeParameters(BaseModel):
    """收益法参数"""
    annual_income: float = Field(..., description="年收益")
    operating_expenses: float = Field(default=0.0, description="运营费用")
    capitalization_rate: float = Field(..., gt=0, description="资本化率")
    vacancy_rate: float = Field(default=0.0, ge=0, le=1, description="空置率")


class AIValuationParameters(BaseModel):
    """AI估值参数"""
    model_type: str = Field(default="random_forest", description="模型类型")
    features: Dict = Field(..., description="特征数据")
    use_comparable_data: bool = Field(default=True, description="是否使用可比数据")
    confidence_threshold: float = Field(default=0.8, description="置信度阈值")


class ValuationResult(BaseModel):
    """估值结果"""
    asset_id: str = Field(..., description="资产ID")
    method: ValuationMethod = Field(..., description="使用的估值方法")
    estimated_value: float = Field(..., description="估值结果")
    
    # 价值范围
    lower_bound: Optional[float] = Field(None, description="价值下限")
    upper_bound: Optional[float] = Field(None, description="价值上限")
    
    # 置信度和风险
    confidence_level: float = Field(..., ge=0, le=1, description="置信度")
    risk_adjustment: float = Field(default=0.0, description="风险调整")
    
    # 详细信息
    parameters_used: Dict = Field(default_factory=dict, description="使用的参数")
    breakdown: Dict = Field(default_factory=dict, description="估值细分")
    assumptions: List[str] = Field(default_factory=list, description="关键假设")
    
    # 元数据
    valuation_date: datetime = Field(default_factory=datetime.now)
    valuator: Optional[str] = Field(None, description="估值人/机构")
    next_valuation_date: Optional[datetime] = Field(None, description="下次估值日期")
    notes: Optional[str] = Field(None, description="备注说明")
    
    class Config:
        use_enum_values = True


class ValuationComparison(BaseModel):
    """多方法估值比较"""
    asset_id: str = Field(..., description="资产ID")
    valuations: List[ValuationResult] = Field(..., description="各方法估值结果")
    weighted_average: float = Field(..., description="加权平均值")
    recommended_value: float = Field(..., description="推荐估值")
    variance: float = Field(..., description="方差")
    standard_deviation: float = Field(..., description="标准差")
    comparison_date: datetime = Field(default_factory=datetime.now)


class SensitivityAnalysis(BaseModel):
    """敏感性分析"""
    asset_id: str = Field(..., description="资产ID")
    base_case_value: float = Field(..., description="基准情况估值")
    scenarios: Dict[str, Dict] = Field(..., description="情景分析")
    # 例如: {"optimistic": {"value": 1000000, "probability": 0.3}}
    key_drivers: List[Dict] = Field(..., description="关键驱动因素")
    # 例如: [{"factor": "discount_rate", "impact": -0.05, "value_change": -50000}]
    analysis_date: datetime = Field(default_factory=datetime.now)


class ValuationHistory(BaseModel):
    """估值历史记录"""
    asset_id: str = Field(..., description="资产ID")
    valuations: List[ValuationResult] = Field(default_factory=list, description="历史估值列表")
    trend: str = Field(default="stable", description="趋势：increasing/decreasing/stable")
    average_value: float = Field(..., description="平均估值")
    volatility: float = Field(..., description="波动率")


class MarketData(BaseModel):
    """市场数据"""
    asset_type: str = Field(..., description="资产类型")
    location: Optional[str] = Field(None, description="地理位置")
    average_price: float = Field(..., description="平均价格")
    median_price: float = Field(..., description="中位数价格")
    price_per_unit: Optional[float] = Field(None, description="单位价格")
    transaction_volume: int = Field(..., description="交易量")
    liquidity_score: float = Field(..., ge=0, le=1, description="流动性评分")
    market_sentiment: str = Field(..., description="市场情绪：bullish/neutral/bearish")
    data_date: datetime = Field(default_factory=datetime.now)
    source: Optional[str] = Field(None, description="数据来源")


# 示例估值结果
EXAMPLE_DCF_VALUATION = ValuationResult(
    asset_id="asset_001",
    method=ValuationMethod.DCF,
    estimated_value=8500000,
    lower_bound=7500000,
    upper_bound=9500000,
    confidence_level=0.85,
    parameters_used={
        "projected_cash_flows": [1000000, 1200000, 1400000, 1500000, 1600000],
        "discount_rate": 0.08,
        "terminal_growth_rate": 0.02
    },
    breakdown={
        "pv_cash_flows": 5200000,
        "terminal_value": 3300000,
        "total_pv": 8500000
    },
    assumptions=[
        "稳定的现金流增长",
        "市场折现率保持在8%",
        "永续增长率2%符合长期经济增长预期"
    ],
    notes="基于过去3年历史数据进行预测"
)
