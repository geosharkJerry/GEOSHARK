"""
RWA资产代币化模型
支持NFT和ERC-20代币化
"""

from datetime import datetime
from enum import Enum
from typing import Optional, Dict, List
from pydantic import BaseModel, Field


class TokenStandard(str, Enum):
    """代币标准"""
    ERC20 = "erc20"  # 同质化代币
    ERC721 = "erc721"  # NFT非同质化代币
    ERC1155 = "erc1155"  # 半同质化代币


class TokenizationStatus(str, Enum):
    """代币化状态"""
    PENDING = "pending"  # 待处理
    IN_PROGRESS = "in_progress"  # 进行中
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"  # 失败
    REVOKED = "revoked"  # 已撤销


class TokenType(str, Enum):
    """代币类型"""
    ASSET_NFT = "asset_nft"  # 资产NFT
    FRACTIONAL = "fractional"  # 资产份额代币
    SECURITY = "security"  # 证券型代币
    UTILITY = "utility"  # 实用型代币
    GOVERNANCE = "governance"  # 治理代币


class BlockchainNetwork(str, Enum):
    """区块链网络"""
    ETHEREUM = "ethereum"
    POLYGON = "polygon"
    BSC = "bsc"  # Binance Smart Chain
    ARBITRUM = "arbitrum"
    OPTIMISM = "optimism"
    AVALANCHE = "avalanche"


class TokenizationRequest(BaseModel):
    """代币化请求"""
    asset_id: str = Field(..., description="资产ID")
    token_standard: TokenStandard = Field(..., description="代币标准")
    token_type: TokenType = Field(..., description="代币类型")
    network: BlockchainNetwork = Field(..., description="区块链网络")
    
    # 代币基本信息
    token_name: str = Field(..., description="代币名称")
    token_symbol: str = Field(..., description="代币符号")
    total_supply: int = Field(..., gt=0, description="总供应量")
    
    # 价格和分配
    initial_price: float = Field(..., gt=0, description="初始价格（单位：USD）")
    min_investment: float = Field(default=100, description="最低投资额")
    max_investment: Optional[float] = Field(None, description="最高投资额")
    
    # 元数据
    metadata: Dict = Field(default_factory=dict, description="代币元数据")
    metadata_uri: Optional[str] = Field(None, description="元数据URI（IPFS等）")
    
    # 智能合约参数
    is_transferable: bool = Field(default=True, description="是否可转让")
    is_burnable: bool = Field(default=False, description="是否可销毁")
    is_mintable: bool = Field(default=False, description="是否可增发")
    has_whitelist: bool = Field(default=False, description="是否有白名单")
    
    # 合规设置
    kyc_required: bool = Field(default=True, description="是否需要KYC")
    accredited_investor_only: bool = Field(default=False, description="仅限合格投资者")
    jurisdiction_restrictions: List[str] = Field(default_factory=list, description="司法管辖限制")
    
    # 请求信息
    requester: str = Field(..., description="请求人")
    requested_at: datetime = Field(default_factory=datetime.now)


class TokenMetadata(BaseModel):
    """代币元数据"""
    name: str = Field(..., description="名称")
    description: str = Field(..., description="描述")
    image: Optional[str] = Field(None, description="图片URI")
    
    # 资产相关
    asset_type: str = Field(..., description="资产类型")
    asset_value: float = Field(..., description="资产价值")
    valuation_date: datetime = Field(..., description="估值日期")
    
    # 财务信息
    expected_return: Optional[float] = Field(None, description="预期回报率")
    risk_level: Optional[str] = Field(None, description="风险等级")
    
    # 法律文档
    legal_documents: List[str] = Field(default_factory=list, description="法律文档URI")
    prospectus_uri: Optional[str] = Field(None, description="招股说明书URI")
    
    # 附加属性
    attributes: List[Dict] = Field(default_factory=list, description="其他属性")
    # 例如: [{"trait_type": "Location", "value": "Shanghai"}]


class TokenContract(BaseModel):
    """代币合约信息"""
    contract_address: str = Field(..., description="合约地址")
    contract_name: str = Field(..., description="合约名称")
    network: BlockchainNetwork = Field(..., description="区块链网络")
    standard: TokenStandard = Field(..., description="代币标准")
    
    # 合约部署信息
    deployer_address: str = Field(..., description="部署者地址")
    deployment_tx_hash: str = Field(..., description="部署交易哈希")
    deployment_date: datetime = Field(default_factory=datetime.now)
    block_number: int = Field(..., description="部署区块号")
    
    # 合约状态
    is_verified: bool = Field(default=False, description="是否已验证")
    is_paused: bool = Field(default=False, description="是否已暂停")
    owner_address: Optional[str] = Field(None, description="拥有者地址")
    
    # 合约参数
    total_supply: int = Field(..., description="总供应量")
    decimals: int = Field(default=18, description="小数位数")
    
    # ABI和源码
    abi: Optional[List] = Field(None, description="合约ABI")
    source_code: Optional[str] = Field(None, description="源代码")


