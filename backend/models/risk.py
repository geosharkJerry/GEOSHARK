"""
RWA资产风险评估模型
包含信用风险、市场风险、流动性风险、操作风险等多维度评估
"""

from datetime import datetime
from enum import Enum
from typing import Optional, Dict, List
from pydantic import BaseModel, Field


class RiskLevel(str, Enum):
    """风险等级"""
    A = "A"  # 低风险 (800-1000分)
    B = "B"  # 较低风险 (650-799分)
    C = "C"  # 中等风险 (500-649分)
    D = "D"  # 较高风险 (350-499分)
    E = "E"  # 高风险 (0-349分)


class RiskType(str, Enum):
    """风险类型"""
    CREDIT = "credit"  # 信用风险
    MARKET = "market"  # 市场风险
    LIQUIDITY = "liquidity"  # 流动性风险
    OPERATIONAL = "operational"  # 操作风险
    LEGAL = "legal"  # 法律风险
    ENVIRONMENTAL = "environmental"  # 环境风险
    POLITICAL = "political"  # 政治风险


class CreditRiskFactors(BaseModel):
    """信用风险因素"""
    payment_history: float = Field(..., ge=0, le=1, description="还款历史评分 (0-1)")
    debt_to_income_ratio: float = Field(..., ge=0, description="负债收入比")
    credit_utilization: float = Field(..., ge=0, le=1, description="信用使用率")
    credit_age: int = Field(..., ge=0, description="信用历史长度（月）")
    recent_inquiries: int = Field(default=0, description="近期查询次数")
    delinquencies: int = Field(default=0, description="违约次数")
    bankruptcies: int = Field(default=0, description="破产次数")
    
    # 企业特有
    debt_service_coverage_ratio: Optional[float] = Field(None, description="偿债覆盖率")
    current_ratio: Optional[float] = Field(None, description="流动比率")
    quick_ratio: Optional[float] = Field(None, description="速动比率")


class MarketRiskFactors(BaseModel):
    """市场风险因素"""
    price_volatility: float = Field(..., ge=0, description="价格波动率")
    market_liquidity: float = Field(..., ge=0, le=1, description="市场流动性")
    correlation_with_market: float = Field(..., ge=-1, le=1, description="与市场相关性")
    interest_rate_sensitivity: float = Field(..., description="利率敏感度")
    currency_exposure: float = Field(default=0.0, description="汇率风险敞口")
    sector_concentration: float = Field(..., ge=0, le=1, description="行业集中度")


class LiquidityRiskFactors(BaseModel):
    """流动性风险因素"""
    time_to_liquidate: int = Field(..., gt=0, description="预计清算天数")
    bid_ask_spread: float = Field(..., ge=0, description="买卖价差")
    market_depth: float = Field(..., ge=0, le=1, description="市场深度")
    forced_sale_discount: float = Field(..., ge=0, le=1, description="强制出售折扣")
    seasonal_factors: Optional[Dict] = Field(None, description="季节性因素")


class OperationalRiskFactors(BaseModel):
    """操作风险因素"""
    management_quality: float = Field(..., ge=0, le=1, description="管理质量评分")
    system_reliability: float = Field(..., ge=0, le=1, description="系统可靠性")
    fraud_incidents: int = Field(default=0, description="欺诈事件数")
    compliance_issues: int = Field(default=0, description="合规问题数")
    process_failures: int = Field(default=0, description="流程失败次数")
    employee_turnover: float = Field(default=0.0, ge=0, le=1, description="员工流失率")


class RiskAssessmentRequest(BaseModel):
    """风险评估请求"""
    asset_id: str = Field(..., description="资产ID")
    risk_types: List[RiskType] = Field(..., description="评估的风险类型")
    assessment_date: datetime = Field(default_factory=datetime.now)
    assessor: Optional[str] = Field(None, description="评估人")


class RiskScore(BaseModel):
    """单项风险评分"""
    risk_type: RiskType = Field(..., description="风险类型")
    score: int = Field(..., ge=0, le=1000, description="风险评分 (0-1000)")
    level: RiskLevel = Field(..., description="风险等级")
    weight: float = Field(default=1.0, ge=0, le=1, description="权重")
    factors: Dict = Field(default_factory=dict, description="风险因素详情")
    mitigation_strategies: List[str] = Field(default_factory=list, description="风险缓释策略")


class ComprehensiveRiskAssessment(BaseModel):
    """综合风险评估"""
    asset_id: str = Field(..., description="资产ID")
    
    # 综合评分
    overall_score: int = Field(..., ge=0, le=1000, description="综合风险评分")
    overall_level: RiskLevel = Field(..., description="综合风险等级")
    
    # 各项风险评分
    risk_scores: List[RiskScore] = Field(..., description="各类风险评分")
    
    # 违约相关
    probability_of_default: float = Field(..., ge=0, le=1, description="违约概率 PD")
    loss_given_default: float = Field(..., ge=0, le=1, description="违约损失率 LGD")
    expected_loss: float = Field(..., description="预期损失 EL")
    
    # 风险价值
    value_at_risk_95: Optional[float] = Field(None, description="95%置信度VaR")
    value_at_risk_99: Optional[float] = Field(None, description="99%置信度VaR")
    conditional_var: Optional[float] = Field(None, description="条件风险价值CVaR")
    
    # 评估详情
    key_risks: List[str] = Field(default_factory=list, description="关键风险点")
    risk_drivers: List[str] = Field(default_factory=list, description="风险驱动因素")
    recommendations: List[str] = Field(default_factory=list, description="风险管理建议")
    
    # 元数据
    assessment_date: datetime = Field(default_factory=datetime.now)
    next_review_date: Optional[datetime] = Field(None, description="下次复审日期")
    assessor: Optional[str] = Field(None, description="评估人/机构")
    methodology: str = Field(default="综合评分法", description="评估方法")
    
    class Config:
        use_enum_values = True


