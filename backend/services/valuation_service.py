"""
资产估值服务
实现多种估值方法：DCF、市场比较法、清算价值法、成本法、AI估值等
"""

import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

from backend.models.valuation import (
    ValuationRequest, ValuationResult, ValuationMethod,
    DCFParameters, MarketComparisonParameters, LiquidationParameters,
    CostParameters, IncomeParameters, AIValuationParameters,
    ValuationComparison, SensitivityAnalysis, MarketData
)
from backend.models.asset import Asset

logger = logging.getLogger(__name__)


class ValuationService:
    """估值服务类"""
    
    def __init__(self):
        self.market_data_cache: Dict[str, MarketData] = {}
    
    def estimate_value(self, asset: Asset, request: ValuationRequest) -> ValuationResult:
        """
        执行资产估值
        
        Args:
            asset: 资产对象
            request: 估值请求
            
        Returns:
            ValuationResult: 估值结果
        """
        method = request.method
        
        if method == ValuationMethod.DCF:
            return self._dcf_valuation(asset, request.parameters)
        elif method == ValuationMethod.MARKET_COMPARISON:
            return self._market_comparison_valuation(asset, request.parameters)
        elif method == ValuationMethod.LIQUIDATION:
            return self._liquidation_valuation(asset, request.parameters)
        elif method == ValuationMethod.COST:
            return self._cost_valuation(asset, request.parameters)
        elif method == ValuationMethod.INCOME:
            return self._income_valuation(asset, request.parameters)
        elif method == ValuationMethod.AI_MODEL:
            return self._ai_valuation(asset, request.parameters)
        else:
            raise ValueError(f"Unsupported valuation method: {method}")
    
    def _dcf_valuation(self, asset: Asset, params: Dict) -> ValuationResult:
        """
        DCF折现现金流估值法
        
        公式: PV = Σ(CFt / (1 + r)^t) + TV / (1 + r)^n
        其中 TV = CFn * (1 + g) / (r - g)
        """
        try:
            dcf_params = DCFParameters(**params)
            
            cash_flows = dcf_params.projected_cash_flows
            discount_rate = dcf_params.discount_rate
            terminal_growth_rate = dcf_params.terminal_growth_rate
            
            # 计算现金流现值
            pv_cash_flows = 0
            for t, cf in enumerate(cash_flows, start=1):
                pv = cf / ((1 + discount_rate) ** t)
                pv_cash_flows += pv
            
            # 计算终值 (Terminal Value)
            if terminal_growth_rate and terminal_growth_rate < discount_rate:
                last_cf = cash_flows[-1]
                terminal_value = (last_cf * (1 + terminal_growth_rate)) / (discount_rate - terminal_growth_rate)
                pv_terminal = terminal_value / ((1 + discount_rate) ** len(cash_flows))
            else:
                pv_terminal = 0
            
            # 总估值
            total_value = pv_cash_flows + pv_terminal
            
            # 计算置信区间 (±15%)
            lower_bound = total_value * 0.85
            upper_bound = total_value * 1.15
            
            return ValuationResult(
                asset_id=asset.id,
                method=ValuationMethod.DCF,
                estimated_value=round(total_value, 2),
                lower_bound=round(lower_bound, 2),
                upper_bound=round(upper_bound, 2),
                confidence_level=0.85,
                parameters_used=params,
                breakdown={
                    "pv_cash_flows": round(pv_cash_flows, 2),
                    "terminal_value": round(pv_terminal, 2),
                    "discount_rate": discount_rate,
                    "years": len(cash_flows)
                },
                assumptions=[
                    f"折现率 {discount_rate*100:.1f}% 反映市场风险",
                    f"永续增长率 {terminal_growth_rate*100:.1f}%",
                    f"预测期 {len(cash_flows)} 年的现金流可靠",
                    "不考虑非经营性资产价值"
                ],
                valuator="DCF Model v1.0"
            )
        
        except Exception as e:
            logger.error(f"DCF valuation failed: {str(e)}")
            raise
    
    def _market_comparison_valuation(self, asset: Asset, params: Dict) -> ValuationResult:
        """
        市场比较法估值
        基于可比资产的市场价格进行估值
        """
        try:
            comp_params = MarketComparisonParameters(**params)
            
            comparable_assets = comp_params.comparable_assets
            adjustment_factors = comp_params.adjustment_factors
            market_premium = comp_params.market_premium
            
            if not comparable_assets:
                raise ValueError("No comparable assets provided")
            
            # 计算可比资产平均价格
            total_price = 0
            weights = []
            
            for comp in comparable_assets:
                price = comp.get("price", 0)
                similarity = comp.get("similarity", 1.0)  # 相似度权重
                
                # 应用调整因子
                adjusted_price = price
                for factor, value in adjustment_factors.items():
                    adjusted_price *= (1 + value)
                
                total_price += adjusted_price * similarity
                weights.append(similarity)
            
            # 加权平均价格
            avg_price = total_price / sum(weights) if weights else 0
            
            # 应用市场溢价
            estimated_value = avg_price * (1 + market_premium)
            
            # 置信区间
            std_dev = np.std([c.get("price", 0) for c in comparable_assets])
            lower_bound = estimated_value - std_dev
            upper_bound = estimated_value + std_dev
            
            return ValuationResult(
                asset_id=asset.id,
                method=ValuationMethod.MARKET_COMPARISON,
                estimated_value=round(estimated_value, 2),
                lower_bound=round(max(0, lower_bound), 2),
                upper_bound=round(upper_bound, 2),
                confidence_level=0.75,
                parameters_used=params,
                breakdown={
                    "comparable_count": len(comparable_assets),
                    "average_comparable_price": round(avg_price, 2),
                    "market_premium": market_premium,
                    "price_std_dev": round(std_dev, 2)
                },
                assumptions=[
                    f"参考 {len(comparable_assets)} 个可比资产",
                    "市场价格反映真实价值",
                    "调整因子准确反映差异",
                    f"市场溢价率 {market_premium*100:.1f}%"
                ],
                valuator="Market Comparison Model v1.0"
            )
        
        except Exception as e:
            logger.error(f"Market comparison valuation failed: {str(e)}")
            raise
    
    def _liquidation_valuation(self, asset: Asset, params: Dict) -> ValuationResult:
        """
        清算价值法估值
        快速处置情况下的资产价值
        """
        try:
            liq_params = LiquidationParameters(**params)
            
            # 从资产当前价值或原始价值开始
            base_value = asset.current_value or asset.original_value
            
            # 应用强制出售折扣
            discounted_value = base_value * (1 - liq_params.forced_sale_discount)
            
            # 扣除清算成本
            liquidation_value = discounted_value - liq_params.liquidation_costs
            
            # 确保不为负值
            liquidation_value = max(0, liquidation_value)
            
            # 根据出售时间调整（时间越长，价值越低）
            time_factor = 1 - (liq_params.estimated_time_to_sell / 365 * 0.1)
            time_factor = max(0.7, time_factor)  # 最多降低30%
            
            final_value = liquidation_value * time_factor
            
            return ValuationResult(
                asset_id=asset.id,
                method=ValuationMethod.LIQUIDATION,
                estimated_value=round(final_value, 2),
                lower_bound=round(final_value * 0.8, 2),
                upper_bound=round(final_value * 1.1, 2),
                confidence_level=0.70,
                parameters_used=params,
                breakdown={
                    "base_value": round(base_value, 2),
                    "forced_sale_discount": liq_params.forced_sale_discount,
                    "liquidation_costs": liq_params.liquidation_costs,
                    "time_adjustment_factor": round(time_factor, 3),
                    "estimated_time_days": liq_params.estimated_time_to_sell
                },
                assumptions=[
                    "资产需要快速变现",
                    f"强制出售折扣 {liq_params.forced_sale_discount*100:.0f}%",
                    f"预计 {liq_params.estimated_time_to_sell} 天内完成交易",
                    "市场流动性一般"
                ],
                valuator="Liquidation Value Model v1.0"
            )
        
        except Exception as e:
            logger.error(f"Liquidation valuation failed: {str(e)}")
            raise
    
    def _cost_valuation(self, asset: Asset, params: Dict) -> ValuationResult:
        """
        成本法估值
        基于重置成本和折旧计算价值
        """
        try:
            cost_params = CostParameters(**params)
            
            replacement_cost = cost_params.replacement_cost
            depreciation_rate = cost_params.depreciation_rate
            age = cost_params.age_of_asset
            obsolescence = cost_params.obsolescence_factor
            
            # 计算物理折旧
            physical_depreciation = replacement_cost * depreciation_rate * age
            
            # 计算功能性过时损失
            obsolescence_loss = replacement_cost * obsolescence
            
            # 重置成本 - 折旧 - 过时损失
            estimated_value = replacement_cost - physical_depreciation - obsolescence_loss
            estimated_value = max(0, estimated_value)
            
            return ValuationResult(
                asset_id=asset.id,
                method=ValuationMethod.COST,
                estimated_value=round(estimated_value, 2),
                lower_bound=round(estimated_value * 0.9, 2),
                upper_bound=round(estimated_value * 1.1, 2),
                confidence_level=0.80,
                parameters_used=params,
                breakdown={
                    "replacement_cost": replacement_cost,
                    "physical_depreciation": round(physical_depreciation, 2),
                    "obsolescence_loss": round(obsolescence_loss, 2),
                    "asset_age": age,
                    "depreciation_rate": depreciation_rate
                },
                assumptions=[
                    f"重置成本 ¥{replacement_cost:,.0f}",
                    f"年折旧率 {depreciation_rate*100:.1f}%",
                    f"资产年龄 {age} 年",
                    f"技术过时因子 {obsolescence*100:.1f}%"
                ],
                valuator="Cost Approach Model v1.0"
            )
        
        except Exception as e:
            logger.error(f"Cost valuation failed: {str(e)}")
            raise
    
    def _income_valuation(self, asset: Asset, params: Dict) -> ValuationResult:
        """
        收益法估值
        基于资产产生的收益流估值
        """
        try:
            income_params = IncomeParameters(**params)
            
            annual_income = income_params.annual_income
            operating_expenses = income_params.operating_expenses
            cap_rate = income_params.capitalization_rate
            vacancy_rate = income_params.vacancy_rate
            
            # 计算净营运收入 (NOI)
            effective_income = annual_income * (1 - vacancy_rate)
            noi = effective_income - operating_expenses
            
            # 使用资本化率计算价值
            estimated_value = noi / cap_rate if cap_rate > 0 else 0
            
            return ValuationResult(
                asset_id=asset.id,
                method=ValuationMethod.INCOME,
                estimated_value=round(estimated_value, 2),
                lower_bound=round(estimated_value * 0.85, 2),
                upper_bound=round(estimated_value * 1.15, 2),
                confidence_level=0.82,
                parameters_used=params,
                breakdown={
                    "annual_income": annual_income,
                    "operating_expenses": operating_expenses,
                    "effective_income": round(effective_income, 2),
                    "noi": round(noi, 2),
                    "cap_rate": cap_rate,
                    "vacancy_rate": vacancy_rate
                },
                assumptions=[
                    f"年收入 ¥{annual_income:,.0f}",
                    f"空置率 {vacancy_rate*100:.1f}%",
                    f"资本化率 {cap_rate*100:.1f}%",
                    "收入和支出保持稳定"
                ],
                valuator="Income Capitalization Model v1.0"
            )
        
        except Exception as e:
            logger.error(f"Income valuation failed: {str(e)}")
            raise
    
    def _ai_valuation(self, asset: Asset, params: Dict) -> ValuationResult:
        """
        AI智能估值
        使用机器学习模型进行估值
        """
        try:
            ai_params = AIValuationParameters(**params)
            features = ai_params.features
            
            # 这里是简化的AI估值逻辑
            # 实际应该使用训练好的ML模型
            
            # 基础价值
            base_value = asset.current_value or asset.original_value
            
            # 特征权重（示例）
            feature_weights = {
                "location_score": 0.3,
                "condition_score": 0.25,
                "market_trend": 0.2,
                "liquidity_score": 0.15,
                "risk_score": 0.1
            }
            
            # 计算特征调整
            total_adjustment = 0
            for feature, weight in feature_weights.items():
                if feature in features:
                    # 特征值范围 0-1，转换为 -20% 到 +20% 的调整
                    feature_value = features[feature]
                    adjustment = (feature_value - 0.5) * 0.4 * weight
                    total_adjustment += adjustment
            
            # 应用AI调整
            estimated_value = base_value * (1 + total_adjustment)
            
            # 置信度基于特征完整性
            confidence = len(features) / len(feature_weights) * 0.9
            
            return ValuationResult(
                asset_id=asset.id,
                method=ValuationMethod.AI_MODEL,
                estimated_value=round(estimated_value, 2),
                lower_bound=round(estimated_value * 0.85, 2),
                upper_bound=round(estimated_value * 1.15, 2),
                confidence_level=round(confidence, 2),
                parameters_used=params,
                breakdown={
                    "base_value": base_value,
                    "ai_adjustment": round(total_adjustment * 100, 2),
                    "features_used": list(features.keys()),
                    "model_type": ai_params.model_type
                },
                assumptions=[
                    f"使用 {ai_params.model_type} 模型",
                    f"基于 {len(features)} 个特征",
                    "模型基于历史交易数据训练",
                    "市场条件与训练数据相似"
                ],
                valuator=f"AI Model ({ai_params.model_type}) v1.0",
                notes="AI估值结果仅供参考，建议结合其他估值方法"
            )
        
        except Exception as e:
            logger.error(f"AI valuation failed: {str(e)}")
            raise
    
    def compare_valuations(self, asset: Asset, methods: List[ValuationMethod],
                          parameters_dict: Dict[ValuationMethod, Dict]) -> ValuationComparison:
        """
        多方法估值比较
        
        Args:
            asset: 资产对象
            methods: 估值方法列表
            parameters_dict: 各方法参数字典
            
        Returns:
            ValuationComparison: 估值比较结果
        """
        valuations = []
        
        for method in methods:
            params = parameters_dict.get(method, {})
            request = ValuationRequest(
                asset_id=asset.id,
                method=method,
                parameters=params
            )
            result = self.estimate_value(asset, request)
            valuations.append(result)
        
        # 计算统计指标
        values = [v.estimated_value for v in valuations]
        weights = [v.confidence_level for v in valuations]
        
        # 加权平均
        weighted_avg = sum(v * w for v, w in zip(values, weights)) / sum(weights)
        
        # 推荐值（取中位数或加权平均）
        recommended = np.median(values)
        
        # 方差和标准差
        variance = np.var(values)
        std_dev = np.std(values)
        
        return ValuationComparison(
            asset_id=asset.id,
            valuations=valuations,
            weighted_average=round(weighted_avg, 2),
            recommended_value=round(recommended, 2),
            variance=round(variance, 2),
            standard_deviation=round(std_dev, 2)
        )
    
    def sensitivity_analysis(self, asset: Asset, base_params: Dict,
                            variable_ranges: Dict) -> SensitivityAnalysis:
        """
        敏感性分析
        
        Args:
            asset: 资产对象
            base_params: 基准参数
            variable_ranges: 变量范围 {"discount_rate": [0.06, 0.08, 0.10]}
            
        Returns:
            SensitivityAnalysis: 敏感性分析结果
        """
        # 基准情况估值
        base_request = ValuationRequest(
            asset_id=asset.id,
            method=ValuationMethod.DCF,
            parameters=base_params
        )
        base_result = self.estimate_value(asset, base_request)
        base_value = base_result.estimated_value
        
        # 情景分析
        scenarios = {}
        key_drivers = []
        
        for variable, values in variable_ranges.items():
            for value in values:
                # 创建新参数
                test_params = base_params.copy()
                
                # 更新变量
                if variable in test_params:
                    test_params[variable] = value
                
                # 计算估值
                test_request = ValuationRequest(
                    asset_id=asset.id,
                    method=ValuationMethod.DCF,
                    parameters=test_params
                )
                result = self.estimate_value(asset, test_request)
                
                # 记录场景
                scenario_name = f"{variable}_{value}"
                scenarios[scenario_name] = {
                    "value": result.estimated_value,
                    "change": result.estimated_value - base_value,
                    "change_pct": (result.estimated_value - base_value) / base_value
                }
                
                # 记录关键驱动因素
                key_drivers.append({
                    "factor": variable,
                    "test_value": value,
                    "impact": result.estimated_value - base_value,
                    "value_change": result.estimated_value - base_value
                })
        
        return SensitivityAnalysis(
            asset_id=asset.id,
            base_case_value=base_value,
            scenarios=scenarios,
            key_drivers=key_drivers
        )


# 创建全局服务实例
valuation_service = ValuationService()
