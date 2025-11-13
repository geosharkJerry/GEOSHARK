"""
资产管理服务
提供资产CRUD、查询、统计等功能
"""

from typing import List, Optional, Dict
from datetime import datetime
import uuid
import json
from pathlib import Path

from backend.models.asset import (
    Asset, AssetType, AssetStatus, RiskLevel,
    RealEstateAsset, NPLAsset, InventoryAsset, ReceivablesAsset,
    AssetValuation, AssetTransaction, AssetPool
)


class AssetService:
    """资产服务类"""
    
    def __init__(self, data_dir: str = "data"):
        """初始化服务"""
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.assets_file = self.data_dir / "assets.json"
        self.transactions_file = self.data_dir / "transactions.json"
        self.pools_file = self.data_dir / "asset_pools.json"
        
        # 确保数据文件存在
        self._init_data_files()
    
    def _init_data_files(self):
        """初始化数据文件"""
        if not self.assets_file.exists():
            self.assets_file.write_text("[]")
        if not self.transactions_file.exists():
            self.transactions_file.write_text("[]")
        if not self.pools_file.exists():
            self.pools_file.write_text("[]")
    
    def _load_assets(self) -> List[Dict]:
        """加载所有资产"""
        return json.loads(self.assets_file.read_text())
    
    def _save_assets(self, assets: List[Dict]):
        """保存资产"""
        self.assets_file.write_text(json.dumps(assets, indent=2, default=str))
    
    def _load_transactions(self) -> List[Dict]:
        """加载交易记录"""
        return json.loads(self.transactions_file.read_text())
    
    def _save_transactions(self, transactions: List[Dict]):
        """保存交易记录"""
        self.transactions_file.write_text(json.dumps(transactions, indent=2, default=str))
    
    def _load_pools(self) -> List[Dict]:
        """加载资产池"""
        return json.loads(self.pools_file.read_text())
    
    def _save_pools(self, pools: List[Dict]):
        """保存资产池"""
        self.pools_file.write_text(json.dumps(pools, indent=2, default=str))
    
    def create_asset(self, asset: Asset) -> Asset:
        """
        创建新资产
        
        Args:
            asset: 资产对象
            
        Returns:
            创建后的资产（包含ID）
        """
        assets = self._load_assets()
        
        # 生成唯一ID
        asset.id = f"asset_{uuid.uuid4().hex[:12]}"
        asset.created_at = datetime.now()
        asset.updated_at = datetime.now()
        
        # 添加到列表
        assets.append(asset.dict())
        self._save_assets(assets)
        
        return asset
    
    def get_asset(self, asset_id: str) -> Optional[Asset]:
        """
        获取单个资产
        
        Args:
            asset_id: 资产ID
            
        Returns:
            资产对象或None
        """
        assets = self._load_assets()
        for asset_data in assets:
            if asset_data.get("id") == asset_id:
                return Asset(**asset_data)
        return None
    
    def update_asset(self, asset_id: str, updates: Dict) -> Optional[Asset]:
        """
        更新资产信息
        
        Args:
            asset_id: 资产ID
            updates: 更新字段
            
        Returns:
            更新后的资产或None
        """
        assets = self._load_assets()
        
        for i, asset_data in enumerate(assets):
            if asset_data.get("id") == asset_id:
                # 更新字段
                asset_data.update(updates)
                asset_data["updated_at"] = datetime.now().isoformat()
                assets[i] = asset_data
                self._save_assets(assets)
                return Asset(**asset_data)
        
        return None
    
    def delete_asset(self, asset_id: str) -> bool:
        """
        删除资产
        
        Args:
            asset_id: 资产ID
            
        Returns:
            是否删除成功
        """
        assets = self._load_assets()
        original_count = len(assets)
        assets = [a for a in assets if a.get("id") != asset_id]
        
        if len(assets) < original_count:
            self._save_assets(assets)
            return True
        return False
    
    def list_assets(
        self,
        asset_type: Optional[AssetType] = None,
        status: Optional[AssetStatus] = None,
        risk_level: Optional[RiskLevel] = None,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Asset]:
        """
        列出资产（支持筛选）
        
        Args:
            asset_type: 资产类型筛选
            status: 状态筛选
            risk_level: 风险等级筛选
            min_value: 最小价值
            max_value: 最大价值
            limit: 返回数量限制
            offset: 偏移量
            
        Returns:
            资产列表
        """
        assets = self._load_assets()
        
        # 筛选
        filtered = []
        for asset_data in assets:
            # 类型筛选
            if asset_type and asset_data.get("asset_type") != asset_type.value:
                continue
            
            # 状态筛选
            if status and asset_data.get("status") != status.value:
                continue
            
            # 风险等级筛选
            if risk_level and asset_data.get("risk_level") != risk_level.value:
                continue
            
            # 价值范围筛选
            current_value = asset_data.get("current_value") or asset_data.get("original_value", 0)
            if min_value is not None and current_value < min_value:
                continue
            if max_value is not None and current_value > max_value:
                continue
            
            filtered.append(Asset(**asset_data))
        
        # 分页
        return filtered[offset:offset + limit]
    
    def search_assets(self, keyword: str) -> List[Asset]:
        """
        搜索资产
        
        Args:
            keyword: 搜索关键词
            
        Returns:
            匹配的资产列表
        """
        assets = self._load_assets()
        keyword_lower = keyword.lower()
        
        results = []
        for asset_data in assets:
            # 在名称和描述中搜索
            if (keyword_lower in asset_data.get("name", "").lower() or
                keyword_lower in asset_data.get("description", "").lower() or
                keyword_lower in asset_data.get("location", "").lower()):
                results.append(Asset(**asset_data))
        
        return results
    
    def get_statistics(self) -> Dict:
        """
        获取资产统计信息
        
        Returns:
            统计数据字典
        """
        assets = self._load_assets()
        
        stats = {
            "total_count": len(assets),
            "total_value": 0,
            "by_type": {},
            "by_status": {},
            "by_risk_level": {},
            "tokenized_count": 0,
            "average_value": 0
        }
        
        for asset_data in assets:
            # 累计价值
            value = asset_data.get("current_value") or asset_data.get("original_value", 0)
            stats["total_value"] += value
            
            # 按类型统计
            asset_type = asset_data.get("asset_type", "unknown")
            stats["by_type"][asset_type] = stats["by_type"].get(asset_type, 0) + 1
            
            # 按状态统计
            status = asset_data.get("status", "unknown")
            stats["by_status"][status] = stats["by_status"].get(status, 0) + 1
            
            # 按风险等级统计
            risk_level = asset_data.get("risk_level")
            if risk_level:
                stats["by_risk_level"][risk_level] = stats["by_risk_level"].get(risk_level, 0) + 1
            
            # 代币化统计
            if asset_data.get("is_tokenized"):
                stats["tokenized_count"] += 1
        
        # 平均价值
        if stats["total_count"] > 0:
            stats["average_value"] = stats["total_value"] / stats["total_count"]
        
        return stats
    
    def record_transaction(self, transaction: AssetTransaction) -> AssetTransaction:
        """
        记录资产交易
        
        Args:
            transaction: 交易对象
            
        Returns:
            记录后的交易
        """
        transactions = self._load_transactions()
        
        # 生成ID
        transaction.id = f"tx_{uuid.uuid4().hex[:12]}"
        transaction.transaction_date = datetime.now()
        
        transactions.append(transaction.dict())
        self._save_transactions(transactions)
        
        return transaction
    
    def get_asset_transactions(self, asset_id: str) -> List[AssetTransaction]:
        """
        获取资产的交易历史
        
        Args:
            asset_id: 资产ID
            
        Returns:
            交易记录列表
        """
        transactions = self._load_transactions()
        return [
            AssetTransaction(**tx)
            for tx in transactions
            if tx.get("asset_id") == asset_id
        ]
    
    def create_asset_pool(self, pool: AssetPool) -> AssetPool:
        """
        创建资产池/资产包
        
        Args:
            pool: 资产池对象
            
        Returns:
            创建后的资产池
        """
        pools = self._load_pools()
        
        pool.id = f"pool_{uuid.uuid4().hex[:12]}"
        pool.created_at = datetime.now()
        
        # 计算总价值
        total_value = 0
        for asset_id in pool.asset_ids:
            asset = self.get_asset(asset_id)
            if asset:
                value = asset.current_value or asset.original_value
                total_value += value
        pool.total_value = total_value
        
        pools.append(pool.dict())
        self._save_pools(pools)
        
        return pool
    
    def get_asset_pool(self, pool_id: str) -> Optional[AssetPool]:
        """获取资产池"""
        pools = self._load_pools()
        for pool_data in pools:
            if pool_data.get("id") == pool_id:
                return AssetPool(**pool_data)
        return None
    
    def list_asset_pools(self) -> List[AssetPool]:
        """列出所有资产池"""
        pools = self._load_pools()
        return [AssetPool(**p) for p in pools]


# 示例使用
if __name__ == "__main__":
    service = AssetService(data_dir="/home/user/webapp/data")
    
    # 创建示例不良贷款资产
    npl_asset = NPLAsset(
        name="某企业不良贷款",
        original_value=5000000,
        description="某中小企业经营贷款，逾期6个月",
        location="上海市",
        loan_amount=5000000,
        outstanding_balance=5200000,
        interest_rate=0.065,
        overdue_days=180,
        borrower_info={"name": "某某科技有限公司"},
        collateral_info={"type": "real_estate", "value": 3000000}
    )
    
    created = service.create_asset(npl_asset)
    print(f"创建资产: {created.id}")
    
    # 获取统计
    stats = service.get_statistics()
    print(f"资产统计: {stats}")