class TokenHolder(BaseModel):
    """代币持有者"""
    address: str = Field(..., description="钱包地址")
    balance: float = Field(..., ge=0, description="持有数量")
    percentage: float = Field(..., ge=0, le=100, description="持有占比（%）")
    
    # 持有者信息
    holder_type: str = Field(default="individual", description="持有者类型：individual/institutional")
    kyc_verified: bool = Field(default=False, description="是否通过KYC")
    first_acquisition_date: datetime = Field(..., description="首次获得日期")
    
    # 锁定信息
    locked_amount: float = Field(default=0.0, description="锁定数量")
    unlock_date: Optional[datetime] = Field(None, description="解锁日期")


class TokenTransaction(BaseModel):
    """代币交易记录"""
    tx_hash: str = Field(..., description="交易哈希")
    from_address: str = Field(..., description="发送方地址")
    to_address: str = Field(..., description="接收方地址")
    amount: float = Field(..., description="交易数量")
    
    # 交易详情
    transaction_type: str = Field(..., description="交易类型：transfer/mint/burn")
    block_number: int = Field(..., description="区块号")
    timestamp: datetime = Field(..., description="交易时间")
    gas_used: Optional[int] = Field(None, description="消耗Gas")
    gas_price: Optional[float] = Field(None, description="Gas价格")
    
    # 交易价值
    token_price_usd: Optional[float] = Field(None, description="代币价格（USD）")
    transaction_value_usd: Optional[float] = Field(None, description="交易价值（USD）")
    
    # 状态
    status: str = Field(default="confirmed", description="交易状态")
    confirmations: int = Field(default=0, description="确认数")


class TokenizationResult(BaseModel):
    """代币化结果"""
    asset_id: str = Field(..., description="资产ID")
    status: TokenizationStatus = Field(..., description="代币化状态")
    
    # 代币信息
    token_contract: Optional[TokenContract] = Field(None, description="代币合约")
    token_standard: TokenStandard = Field(..., description="代币标准")
    total_supply: int = Field(..., description="总供应量")
    
    # 铸造信息
    minted_amount: int = Field(..., description="已铸造数量")
    mint_tx_hash: Optional[str] = Field(None, description="铸造交易哈希")
    
    # 元数据
    metadata_uri: Optional[str] = Field(None, description="元数据URI")
    metadata: Optional[TokenMetadata] = Field(None, description="元数据内容")
    
    # 状态信息
    tokenized_at: Optional[datetime] = Field(None, description="代币化完成时间")
    error_message: Optional[str] = Field(None, description="错误信息")
    
    class Config:
        use_enum_values = True


class TokenPricing(BaseModel):
    """代币定价"""
    token_address: str = Field(..., description="代币地址")
    network: BlockchainNetwork = Field(..., description="区块链网络")
    
    # 价格信息
    current_price: float = Field(..., description="当前价格（USD）")
    initial_price: float = Field(..., description="初始价格（USD）")
    price_change_24h: float = Field(..., description="24小时价格变化（%）")
    price_change_7d: float = Field(..., description="7日价格变化（%）")
    
    # 市场数据
    market_cap: float = Field(..., description="市值（USD）")
    circulating_supply: int = Field(..., description="流通量")
    total_supply: int = Field(..., description="总供应量")
    
    # 交易数据
    volume_24h: float = Field(..., description="24小时交易量（USD）")
    liquidity: float = Field(..., description="流动性（USD）")
    
    # 技术指标
    volatility: float = Field(..., description="波动率")
    sharpe_ratio: Optional[float] = Field(None, description="夏普比率")
    
    # 更新时间
    last_updated: datetime = Field(default_factory=datetime.now)


class DistributionSchedule(BaseModel):
    """代币分配计划"""
    token_address: str = Field(..., description="代币地址")
    
    # 分配方案
    distributions: List[Dict] = Field(..., description="分配方案")
    # 例如: [{"category": "public_sale", "percentage": 40, "amount": 400000}]
    
    # 锁定和释放
    vesting_schedule: List[Dict] = Field(default_factory=list, description="锁仓释放计划")
    # 例如: [{"date": "2025-01-01", "amount": 100000, "percentage": 10}]
    
    total_distributed: int = Field(default=0, description="已分配总量")
    remaining: int = Field(..., description="剩余待分配")


class SecondaryMarket(BaseModel):
    """二级市场信息"""
    token_address: str = Field(..., description="代币地址")
    
    # 交易所列表
    exchanges: List[Dict] = Field(default_factory=list, description="上市交易所")
    # 例如: [{"name": "Uniswap", "pair": "TOKEN/USDT", "liquidity": 500000}]
    
    # 做市商
    market_makers: List[str] = Field(default_factory=list, description="做市商列表")
    
    # 流动性池
    liquidity_pools: List[Dict] = Field(default_factory=list, description="流动性池")
    
    # 市场深度
    bid_depth: float = Field(..., description="买单深度")
    ask_depth: float = Field(..., description="卖单深度")


# 示例代币化请求
EXAMPLE_TOKENIZATION_REQUEST = TokenizationRequest(
    asset_id="asset_001",
    token_standard=TokenStandard.ERC721,
    token_type=TokenType.ASSET_NFT,
    network=BlockchainNetwork.POLYGON,
    token_name="Real Estate Asset NFT #001",
    token_symbol="REA",
    total_supply=1,
    initial_price=1000000,
    min_investment=100000,
    metadata={
        "asset_type": "real_estate",
        "location": "Shanghai",
        "area": 2000,
        "valuation": 1000000
    },
    is_transferable=True,
    kyc_required=True,
    requester="admin@platform.com"
)
