"""
RWA低效资产数据模型
支持多种类型的低效资产管理
"""

from datetime import datetime
from enum import Enum
from typing import Optional, Dict, List
from pydantic import BaseModel, Field


class AssetType(str, Enum):
    """资产类型枚举"""
    NPL = "npl"  # Non-Performing Loan 不良贷款
    REAL_ESTATE = "real_estate"  # 房地产
    INVENTORY = "inventory"  # 库存资产
    COLLATERAL = "collateral"  # 抵押资产
    RECEIVABLES = "receivables"  # 应收账款
    EQUIPMENT = "equipment"  # 设备资产
    OTHERS = "others"  # 其他


class AssetStatus(str, Enum):
    """资产状态"""
    IDLE = "idle"  # 闲置
    DISTRESSED = "distressed"  # 困境
    LIQUIDATING = "liquidating"  # 清算中
    TOKENIZED = "tokenized"  # 已代币化
    SOLD = "sold"  # 已出售
    RESTRUCTURING = "restructuring"  # 重组中


class RiskLevel(str, Enum):
    """风险等级"""
    A = "A"  # 低风险 (800-1000分)
    B = "B"  # 较低风险 (650-799分)
    C = "C"  # 中等风险 (500-649分)
    D = "D"  # 较高风险 (350-499分)
    E = "E"  # 高风险 (0-349分)


class Asset(BaseModel):
    """资产基础模型"""
    id: Optional[str] = None
    name: str = Field(..., description="资产名称")
    asset_type: AssetType = Field(..., description="资产类型")
    status: AssetStatus = Field(default=AssetStatus.IDLE, description="资产状态")
    
    # 价值信息
    original_value: float = Field(..., gt=0, description="原始价值（元）")
    current_value: Optional[float] = Field(None, description="当前估值（元）")
    market_value: Optional[float] = Field(None, description="市场价值（元）")
    liquidation_value: Optional[float] = Field(None, description="清算价值（元）")
    
    # 基本信息
    description: str = Field(..., description="资产描述")
    location: Optional[str] = Field(None, description="资产位置")
    acquisition_date: datetime = Field(default_factory=datetime.now, description="获取日期")
    
    # 风险信息
    risk_level: Optional[RiskLevel] = Field(None, description="风险等级")
    credit_score: Optional[int] = Field(None, ge=0, le=1000, description="信用评分")
    default_probability: Optional[float] = Field(None, ge=0, le=1, description="违约概率")
    
    # 代币化信息
    is_tokenized: bool = Field(default=False, description="是否已代币化")
    token_contract: Optional[str] = Field(None, description="代币合约地址")
    token_id: Optional[str] = Field(None, description="代币ID")
    
    # 元数据
    metadata: Dict = Field(default_factory=dict, description="额外元数据")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        use_enum_values = True


class RealEstateAsset(Asset):
    """房地产资产"""
    asset_type: AssetType = AssetType.REAL_ESTATE
    
    # 房地产特定字段
    area: float = Field(..., gt=0, description="建筑面积（平方米）")
    property_type: str = Field(..., description="物业类型：住宅/商业/工业")
    year_built: Optional[int] = Field(None, description="建造年份")
    occupancy_rate: float = Field(default=0.0, ge=0, le=1, description="入住率")
    annual_rental_income: Optional[float] = Field(None, description="年租金收入")
    

class NPLAsset(Asset):
    """不良贷款资产"""
    asset_type: AssetType = AssetType.NPL
    
    # 贷款特定字段
    loan_amount: float = Field(..., gt=0, description="贷款金额")
    outstanding_balance: float = Field(..., description="未偿还余额")
    interest_rate: float = Field(..., description="利率")
    overdue_days: int = Field(default=0, ge=0, description="逾期天数")
    borrower_info: Dict = Field(default_factory=dict, description="借款人信息")
    collateral_info: Optional[Dict] = Field(None, description="抵押物信息")


