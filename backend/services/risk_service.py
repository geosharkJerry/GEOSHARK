"""
风险评估服务
实现多维度风险评估：信用风险、市场风险、流动性风险、操作风险等
"""

import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

from backend.models.risk import (
    RiskLevel, RiskType, RiskScore, ComprehensiveRiskAssessment,
    CreditRiskFactors, MarketRiskFactors, LiquidityRiskFactors,
    OperationalRiskFactors, RiskAssessmentRequest,
    StressTestScenario, StressTestResult, RiskMonitoring,
    CREDIT_SCORE_WEIGHTS, get_risk_level_from_score
)
from backend.models.asset import Asset

logger = logging.getLogger(__name__)


class RiskService:
    """风险评估服务类"""
    
    def __init__(self):
        self.risk_cache: Dict[str, ComprehensiveRiskAssessment] = {}
    
    def assess_comprehensive_risk(self, asset: Asset, 
                                 request: RiskAssessmentRequest) -> ComprehensiveRiskAssessment:
        """
        综合风险评估
        
        Args:
            asset: 资产对象
            request: 风险评估请求
            
        Returns:
            ComprehensiveRiskAssessment: 综合风险评估结果
        """
        risk_scores = []
        
        # 根据请求的风险类型进行评估
        for risk_type in request.risk_types:
            if risk_type == RiskType.CREDIT:
                score = self._assess_credit_risk(asset)
            elif risk_type == RiskType.MARKET:
                score = self._assess_market_risk(asset)
            elif risk_type == RiskType.LIQUIDITY:
                score = self._assess_liquidity_risk(asset)
            elif risk_type == RiskType.OPERATIONAL:
                score = self._assess_operational_risk(asset)
            else:
                continue
            
            risk_scores.append(score)
        
        # 计算综合评分（加权平均）
        total_weight = sum(s.weight for s in risk_scores)
        if total_weight > 0:
            overall_score = int(sum(s.score * s.weight for s in risk_scores) / total_weight)
        else:
            overall_score = 500  # 默认中等风险
        
        overall_level = get_risk_level_from_score(overall_score)
        
        # 计算违约概率和损失率
        pd = self._calculate_probability_of_default(overall_score)
        lgd = self._calculate_loss_given_default(asset, overall_score)
        el = pd * lgd * asset.current_value if asset.current_value else 0
        
        # 计算VaR
        var_95 = self._calculate_var(asset, overall_score, confidence=0.95)
        var_99 = self._calculate_var(asset, overall_score, confidence=0.99)
        cvar = self._calculate_cvar(asset, overall_score)
        
        # 识别关键风险
        key_risks = self._identify_key_risks(asset, risk_scores)
        risk_drivers = self._identify_risk_drivers(asset, risk_scores)
        recommendations = self._generate_recommendations(asset, risk_scores)
        
        # 下次复审日期（根据风险等级决定）
        review_days = {
            RiskLevel.A: 365,
            RiskLevel.B: 180,
            RiskLevel.C: 90,
            RiskLevel.D: 30,
            RiskLevel.E: 7
        }
        next_review = datetime.now() + timedelta(days=review_days.get(overall_level, 90))
        
        return ComprehensiveRiskAssessment(
            asset_id=asset.id,
            overall_score=overall_score,
            overall_level=overall_level,
            risk_scores=risk_scores,
            probability_of_default=round(pd, 4),
            loss_given_default=round(lgd, 4),
            expected_loss=round(el, 2),
            value_at_risk_95=round(var_95, 2) if var_95 else None,
            value_at_risk_99=round(var_99, 2) if var_99 else None,
            conditional_var=round(cvar, 2) if cvar else None,
            key_risks=key_risks,
            risk_drivers=risk_drivers,
            recommendations=recommendations,
            next_review_date=next_review,
            assessor=request.assessor
        )
    
    def _assess_credit_risk(self, asset: Asset) -> RiskScore:
        """评估信用风险"""
        # 从资产元数据中获取信用因素
        metadata = asset.metadata
        
        # 构建信用风险因素（示例数据）
        payment_history = metadata.get("payment_history", 0.7)
        debt_ratio = metadata.get("debt_to_income_ratio", 0.5)
        credit_age = metadata.get("credit_age_months", 60)
        delinquencies = metadata.get("delinquencies", 0)
        
        # 计算信用评分 (0-1000)
        score = 1000
        
        # 还款历史影响 (35%)
        score -= (1 - payment_history) * 350
        
        # 负债比率影响 (30%)
        if debt_ratio > 0.8:
            score -= 300
        elif debt_ratio > 0.5:
            score -= 150
        elif debt_ratio > 0.3:
            score -= 50
        
        # 信用历史长度影响 (15%)
        if credit_age < 12:
            score -= 150
        elif credit_age < 36:
            score -= 75
        elif credit_age < 60:
            score -= 30
        
        # 违约记录影响 (20%)
        score -= delinquencies * 100
        
        # 确保分数在有效范围内
        score = max(0, min(1000, int(score)))
        
        level = get_risk_level_from_score(score)
        
        # 缓释策略
        mitigation_strategies = []
        if score < 650:
            mitigation_strategies.extend([
                "增加抵押物覆盖率",
                "购买信用保险",
                "设置更严格的贷款条件"
            ])
        
        return RiskScore(
            risk_type=RiskType.CREDIT,
            score=score,
            level=level,
            weight=0.4,  # 信用风险权重40%
            factors={
                "payment_history": payment_history,
                "debt_ratio": debt_ratio,
                "credit_age_months": credit_age,
                "delinquencies": delinquencies
            },
            mitigation_strategies=mitigation_strategies
        )
    
    def _assess_market_risk(self, asset: Asset) -> RiskScore:
        """评估市场风险"""
        metadata = asset.metadata
        
        # 市场风险因素
        volatility = metadata.get("price_volatility", 0.15)
        liquidity = metadata.get("market_liquidity", 0.7)
        correlation = metadata.get("market_correlation", 0.5)
        
        # 计算市场风险评分
        score = 800  # 基准分数
        
        # 波动性影响
        score -= volatility * 500
        
        # 流动性影响
        score -= (1 - liquidity) * 300
        
        # 市场相关性影响（高相关性=高系统性风险）
        score -= abs(correlation) * 100
        
        score = max(0, min(1000, int(score)))
        level = get_risk_level_from_score(score)
        
        mitigation_strategies = []
        if volatility > 0.3:
            mitigation_strategies.append("使用期权对冲价格波动")
        if liquidity < 0.5:
            mitigation_strategies.append("建立流动性储备")
        
        return RiskScore(
            risk_type=RiskType.MARKET,
            score=score,
            level=level,
            weight=0.3,  # 市场风险权重30%
            factors={
                "volatility": volatility,
                "liquidity": liquidity,
                "correlation": correlation
            },
            mitigation_strategies=mitigation_strategies
        )
    
    def _assess_liquidity_risk(self, asset: Asset) -> RiskScore:
        """评估流动性风险"""
        metadata = asset.metadata
        
        # 流动性因素
        time_to_liquidate = metadata.get("time_to_liquidate_days", 60)
        market_depth = metadata.get("market_depth", 0.6)
        forced_sale_discount = metadata.get("forced_sale_discount", 0.2)
        
        # 计算流动性风险评分
        score = 900
        
        # 清算时间影响
        if time_to_liquidate > 180:
            score -= 300
        elif time_to_liquidate > 90:
            score -= 150
        elif time_to_liquidate > 30:
            score -= 50
        
        # 市场深度影响
        score -= (1 - market_depth) * 200
        
        # 强制出售折扣影响
        score -= forced_sale_discount * 300
        
        score = max(0, min(1000, int(score)))
        level = get_risk_level_from_score(score)
        
        mitigation_strategies = []
        if time_to_liquidate > 90:
            mitigation_strategies.append("寻找多个潜在买家")
        if forced_sale_discount > 0.3:
            mitigation_strategies.append("改善资产质量以减少折价")
        
        return RiskScore(
            risk_type=RiskType.LIQUIDITY,
            score=score,
            level=level,
            weight=0.2,  # 流动性风险权重20%
            factors={
                "time_to_liquidate_days": time_to_liquidate,
                "market_depth": market_depth,
                "forced_sale_discount": forced_sale_discount
            },
            mitigation_strategies=mitigation_strategies
        )
    
    def _assess_operational_risk(self, asset: Asset) -> RiskScore:
        """评估操作风险"""
        metadata = asset.metadata
        
        # 操作风险因素
        management_quality = metadata.get("management_quality", 0.7)
        compliance_issues = metadata.get("compliance_issues", 0)
        fraud_incidents = metadata.get("fraud_incidents", 0)
        
        # 计算操作风险评分
        score = 850
        
        # 管理质量影响
        score -= (1 - management_quality) * 200
        
        # 合规问题影响
        score -= compliance_issues * 100
        
        # 欺诈事件影响
        score -= fraud_incidents * 150
        
        score = max(0, min(1000, int(score)))
        level = get_risk_level_from_score(score)
        
        mitigation_strategies = []
        if management_quality < 0.6:
            mitigation_strategies.append("加强管理层培训")
        if compliance_issues > 0:
            mitigation_strategies.append("建立合规监控系统")
        
        return RiskScore(
            risk_type=RiskType.OPERATIONAL,
            score=score,
            level=level,
            weight=0.1,  # 操作风险权重10%
            factors={
                "management_quality": management_quality,
                "compliance_issues": compliance_issues,
                "fraud_incidents": fraud_incidents
            },
            mitigation_strategies=mitigation_strategies
        )
    
    def _calculate_probability_of_default(self, credit_score: int) -> float:
        """
        计算违约概率 (PD)
        基于信用评分映射到违约概率
        """
        # 违约概率映射表
        if credit_score >= 800:
            return 0.01  # 1%
        elif credit_score >= 650:
            return 0.05  # 5%
        elif credit_score >= 500:
            return 0.15  # 15%
        elif credit_score >= 350:
            return 0.35  # 35%
        else:
            return 0.60  # 60%
    
    def _calculate_loss_given_default(self, asset: Asset, credit_score: int) -> float:
        """
        计算违约损失率 (LGD)
        考虑抵押物、回收率等因素
        """
        # 基础LGD
        base_lgd = 0.45
        
        # 根据资产类型调整
        asset_type_lgd = {
            "npl": 0.60,
            "real_estate": 0.30,
            "inventory": 0.50,
            "receivables": 0.40,
            "collateral": 0.35
        }
        
        lgd = asset_type_lgd.get(asset.asset_type, base_lgd)
        
        # 根据信用评分调整
        if credit_score < 350:
            lgd += 0.15
        elif credit_score < 500:
            lgd += 0.10
        
        # 考虑抵押物
        if asset.metadata.get("has_collateral", False):
            lgd -= 0.20
        
        return max(0, min(1, lgd))
    
    def _calculate_var(self, asset: Asset, risk_score: int, 
                      confidence: float = 0.95) -> Optional[float]:
        """
        计算风险价值 (VaR)
        使用参数法计算
        """
        if not asset.current_value:
            return None
        
        # 估算波动率（基于风险评分）
        volatility = (1000 - risk_score) / 1000 * 0.5  # 0-50%
        
        # 标准正态分布分位数
        z_scores = {
            0.90: 1.28,
            0.95: 1.65,
            0.99: 2.33
        }
        
        z = z_scores.get(confidence, 1.65)
        
        # VaR = Value * Volatility * Z-score
        var = asset.current_value * volatility * z
        
        return var
    
    def _calculate_cvar(self, asset: Asset, risk_score: int) -> Optional[float]:
        """
        计算条件风险价值 (CVaR / Expected Shortfall)
        """
        var_95 = self._calculate_var(asset, risk_score, 0.95)
        
        if var_95:
            # CVaR 通常是 VaR 的 1.2-1.5 倍
            return var_95 * 1.3
        
        return None
    
    def _identify_key_risks(self, asset: Asset, 
                           risk_scores: List[RiskScore]) -> List[str]:
        """识别关键风险点"""
        key_risks = []
        
        for score in risk_scores:
            if score.level in [RiskLevel.D, RiskLevel.E]:
                risk_type_names = {
                    RiskType.CREDIT: "信用风险",
                    RiskType.MARKET: "市场风险",
                    RiskType.LIQUIDITY: "流动性风险",
                    RiskType.OPERATIONAL: "操作风险"
                }
                risk_name = risk_type_names.get(score.risk_type, str(score.risk_type))
                key_risks.append(f"{risk_name}较高（评分: {score.score}）")
        
        # 添加资产特定风险
        if asset.status == "distressed":
            key_risks.append("资产处于困境状态")
        
        if asset.metadata.get("overdue_days", 0) > 90:
            key_risks.append("长期逾期（超过90天）")
        
        return key_risks
    
    def _identify_risk_drivers(self, asset: Asset, 
                               risk_scores: List[RiskScore]) -> List[str]:
        """识别风险驱动因素"""
        drivers = []
        
        for score in risk_scores:
            factors = score.factors
            
            # 分析各因素
            if score.risk_type == RiskType.CREDIT:
                if factors.get("payment_history", 1) < 0.7:
                    drivers.append("还款历史不佳")
                if factors.get("debt_ratio", 0) > 0.6:
                    drivers.append("负债率过高")
            
            elif score.risk_type == RiskType.MARKET:
                if factors.get("volatility", 0) > 0.3:
                    drivers.append("市场波动性大")
                if factors.get("liquidity", 1) < 0.5:
                    drivers.append("市场流动性不足")
            
            elif score.risk_type == RiskType.LIQUIDITY:
                if factors.get("time_to_liquidate_days", 0) > 90:
                    drivers.append("清算周期长")
        
        return drivers
    
    def _generate_recommendations(self, asset: Asset, 
                                 risk_scores: List[RiskScore]) -> List[str]:
        """生成风险管理建议"""
        recommendations = []
        
        # 收集所有缓释策略
        for score in risk_scores:
            recommendations.extend(score.mitigation_strategies)
        
        # 添加通用建议
        if asset.risk_level in [RiskLevel.D, RiskLevel.E]:
            recommendations.extend([
                "定期监控资产状态",
                "考虑提前处置或重组",
                "增加风险准备金"
            ])
        
        # 去重
        recommendations = list(set(recommendations))
        
        return recommendations[:10]  # 最多返回10条建议
    
    def stress_test(self, asset: Asset, 
                   scenarios: List[StressTestScenario]) -> StressTestResult:
        """
        压力测试
        
        Args:
            asset: 资产对象
            scenarios: 压力测试场景列表
            
        Returns:
            StressTestResult: 压力测试结果
        """
        if not asset.current_value:
            raise ValueError("Asset must have a current value for stress testing")
        
        worst_case_value = asset.current_value
        worst_case_score = 1000
        
        # 执行各场景测试
        for scenario in scenarios:
            # 计算场景影响
            impact_value = asset.current_value + scenario.impact_on_value
            impact_score = 1000 + scenario.impact_on_risk_score
            
            # 更新最坏情况
            if impact_value < worst_case_value:
                worst_case_value = impact_value
            if impact_score < worst_case_score:
                worst_case_score = impact_score
        
        # 计算抗压能力评分
        value_resilience = worst_case_value / asset.current_value
        score_resilience = worst_case_score / 1000
        resilience_score = (value_resilience + score_resilience) / 2
        
        return StressTestResult(
            asset_id=asset.id,
            scenarios=scenarios,
            worst_case_value=round(worst_case_value, 2),
            worst_case_score=max(0, worst_case_score),
            resilience_score=round(resilience_score, 3)
        )
    
    def create_risk_monitoring(self, asset: Asset, 
                              risk_assessment: ComprehensiveRiskAssessment) -> RiskMonitoring:
        """
        创建风险监控
        
        Args:
            asset: 资产对象
            risk_assessment: 风险评估结果
            
        Returns:
            RiskMonitoring: 风险监控配置
        """
        # 根据风险等级确定监控频率
        frequency_map = {
            RiskLevel.A: "monthly",
            RiskLevel.B: "monthly",
            RiskLevel.C: "weekly",
            RiskLevel.D: "daily",
            RiskLevel.E: "daily"
        }
        
        frequency = frequency_map.get(risk_assessment.overall_level, "weekly")
        
        # 设置预警阈值
        alert_thresholds = {
            "credit_score": 500,
            "probability_of_default": 0.3,
            "value_at_risk": asset.current_value * 0.2 if asset.current_value else 0,
            "overdue_days": 60
        }
        
        # 检查当前预警
        current_alerts = []
        if risk_assessment.overall_score < alert_thresholds["credit_score"]:
            current_alerts.append("信用评分低于阈值")
        if risk_assessment.probability_of_default > alert_thresholds["probability_of_default"]:
            current_alerts.append("违约概率过高")
        
        # 确定风险趋势（简化版本）
        trend = "stable"
        if risk_assessment.overall_level in [RiskLevel.D, RiskLevel.E]:
            trend = "deteriorating"
        elif risk_assessment.overall_level == RiskLevel.A:
            trend = "improving"
        
        return RiskMonitoring(
            asset_id=asset.id,
            monitoring_frequency=frequency,
            alert_thresholds=alert_thresholds,
            current_alerts=current_alerts,
            trend=trend
        )


# 创建全局服务实例
risk_service = RiskService()
