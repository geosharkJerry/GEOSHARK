"""
RWA资产管理系统 - API路由
完整的RESTful API端点定义
"""

from fastapi import APIRouter, HTTPException, Query, Path
from typing import List, Optional, Dict
from datetime import datetime

from backend.models.asset import (
    Asset, AssetType, AssetStatus, RiskLevel,
    NPLAsset, RealEstateAsset, InventoryAsset, ReceivablesAsset,
    AssetValuation, AssetTransaction, AssetPool
)
from backend.models.valuation import (
    ValuationRequest, ValuationResult, ValuationMethod,
    ValuationComparison, SensitivityAnalysis
)
from backend.models.risk import (
    RiskAssessmentRequest, ComprehensiveRiskAssessment,
    StressTestScenario, StressTestResult, RiskMonitoring,
    RiskType
)
from backend.models.token import (
    TokenizationRequest, TokenizationResult, TokenPricing,
    TokenHolder, TokenTransaction, DistributionSchedule
)

from backend.services.asset_service import AssetService
from backend.services.valuation_service import valuation_service
from backend.services.risk_service import risk_service
from backend.services.tokenization_service import tokenization_service


# 创建路由器
asset_router = APIRouter(prefix="/api/assets", tags=["Assets"])
valuation_router = APIRouter(prefix="/api/valuation", tags=["Valuation"])
risk_router = APIRouter(prefix="/api/risk", tags=["Risk Assessment"])
token_router = APIRouter(prefix="/api/tokenization", tags=["Tokenization"])


# 初始化服务
asset_service = AssetService(data_dir="data")


# ==================== 资产管理路由 ====================

@asset_router.post("", response_model=Asset, summary="创建资产")
async def create_asset(asset: Asset):
    """创建新的低效资产"""
    try:
        created = asset_service.create_asset(asset)
        return created
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@asset_router.get("/{asset_id}", response_model=Asset, summary="获取资产详情")
async def get_asset(
    asset_id: str = Path(..., description="资产ID")
):
    """获取单个资产的详细信息"""
    asset = asset_service.get_asset(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="资产未找到")
    return asset


@asset_router.put("/{asset_id}", response_model=Asset, summary="更新资产")
async def update_asset(
    asset_id: str = Path(..., description="资产ID"),
    updates: Dict = None
):
    """更新资产信息"""
    asset = asset_service.update_asset(asset_id, updates)
    if not asset:
        raise HTTPException(status_code=404, detail="资产未找到")
    return asset


@asset_router.delete("/{asset_id}", summary="删除资产")
async def delete_asset(
    asset_id: str = Path(..., description="资产ID")
):
    """删除资产"""
    success = asset_service.delete_asset(asset_id)
    if not success:
        raise HTTPException(status_code=404, detail="资产未找到")
    return {"message": "资产已删除", "asset_id": asset_id}


@asset_router.get("", response_model=List[Asset], summary="列出资产")
async def list_assets(
    asset_type: Optional[AssetType] = Query(None, description="资产类型筛选"),
    status: Optional[AssetStatus] = Query(None, description="状态筛选"),
    risk_level: Optional[RiskLevel] = Query(None, description="风险等级筛选"),
    min_value: Optional[float] = Query(None, description="最小价值"),
    max_value: Optional[float] = Query(None, description="最大价值"),
    limit: int = Query(100, ge=1, le=1000, description="返回数量"),
    offset: int = Query(0, ge=0, description="偏移量")
):
    """列出所有资产，支持多维度筛选"""
    assets = asset_service.list_assets(
        asset_type=asset_type,
        status=status,
        risk_level=risk_level,
        min_value=min_value,
        max_value=max_value,
        limit=limit,
        offset=offset
    )
    return assets


@asset_router.get("/search/query", summary="搜索资产")
async def search_assets(
    q: str = Query(..., min_length=1, description="搜索关键词")
):
    """全文搜索资产"""
    results = asset_service.search_assets(q)
    return results


