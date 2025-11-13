"""
RWA低效资产管理系统 - FastAPI应用入口
提供RESTful API接口
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

from backend.api.routes import all_routers
from backend.models.asset import NPLAsset, RealEstateAsset, InventoryAsset
from backend.services.asset_service import AssetService

# 创建FastAPI应用
app = FastAPI(
    title="RWA低效资产管理系统API",
    description="Real World Assets - Underperforming Assets Management System API\n\n"
                "支持低效资产的全生命周期管理：\n"
                "- 资产管理（CRUD）\n"
                "- 多方法估值（DCF、市场比较法、清算价值法等）\n"
                "- 多维度风险评估（信用、市场、流动性、操作风险）\n"
                "- 区块链代币化（NFT和ERC-20）\n"
                "- 交易管理和资产池\n",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册所有路由
for router in all_routers:
    app.include_router(router)

# 初始化服务
asset_service = AssetService(data_dir="data")


# ==================== 健康检查和基本路由 ====================

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "RWA低效资产管理系统API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "assets": "/api/assets",
            "valuation": "/api/valuation",
            "risk": "/api/risk",
            "tokenization": "/api/tokenization"
        }
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


# ==================== 演示数据 ====================

@app.post("/api/demo/create-sample-assets")
async def create_sample_assets():
    """创建示例资产数据"""
    sample_assets = []
    
    # 不良贷款示例
    npl1 = NPLAsset(
        name="某制造企业不良贷款",
        original_value=5000000,
        current_value=2500000,
        description="某中小制造企业经营贷款，逾期6个月，有厂房抵押",
        location="上海市浦东新区",
        loan_amount=5000000,
        outstanding_balance=5200000,
        interest_rate=0.065,
        overdue_days=180,
        borrower_info={"name": "某某制造有限公司", "industry": "制造业"},
        collateral_info={"type": "factory", "value": 3000000}
    )
    sample_assets.append(asset_service.create_asset(npl1))
    
    # 房地产示例
    re1 = RealEstateAsset(
        name="核心商圈写字楼闲置资产",
        original_value=30000000,
        current_value=25000000,
        description="CBD核心区写字楼，长期空置，入住率30%",
        location="北京市朝阳区国贸",
        area=2000,
        property_type="商业",
        year_built=2015,
        occupancy_rate=0.3,
        annual_rental_income=1500000
    )
    sample_assets.append(asset_service.create_asset(re1))
    
    # 库存资产示例
    inv1 = InventoryAsset(
        name="电子产品积压库存",
        original_value=2000000,
        current_value=1200000,
        description="某品牌手机库存积压，库龄超过1年",
        location="深圳市",
        quantity=5000,
        unit_cost=400,
        storage_location="深圳保税区",
        storage_cost=10000,
        aging_days=400
    )
    sample_assets.append(asset_service.create_asset(inv1))
    
    return {
        "message": "示例资产创建成功",
        "count": len(sample_assets),
        "assets": [{"id": a.id, "name": a.name} for a in sample_assets]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