class StressTestScenario(BaseModel):
    """压力测试场景"""
    scenario_name: str = Field(..., description="场景名称")
    description: str = Field(..., description="场景描述")
    probability: float = Field(..., ge=0, le=1, description="发生概率")
    
    # 场景参数
    market_shock: Optional[float] = Field(None, description="市场冲击幅度")
    interest_rate_change: Optional[float] = Field(None, description="利率变化")
    credit_downgrade: Optional[int] = Field(None, description="信用评级下调级数")
    liquidity_crisis: Optional[bool] = Field(None, description="流动性危机")
    
    # 影响评估
    impact_on_value: float = Field(..., description="对价值的影响")
    impact_on_risk_score: int = Field(..., description="对风险评分的影响")
    recovery_time: int = Field(..., description="恢复时间（天）")


class StressTestResult(BaseModel):
    """压力测试结果"""
    asset_id: str = Field(..., description="资产ID")
    scenarios: List[StressTestScenario] = Field(..., description="测试场景列表")
    worst_case_value: float = Field(..., description="最坏情况价值")
    worst_case_score: int = Field(..., description="最坏情况评分")
    resilience_score: float = Field(..., ge=0, le=1, description="抗压能力评分")
    test_date: datetime = Field(default_factory=datetime.now)


class RiskMonitoring(BaseModel):
    """风险监控"""
    asset_id: str = Field(..., description="资产ID")
    monitoring_frequency: str = Field(..., description="监控频率：daily/weekly/monthly")
    alert_thresholds: Dict = Field(..., description="预警阈值")
    # 例如: {"credit_score": 500, "pd": 0.3}
    current_alerts: List[str] = Field(default_factory=list, description="当前预警")
    trend: str = Field(..., description="风险趋势：improving/stable/deteriorating")
    last_update: datetime = Field(default_factory=datetime.now)


class RiskMitigationStrategy(BaseModel):
    """风险缓释策略"""
    risk_type: RiskType = Field(..., description="风险类型")
    strategy_name: str = Field(..., description="策略名称")
    description: str = Field(..., description="策略描述")
    implementation_cost: float = Field(..., description="实施成本")
    expected_risk_reduction: float = Field(..., ge=0, le=1, description="预期风险降低幅度")
    time_to_implement: int = Field(..., description="实施周期（天）")
    effectiveness: float = Field(..., ge=0, le=1, description="有效性评分")


# 信用评分计算权重
CREDIT_SCORE_WEIGHTS = {
    "payment_history": 0.35,
    "debt_ratio": 0.30,
    "credit_age": 0.15,
    "credit_mix": 0.10,
    "new_credit": 0.10
}

# 风险等级映射
RISK_LEVEL_MAPPING = {
    "A": {"min": 800, "max": 1000, "description": "低风险，优质资产"},
    "B": {"min": 650, "max": 799, "description": "较低风险，良好资产"},
    "C": {"min": 500, "max": 649, "description": "中等风险，标准资产"},
    "D": {"min": 350, "max": 499, "description": "较高风险，次级资产"},
    "E": {"min": 0, "max": 349, "description": "高风险，不良资产"}
}


def get_risk_level_from_score(score: int) -> RiskLevel:
    """根据评分获取风险等级"""
    for level, range_info in RISK_LEVEL_MAPPING.items():
        if range_info["min"] <= score <= range_info["max"]:
            return RiskLevel(level)
    return RiskLevel.E


# 示例风险评估
EXAMPLE_RISK_ASSESSMENT = ComprehensiveRiskAssessment(
    asset_id="asset_001",
    overall_score=550,
    overall_level=RiskLevel.C,
    risk_scores=[
        RiskScore(
            risk_type=RiskType.CREDIT,
            score=520,
            level=RiskLevel.C,
            weight=0.4,
            factors={
                "payment_history": 0.7,
                "debt_to_income_ratio": 0.55,
                "delinquencies": 2
            }
        ),
        RiskScore(
            risk_type=RiskType.MARKET,
            score=600,
            level=RiskLevel.C,
            weight=0.3,
            factors={
                "price_volatility": 0.25,
                "market_liquidity": 0.65
            }
        )
    ],
    probability_of_default=0.12,
    loss_given_default=0.35,
    expected_loss=0.042,
    key_risks=[
        "信用历史中有违约记录",
        "市场波动性较高",
        "流动性一般"
    ],
    recommendations=[
        "加强抵押物管理",
        "定期监控市场变化",
        "考虑购买信用保险"
    ]
)
