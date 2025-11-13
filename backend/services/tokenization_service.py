"""
资产代币化服务
支持ERC-20和ERC-721代币化，与区块链交互
"""

import json
import hashlib
from datetime import datetime
from typing import List, Dict, Optional
import logging

from backend.models.token import (
    TokenizationRequest, TokenizationResult, TokenizationStatus,
    TokenStandard, TokenType, BlockchainNetwork,
    TokenContract, TokenMetadata, TokenHolder, TokenTransaction,
    TokenPricing, DistributionSchedule
)
from backend.models.asset import Asset

logger = logging.getLogger(__name__)


class TokenizationService:
    """代币化服务类"""
    
    def __init__(self):
        self.contracts_cache: Dict[str, TokenContract] = {}
        # 在实际环境中，这里会初始化Web3连接
        # self.w3 = Web3(Web3.HTTPProvider(rpc_url))
    
    def tokenize_asset(self, asset: Asset, 
                      request: TokenizationRequest) -> TokenizationResult:
        """
        将资产代币化
        
        Args:
            asset: 资产对象
            request: 代币化请求
            
        Returns:
            TokenizationResult: 代币化结果
        """
        try:
            logger.info(f"Starting tokenization for asset {asset.id}")
            
            # 验证资产是否可以代币化
            self._validate_asset_for_tokenization(asset)
            
            # 创建代币元数据
            metadata = self._create_token_metadata(asset, request)
            
            # 上传元数据到IPFS（模拟）
            metadata_uri = self._upload_metadata_to_ipfs(metadata)
            
            # 部署智能合约
            contract = self._deploy_token_contract(asset, request, metadata_uri)
            
            # 铸造代币
            mint_tx_hash = self._mint_tokens(contract, request)
            
            # 创建代币化结果
            result = TokenizationResult(
                asset_id=asset.id,
                status=TokenizationStatus.COMPLETED,
                token_contract=contract,
                token_standard=request.token_standard,
                total_supply=request.total_supply,
                minted_amount=request.total_supply,
                mint_tx_hash=mint_tx_hash,
                metadata_uri=metadata_uri,
                metadata=metadata,
                tokenized_at=datetime.now()
            )
            
            logger.info(f"Tokenization completed for asset {asset.id}")
            return result
            
        except Exception as e:
            logger.error(f"Tokenization failed: {str(e)}")
            return TokenizationResult(
                asset_id=asset.id,
                status=TokenizationStatus.FAILED,
                token_standard=request.token_standard,
                total_supply=request.total_supply,
                minted_amount=0,
                error_message=str(e)
            )
    
    def _validate_asset_for_tokenization(self, asset: Asset):
        """验证资产是否符合代币化条件"""
        if asset.is_tokenized:
            raise ValueError("Asset is already tokenized")
        
        if not asset.current_value or asset.current_value <= 0:
            raise ValueError("Asset must have a valid current value")
        
        if asset.status == "sold":
            raise ValueError("Cannot tokenize sold assets")
    
    def _create_token_metadata(self, asset: Asset, 
                              request: TokenizationRequest) -> TokenMetadata:
        """创建代币元数据"""
        # 构建属性列表
        attributes = [
            {"trait_type": "Asset Type", "value": asset.asset_type},
            {"trait_type": "Risk Level", "value": asset.risk_level or "Unrated"},
            {"trait_type": "Status", "value": asset.status}
        ]
        
        # 添加位置信息
        if asset.location:
            attributes.append({"trait_type": "Location", "value": asset.location})
        
        # 添加资产特定属性
        if hasattr(asset, 'area'):
            attributes.append({
                "trait_type": "Area", 
                "value": f"{asset.area} sqm",
                "display_type": "number"
            })
        
        # 计算预期回报率（简化计算）
        expected_return = None
        if asset.current_value and asset.metadata.get("annual_income"):
            annual_income = asset.metadata["annual_income"]
            expected_return = (annual_income / asset.current_value) * 100
        
        return TokenMetadata(
            name=request.token_name,
            description=asset.description,
            image=request.metadata.get("image_uri"),
            asset_type=asset.asset_type,
            asset_value=asset.current_value or asset.original_value,
            valuation_date=datetime.now(),
            expected_return=expected_return,
            risk_level=asset.risk_level,
            legal_documents=request.metadata.get("legal_documents", []),
            prospectus_uri=request.metadata.get("prospectus_uri"),
            attributes=attributes
        )
    
    def _upload_metadata_to_ipfs(self, metadata: TokenMetadata) -> str:
        """
        上传元数据到IPFS
        在实际环境中，这里会调用IPFS API
        """
        # 模拟IPFS上传
        metadata_json = metadata.model_dump_json()
        metadata_hash = hashlib.sha256(metadata_json.encode()).hexdigest()
        ipfs_uri = f"ipfs://Qm{metadata_hash[:44]}"
        
        logger.info(f"Metadata uploaded to {ipfs_uri}")
        return ipfs_uri
    
    def _deploy_token_contract(self, asset: Asset, 
                               request: TokenizationRequest,
                               metadata_uri: str) -> TokenContract:
        """
        部署代币智能合约
        在实际环境中，这里会与区块链交互
        """
        # 模拟合约部署
        # 生成合约地址（模拟）
        contract_data = f"{asset.id}{request.token_name}{datetime.now()}"
        contract_hash = hashlib.sha256(contract_data.encode()).hexdigest()
        contract_address = f"0x{contract_hash[:40]}"
        
        # 生成交易哈希（模拟）
        tx_hash = f"0x{hashlib.sha256(contract_address.encode()).hexdigest()}"
        
        # 模拟区块号
        block_number = 12345678 + hash(asset.id) % 1000000
        
        # 部署者地址（模拟）
        deployer_address = "0x" + "1" * 40
        
        contract = TokenContract(
            contract_address=contract_address,
            contract_name=request.token_name,
            network=request.network,
            standard=request.token_standard,
            deployer_address=deployer_address,
            deployment_tx_hash=tx_hash,
            deployment_date=datetime.now(),
            block_number=block_number,
            is_verified=True,
            is_paused=False,
            owner_address=deployer_address,
            total_supply=request.total_supply,
            decimals=18 if request.token_standard == TokenStandard.ERC20 else 0
        )
        
        # 缓存合约信息
        self.contracts_cache[contract_address] = contract
        
        logger.info(f"Contract deployed at {contract_address}")
        return contract
    
    def _mint_tokens(self, contract: TokenContract, 
                    request: TokenizationRequest) -> str:
        """
        铸造代币
        在实际环境中，这里会调用智能合约的mint函数
        """
        # 模拟铸造交易
        mint_data = f"{contract.contract_address}{request.total_supply}{datetime.now()}"
        tx_hash = f"0x{hashlib.sha256(mint_data.encode()).hexdigest()}"
        
        logger.info(f"Minted {request.total_supply} tokens, tx: {tx_hash}")
        return tx_hash
    
    def transfer_tokens(self, contract_address: str, from_address: str,
                       to_address: str, amount: float) -> TokenTransaction:
        """
        转移代币
        
        Args:
            contract_address: 合约地址
            from_address: 发送方地址
            to_address: 接收方地址
            amount: 转移数量
            
        Returns:
            TokenTransaction: 交易记录
        """
        # 模拟转账交易
        tx_data = f"{from_address}{to_address}{amount}{datetime.now()}"
        tx_hash = f"0x{hashlib.sha256(tx_data.encode()).hexdigest()}"
        
        # 模拟区块号和Gas
        block_number = 12345678 + hash(tx_hash) % 1000000
        gas_used = 21000 + int(amount * 100)
        gas_price = 30.5  # Gwei
        
        transaction = TokenTransaction(
            tx_hash=tx_hash,
            from_address=from_address,
            to_address=to_address,
            amount=amount,
            transaction_type="transfer",
            block_number=block_number,
            timestamp=datetime.now(),
            gas_used=gas_used,
            gas_price=gas_price,
            status="confirmed",
            confirmations=12
        )
        
        logger.info(f"Transfer completed: {amount} tokens from {from_address[:10]}... to {to_address[:10]}...")
        return transaction
    
    def get_token_holders(self, contract_address: str) -> List[TokenHolder]:
        """
        获取代币持有者列表
        在实际环境中，这里会查询区块链数据
        """
        # 模拟持有者数据
        holders = [
            TokenHolder(
                address="0x" + "1" * 40,
                balance=5000,
                percentage=50.0,
                holder_type="institutional",
                kyc_verified=True,
                first_acquisition_date=datetime.now()
            ),
            TokenHolder(
                address="0x" + "2" * 40,
                balance=3000,
                percentage=30.0,
                holder_type="individual",
                kyc_verified=True,
                first_acquisition_date=datetime.now()
            ),
            TokenHolder(
                address="0x" + "3" * 40,
                balance=2000,
                percentage=20.0,
                holder_type="individual",
                kyc_verified=True,
                first_acquisition_date=datetime.now(),
                locked_amount=1000
            )
        ]
        
        return holders
    
    def get_token_price(self, contract_address: str, 
                       network: BlockchainNetwork) -> TokenPricing:
        """
        获取代币价格信息
        在实际环境中，这里会从DEX或价格预言机获取数据
        """
        # 模拟价格数据
        contract = self.contracts_cache.get(contract_address)
        
        if not contract:
            raise ValueError(f"Contract {contract_address} not found")
        
        # 生成模拟价格
        base_price = 100.0
        price_hash = int(hashlib.sha256(contract_address.encode()).hexdigest()[:8], 16)
        current_price = base_price * (1 + (price_hash % 100) / 100)
        
        pricing = TokenPricing(
            token_address=contract_address,
            network=network,
            current_price=round(current_price, 2),
            initial_price=base_price,
            price_change_24h=round((price_hash % 20) - 10, 2),
            price_change_7d=round((price_hash % 40) - 20, 2),
            market_cap=current_price * contract.total_supply,
            circulating_supply=contract.total_supply,
            total_supply=contract.total_supply,
            volume_24h=current_price * (contract.total_supply * 0.05),
            liquidity=current_price * (contract.total_supply * 0.1),
            volatility=0.15 + (price_hash % 20) / 100
        )
        
        return pricing
    
    def create_distribution_schedule(self, contract_address: str,
                                    total_supply: int,
                                    allocation: Dict[str, float]) -> DistributionSchedule:
        """
        创建代币分配计划
        
        Args:
            contract_address: 合约地址
            total_supply: 总供应量
            allocation: 分配方案 {"public_sale": 0.4, "team": 0.2, ...}
            
        Returns:
            DistributionSchedule: 分配计划
        """
        distributions = []
        
        for category, percentage in allocation.items():
            amount = int(total_supply * percentage)
            distributions.append({
                "category": category,
                "percentage": percentage * 100,
                "amount": amount
            })
        
        # 创建锁仓释放计划（示例）
        vesting_schedule = []
        if "team" in allocation:
            team_amount = int(total_supply * allocation["team"])
            # 团队代币分4年释放
            for year in range(1, 5):
                release_date = datetime.now().replace(year=datetime.now().year + year)
                vesting_schedule.append({
                    "date": release_date.isoformat(),
                    "amount": team_amount // 4,
                    "percentage": allocation["team"] * 100 / 4,
                    "category": "team"
                })
        
        return DistributionSchedule(
            token_address=contract_address,
            distributions=distributions,
            vesting_schedule=vesting_schedule,
            total_distributed=0,
            remaining=total_supply
        )
    
    def burn_tokens(self, contract_address: str, amount: int) -> str:
        """
        销毁代币
        
        Args:
            contract_address: 合约地址
            amount: 销毁数量
            
        Returns:
            str: 交易哈希
        """
        # 模拟销毁交易
        burn_data = f"burn{contract_address}{amount}{datetime.now()}"
        tx_hash = f"0x{hashlib.sha256(burn_data.encode()).hexdigest()}"
        
        logger.info(f"Burned {amount} tokens from {contract_address}")
        return tx_hash
    
    def pause_contract(self, contract_address: str) -> bool:
        """
        暂停合约
        
        Args:
            contract_address: 合约地址
            
        Returns:
            bool: 是否成功
        """
        contract = self.contracts_cache.get(contract_address)
        
        if contract:
            contract.is_paused = True
            logger.info(f"Contract {contract_address} paused")
            return True
        
        return False
    
    def unpause_contract(self, contract_address: str) -> bool:
        """
        恢复合约
        
        Args:
            contract_address: 合约地址
            
        Returns:
            bool: 是否成功
        """
        contract = self.contracts_cache.get(contract_address)
        
        if contract:
            contract.is_paused = False
            logger.info(f"Contract {contract_address} unpaused")
            return True
        
        return False
    
    def verify_contract(self, contract_address: str, source_code: str,
                       abi: List) -> bool:
        """
        验证合约源代码
        
        Args:
            contract_address: 合约地址
            source_code: 源代码
            abi: 合约ABI
            
        Returns:
            bool: 是否验证成功
        """
        contract = self.contracts_cache.get(contract_address)
        
        if contract:
            contract.is_verified = True
            contract.source_code = source_code
            contract.abi = abi
            logger.info(f"Contract {contract_address} verified")
            return True
        
        return False
    
    def get_transaction_history(self, contract_address: str,
                               address: Optional[str] = None,
                               limit: int = 100) -> List[TokenTransaction]:
        """
        获取交易历史
        
        Args:
            contract_address: 合约地址
            address: 可选的地址过滤
            limit: 返回数量限制
            
        Returns:
            List[TokenTransaction]: 交易列表
        """
        # 模拟交易历史
        transactions = []
        
        for i in range(min(limit, 10)):
            tx_hash = f"0x{hashlib.sha256(f'{contract_address}{i}'.encode()).hexdigest()}"
            
            transaction = TokenTransaction(
                tx_hash=tx_hash,
                from_address="0x" + "1" * 40,
                to_address="0x" + "2" * 40,
                amount=100.0 * (i + 1),
                transaction_type="transfer",
                block_number=12345678 + i,
                timestamp=datetime.now(),
                gas_used=21000,
                gas_price=30.5,
                token_price_usd=100.0,
                transaction_value_usd=10000.0 * (i + 1),
                status="confirmed",
                confirmations=12 + i
            )
            
            transactions.append(transaction)
        
        return transactions


# 创建全局服务实例
tokenization_service = TokenizationService()
