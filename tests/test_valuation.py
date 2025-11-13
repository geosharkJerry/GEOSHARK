"""
估值模型测试用例
"""

import pytest
from backend.models.valuation import (
    AssetValuationEngine,
    DCFParameters,
    LiquidationParameters,
    IncomeParameters,
    ValuationMethod
)


class TestValuationEngine:
    """估值引擎测试类"""
    
    def test_dcf_valuation(self):
        """测试DCF估值"""
        params = DCFParameters(
            projected_cash_flows=[100000, 120000, 150000, 180000, 200000],
            discount_rate=0.08,
            terminal_growth_rate=0.02
        )
        
        engine = AssetValuationEngine()
        result = engine.dcf_valuation(params)
        
        assert result.method == ValuationMethod.DCF
        assert result.estimated_value > 0
        assert 0 < result.confidence_level <= 1
        assert result.value_range[0] < result.value_range[1]
        assert result.breakdown is not None
    
    def test_liquidation_valuation(self):
        """测试清算价值法估值"""
        params = LiquidationParameters(
            asset_book_value=5000000,
            liquidation_type="orderly",
            discount_rate=0.3,
            time_to_liquidate=6,
            liquidation_costs=100000
        )
        
        engine = AssetValuationEngine()
        result = engine.liquidation_valuation(params)
        
        assert result.method == ValuationMethod.LIQUIDATION
        assert result.estimated_value > 0
        assert result.estimated_value < params.asset_book_value
    
    def test_income_valuation(self):
        """测试收益法估值"""
        params = IncomeParameters(
            annual_income=1000000,
            capitalization_rate=0.08,
            vacancy_rate=0.1,
            operating_expenses_ratio=0.3
        )
        
        engine = AssetValuationEngine()
        result = engine.income_valuation(params)
        
        assert result.method == ValuationMethod.INCOME
        assert result.estimated_value > 0
        assert result.breakdown is not None
    
    def test_forced_liquidation_higher_discount(self):
        """测试强制清算折扣率更高"""
        orderly_params = LiquidationParameters(
            asset_book_value=5000000,
            liquidation_type="orderly",
            discount_rate=0.3,
            time_to_liquidate=6,
            liquidation_costs=0
        )
        
        forced_params = LiquidationParameters(
            asset_book_value=5000000,
            liquidation_type="forced",
            discount_rate=0.3,
            time_to_liquidate=6,
            liquidation_costs=0
        )
        
        engine = AssetValuationEngine()
        orderly_result = engine.liquidation_valuation(orderly_params)
        forced_result = engine.liquidation_valuation(forced_params)
        
        # 强制清算价值应该低于有序清算
        assert forced_result.estimated_value < orderly_result.estimated_value
    
    def test_dcf_with_negative_cashflows(self):
        """测试DCF处理负现金流"""
        params = DCFParameters(
            projected_cash_flows=[-50000, 100000, 150000],
            discount_rate=0.08,
            terminal_growth_rate=0.02
        )
        
        engine = AssetValuationEngine()
        result = engine.dcf_valuation(params)
        
        # 应该能够处理负现金流
        assert result.estimated_value is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
