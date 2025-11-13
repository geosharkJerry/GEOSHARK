"""
风险评估模型测试用例
"""

import pytest
from backend.models.risk import (
    RiskAssessmentEngine,
    CreditScoreFactors,
    CreditRating
)


class TestRiskAssessment:
    """风险评估测试类"""
    
    def test_credit_score_calculation(self):
        """测试信用评分计算"""
        factors = CreditScoreFactors(
            payment_history=80.0,
            debt_ratio=70.0,
            credit_age=75.0,
            credit_mix=80.0,
            new_credit=85.0
        )
        
        engine = RiskAssessmentEngine()
        score = engine.calculate_credit_score(factors)
        
        assert 0 <= score <= 1000
        # 所有因子都较好，应该得到较高分数
        assert score >= 700
    
    def test_risk_level_mapping(self):
        """测试风险等级映射"""
        engine = RiskAssessmentEngine()
        
        assert engine.get_risk_level(900) == 'A'
        assert engine.get_risk_level(700) == 'B'
        assert engine.get_risk_level(550) == 'C'
        assert engine.get_risk_level(400) == 'D'
        assert engine.get_risk_level(200) == 'E'
    
    def test_credit_rating_mapping(self):
        """测试信用评级映射"""
        engine = RiskAssessmentEngine()
        
        assert engine.get_credit_rating(950) == CreditRating.AAA
        assert engine.get_credit_rating(820) == CreditRating.A
        assert engine.get_credit_rating(720) == CreditRating.BBB
        assert engine.get_credit_rating(620) == CreditRating.B
        assert engine.get_credit_rating(200) == CreditRating.D
    
    def test_probability_of_default(self):
        """测试违约概率计算"""
        engine = RiskAssessmentEngine()
        
        # 高信用评分应该有低违约概率
        high_score_pd = engine.calculate_pd(credit_score=850, overdue_days=0)
        assert 0 <= high_score_pd < 0.1
        
        # 低信用评分应该有高违约概率
        low_score_pd = engine.calculate_pd(credit_score=300, overdue_days=0)
        assert low_score_pd > 0.3
        
        # 逾期应该增加违约概率
        overdue_pd = engine.calculate_pd(credit_score=700, overdue_days=180)
        no_overdue_pd = engine.calculate_pd(credit_score=700, overdue_days=0)
        assert overdue_pd > no_overdue_pd
    
    def test_loss_given_default(self):
        """测试违约损失率计算"""
        engine = RiskAssessmentEngine()
        
        # 有足够抵押物的情况
        lgd_with_collateral = engine.calculate_lgd(
            collateral_value=5000000,
            exposure=5000000,
            recovery_costs_ratio=0.15
        )
        assert lgd_with_collateral < 0.2
        
        # 无抵押物的情况
        lgd_no_collateral = engine.calculate_lgd(
            collateral_value=0,
            exposure=5000000,
            recovery_costs_ratio=0.15
        )
        assert lgd_no_collateral > 0.9
    
    def test_expected_loss(self):
        """测试预期损失计算"""
        engine = RiskAssessmentEngine()
        
        el = engine.calculate_expected_loss(
            pd=0.1,
            lgd=0.5,
            ead=1000000
        )
        
        assert el == 50000  # 0.1 * 0.5 * 1000000
    
    def test_comprehensive_assessment(self):
        """测试综合风险评估"""
        factors = CreditScoreFactors(
            payment_history=70.0,
            debt_ratio=60.0,
            credit_age=80.0,
            credit_mix=75.0,
            new_credit=85.0
        )
        
        engine = RiskAssessmentEngine()
        profile = engine.comprehensive_risk_assessment(
            asset_id="test_001",
            asset_type="npl",
            asset_value=5000000,
            credit_factors=factors,
            overdue_days=180,
            collateral_value=3000000,
            volatility=0.25
        )
        
        assert profile.asset_id == "test_001"
        assert profile.risk_metrics.credit_score > 0
        assert profile.risk_metrics.risk_level in ['A', 'B', 'C', 'D', 'E']
        assert 0 <= profile.risk_metrics.probability_of_default <= 1
        assert 0 <= profile.risk_metrics.loss_given_default <= 1
        assert profile.risk_metrics.expected_loss >= 0
        assert len(profile.mitigation_measures) >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