class InventoryAsset(Asset):
    """库存资产"""
    asset_type: AssetType = AssetType.INVENTORY
    
    # 库存特定字段
    quantity: int = Field(..., gt=0, description="库存数量")
    unit_cost: float = Field(..., gt=0, description="单位成本")
    storage_location: str = Field(..., description="仓储位置")
    storage_cost: float = Field(default=0.0, description="仓储费用/月")
    shelf_life: Optional[int] = Field(None, description="保质期（天）")
    aging_days: int = Field(default=0, description="库龄（天）")


class ReceivablesAsset(Asset):
    """应收账款资产"""
    asset_type: AssetType = AssetType.RECEIVABLES
    
    # 应收账款特定字段
    invoice_amount: float = Field(..., gt=0, description="发票金额")
    invoice_date: datetime = Field(..., description="发票日期")
    due_date: datetime = Field(..., description="到期日期")
    debtor_name: str = Field(..., description="债务人名称")
    debtor_credit_score: Optional[int] = Field(None, description="债务人信用评分")
    days_overdue: int = Field(default=0, description="逾期天数")


class AssetValuation(BaseModel):
    """资产估值记录"""
    id: Optional[str] = None
    asset_id: str = Field(..., description="资产ID")
    valuation_method: str = Field(..., description="估值方法")
    estimated_value: float = Field(..., description="估值结果")
    confidence_level: float = Field(..., ge=0, le=1, description="置信度")
    parameters: Dict = Field(default_factory=dict, description="估值参数")
    valuation_date: datetime = Field(default_factory=datetime.now)
    valuator: Optional[str] = Field(None, description="估值人/机构")
    notes: Optional[str] = Field(None, description="备注")


class AssetTransaction(BaseModel):
    """资产交易记录"""
    id: Optional[str] = None
    asset_id: str = Field(..., description="资产ID")
    transaction_type: str = Field(..., description="交易类型：buy/sell/transfer")
    from_party: str = Field(..., description="转出方")
    to_party: str = Field(..., description="接收方")
    amount: float = Field(..., description="交易金额")
    quantity: float = Field(default=1.0, description="交易数量")
    transaction_hash: Optional[str] = Field(None, description="区块链交易哈希")
    transaction_date: datetime = Field(default_factory=datetime.now)
    status: str = Field(default="pending", description="交易状态")


class AssetPool(BaseModel):
    """资产包/资产池"""
    id: Optional[str] = None
    name: str = Field(..., description="资产包名称")
    description: str = Field(..., description="描述")
    asset_ids: List[str] = Field(default_factory=list, description="包含的资产ID列表")
    total_value: float = Field(default=0.0, description="总价值")
    average_risk_level: Optional[str] = Field(None, description="平均风险等级")
    created_at: datetime = Field(default_factory=datetime.now)
    is_tokenized: bool = Field(default=False, description="是否已代币化")
    token_contract: Optional[str] = Field(None, description="代币合约地址")


# 示例数据
EXAMPLE_NPL_ASSET = NPLAsset(
    name="某企业不良贷款资产",
    original_value=5000000,
    current_value=2500000,
    description="某中小企业经营贷款，逾期6个月，有房产抵押",
    location="上海市浦东新区",
    loan_amount=5000000,
    outstanding_balance=5200000,
    interest_rate=0.065,
    overdue_days=180,
    borrower_info={
        "name": "某某科技有限公司",
        "industry": "制造业",
        "employees": 50
    },
    collateral_info={
        "type": "real_estate",
        "estimated_value": 3000000,
        "location": "上海市浦东新区张江"
    }
)

EXAMPLE_REAL_ESTATE = RealEstateAsset(
    name="某商业写字楼闲置资产",
    original_value=30000000,
    current_value=25000000,
    description="核心商圈写字楼，长期空置",
    location="北京市朝阳区国贸CBD",
    area=2000,
    property_type="商业",
    year_built=2015,
    occupancy_rate=0.3,
    annual_rental_income=1500000
)