@asset_router.get("/stats/summary", summary="资产统计")
async def get_statistics():
    """获取资产统计信息"""
    stats = asset_service.get_statistics()
    return stats


# ==================== 估值路由 ====================

@valuation_router.post("/estimate", response_model=ValuationResult, summary="资产估值")
async def estimate_asset_value(request: ValuationRequest):
    """
    对资产进行估值
    支持多种估值方法：DCF、市场比较法、清算价值法、成本法、收益法、AI估值
    """
    # 获取资产
    asset = asset_service.get_asset(request.asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="资产未找到")
    
    try:
        result = valuation_service.estimate_value(asset, request)
        
        # 更新资产当前估值
        asset_service.update_asset(request.asset_id, {
            "current_value": result.estimated_value,
            "updated_at": datetime.now().isoformat()
        })
        
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@valuation_router.post("/compare", response_model=ValuationComparison, summary="多方法估值比较")
async def compare_valuations(
    asset_id: str,
    methods: List[ValuationMethod],
    parameters_dict: Dict[str, Dict]
):
    """
    使用多种方法对资产进行估值并比较结果
    提供加权平均值和推荐估值
    """
    asset = asset_service.get_asset(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="资产未找到")
    
    try:
        # 转换参数字典的键为枚举类型
        converted_params = {}
        for method_str, params in parameters_dict.items():
            method = ValuationMethod(method_str)
            converted_params[method] = params
        
        result = valuation_service.compare_valuations(
            asset, methods, converted_params
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@valuation_router.post("/sensitivity", response_model=SensitivityAnalysis, summary="敏感性分析")
async def sensitivity_analysis(
    asset_id: str,
    base_params: Dict,
    variable_ranges: Dict
):
    """
    进行估值敏感性分析
    分析关键变量对估值的影响
    """
    asset = asset_service.get_asset(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="资产未找到")
    
    try:
        result = valuation_service.sensitivity_analysis(
            asset, base_params, variable_ranges
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==================== 风险评估路由 ====================

@risk_router.post("/assess", response_model=ComprehensiveRiskAssessment, summary="综合风险评估")
async def assess_risk(request: RiskAssessmentRequest):
    """
    对资产进行综合风险评估
    包括信用风险、市场风险、流动性风险、操作风险等
    """
    asset = asset_service.get_asset(request.asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="资产未找到")
    
    try:
        assessment = risk_service.assess_comprehensive_risk(asset, request)
        
        # 更新资产风险信息
        asset_service.update_asset(request.asset_id, {
            "risk_level": assessment.overall_level,
            "credit_score": assessment.overall_score,
            "default_probability": assessment.probability_of_default,
            "updated_at": datetime.now().isoformat()
        })
        
        return assessment
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@risk_router.post("/stress-test", response_model=StressTestResult, summary="压力测试")
async def stress_test(
    asset_id: str,
    scenarios: List[StressTestScenario]
):
    """
    对资产进行压力测试
    评估极端情况下的风险表现
    """
    asset = asset_service.get_asset(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="资产未找到")
    
    try:
        result = risk_service.stress_test(asset, scenarios)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@risk_router.post("/monitoring", response_model=RiskMonitoring, summary="创建风险监控")
async def create_risk_monitoring(
    asset_id: str,
    risk_assessment: ComprehensiveRiskAssessment
):
    """
    为资产创建风险监控配置
    根据风险等级设置监控频率和预警阈值
    """
    asset = asset_service.get_asset(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="资产未找到")
    
    try:
        monitoring = risk_service.create_risk_monitoring(asset, risk_assessment)
        return monitoring
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==================== 代币化路由 ====================

@token_router.post("/mint", response_model=TokenizationResult, summary="铸造代币")
async def tokenize_asset(request: TokenizationRequest):
    """
    将资产代币化
    支持ERC-721 NFT和ERC-20份额代币
    """
    asset = asset_service.get_asset(request.asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="资产未找到")
    
    try:
        result = tokenization_service.tokenize_asset(asset, request)
        
        # 更新资产代币化状态
        if result.status == "completed":
            asset_service.update_asset(request.asset_id, {
                "is_tokenized": True,
                "token_contract": result.token_contract.contract_address if result.token_contract else None,
                "updated_at": datetime.now().isoformat()
            })
        
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@token_router.post("/transfer", response_model=TokenTransaction, summary="转移代币")
async def transfer_tokens(
    contract_address: str,
    from_address: str,
    to_address: str,
    amount: float
):
    """转移代币"""
    try:
        transaction = tokenization_service.transfer_tokens(
            contract_address, from_address, to_address, amount
        )
        return transaction
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@token_router.get("/holders/{contract_address}", response_model=List[TokenHolder], summary="获取持有者")
async def get_token_holders(contract_address: str):
    """获取代币持有者列表"""
    try:
        holders = tokenization_service.get_token_holders(contract_address)
        return holders
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@token_router.get("/price/{contract_address}", response_model=TokenPricing, summary="获取代币价格")
async def get_token_price(
    contract_address: str,
    network: str = Query(..., description="区块链网络")
):
    """获取代币价格信息"""
    try:
        from backend.models.token import BlockchainNetwork
        network_enum = BlockchainNetwork(network)
        pricing = tokenization_service.get_token_price(contract_address, network_enum)
        return pricing
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@token_router.post("/distribution", response_model=DistributionSchedule, summary="创建分配计划")
async def create_distribution_schedule(
    contract_address: str,
    total_supply: int,
    allocation: Dict[str, float]
):
    """创建代币分配计划"""
    try:
        schedule = tokenization_service.create_distribution_schedule(
            contract_address, total_supply, allocation
        )
        return schedule
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@token_router.post("/burn", summary="销毁代币")
async def burn_tokens(
    contract_address: str,
    amount: int
):
    """销毁代币"""
    try:
        tx_hash = tokenization_service.burn_tokens(contract_address, amount)
        return {"tx_hash": tx_hash, "amount": amount}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@token_router.get("/transactions/{contract_address}", response_model=List[TokenTransaction], summary="交易历史")
async def get_transaction_history(
    contract_address: str,
    address: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000)
):
    """获取代币交易历史"""
    try:
        transactions = tokenization_service.get_transaction_history(
            contract_address, address, limit
        )
        return transactions
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==================== 交易管理路由 ====================

transaction_router = APIRouter(prefix="/api/transactions", tags=["Transactions"])


@transaction_router.post("", response_model=AssetTransaction, summary="记录交易")
async def record_transaction(transaction: AssetTransaction):
    """记录资产交易"""
    try:
        recorded = asset_service.record_transaction(transaction)
        return recorded
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@transaction_router.get("/{asset_id}", response_model=List[AssetTransaction], summary="交易历史")
async def get_asset_transactions(asset_id: str):
    """获取资产的交易历史"""
    transactions = asset_service.get_asset_transactions(asset_id)
    return transactions


# ==================== 资产池路由 ====================

pool_router = APIRouter(prefix="/api/pools", tags=["Asset Pools"])


@pool_router.post("", response_model=AssetPool, summary="创建资产池")
async def create_asset_pool(pool: AssetPool):
    """创建资产池/资产包"""
    try:
        created = asset_service.create_asset_pool(pool)
        return created
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@pool_router.get("/{pool_id}", response_model=AssetPool, summary="获取资产池")
async def get_asset_pool(pool_id: str):
    """获取资产池详情"""
    pool = asset_service.get_asset_pool(pool_id)
    if not pool:
        raise HTTPException(status_code=404, detail="资产池未找到")
    return pool


@pool_router.get("", response_model=List[AssetPool], summary="列出资产池")
async def list_asset_pools():
    """列出所有资产池"""
    pools = asset_service.list_asset_pools()
    return pools


# 导出所有路由器
all_routers = [
    asset_router,
    valuation_router,
    risk_router,
    token_router,
    transaction_router,
    pool_router
]
