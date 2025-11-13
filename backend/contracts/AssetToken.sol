// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Burnable.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Snapshot.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/Pausable.sol";

/**
 * @title AssetToken
 * @dev ERC-20代币合约用于资产份额化
 * 将大额资产分割为可交易的代币份额
 */
contract AssetToken is ERC20, ERC20Burnable, ERC20Snapshot, Ownable, Pausable {
    // 资产信息
    struct AssetDetails {
        string assetId;           // 资产ID
        string assetType;         // 资产类型
        uint256 totalAssetValue;  // 资产总价值
        uint256 createdAt;        // 创建时间
        bool isActive;            // 是否活跃
    }
    
    AssetDetails public assetDetails;
    
    // 白名单功能
    mapping(address => bool) public whitelist;
    bool public whitelistEnabled;
    
    // 转账限制
    uint256 public minTransferAmount;
    uint256 public maxTransferAmount;
    bool public transferRestricted;
    
    // 收益分配
    mapping(address => uint256) public dividends;
    uint256 public totalDividends;
    
    // 锁定代币
    struct LockedTokens {
        uint256 amount;
        uint256 unlockTime;
    }
    mapping(address => LockedTokens[]) public lockedTokens;
    
    // 事件
    event AssetValueUpdated(uint256 oldValue, uint256 newValue);
    event DividendDistributed(uint256 totalAmount, uint256 timestamp);
    event DividendClaimed(address indexed account, uint256 amount);
    event TokensLocked(address indexed account, uint256 amount, uint256 unlockTime);
    event TokensUnlocked(address indexed account, uint256 amount);
    event WhitelistUpdated(address indexed account, bool status);
    event TransferRestrictionUpdated(bool restricted, uint256 minAmount, uint256 maxAmount);
    
    /**
     * @dev 构造函数
     * @param name 代币名称
     * @param symbol 代币符号
     * @param initialSupply 初始供应量
     * @param assetId 资产ID
     * @param assetType 资产类型
     * @param assetValue 资产价值
     */
    constructor(
        string memory name,
        string memory symbol,
        uint256 initialSupply,
        string memory assetId,
        string memory assetType,
        uint256 assetValue
    ) ERC20(name, symbol) {
        require(initialSupply > 0, "Initial supply must be greater than 0");
        require(assetValue > 0, "Asset value must be greater than 0");
        require(bytes(assetId).length > 0, "Asset ID cannot be empty");
        
        _mint(msg.sender, initialSupply);
        
        assetDetails = AssetDetails({
            assetId: assetId,
            assetType: assetType,
            totalAssetValue: assetValue,
            createdAt: block.timestamp,
            isActive: true
        });
        
        whitelistEnabled = false;
        transferRestricted = false;
        minTransferAmount = 0;
        maxTransferAmount = initialSupply;
    }
    
    /**
     * @dev 更新资产价值
     */
    function updateAssetValue(uint256 newValue) public onlyOwner {
        require(newValue > 0, "Value must be greater than 0");
        uint256 oldValue = assetDetails.totalAssetValue;
        assetDetails.totalAssetValue = newValue;
        emit AssetValueUpdated(oldValue, newValue);
    }
    
    /**
     * @dev 停用资产
     */
    function deactivateAsset() public onlyOwner {
        require(assetDetails.isActive, "Asset already deactivated");
        assetDetails.isActive = false;
    }
    
    /**
     * @dev 激活资产
     */
    function activateAsset() public onlyOwner {
        require(!assetDetails.isActive, "Asset already active");
        assetDetails.isActive = true;
    }
    
    /**
     * @dev 计算代币价格（每个代币对应的资产价值）
     */
    function tokenPrice() public view returns (uint256) {
        uint256 supply = totalSupply();
        if (supply == 0) return 0;
        return assetDetails.totalAssetValue * 1e18 / supply;
    }
    
    /**
     * @dev 启用/禁用白名单
     */
    function setWhitelistEnabled(bool enabled) public onlyOwner {
        whitelistEnabled = enabled;
    }
    
    /**
     * @dev 更新白名单
     */
    function updateWhitelist(address account, bool status) public onlyOwner {
        whitelist[account] = status;
        emit WhitelistUpdated(account, status);
    }
    
    /**
     * @dev 批量更新白名单
     */
    function batchUpdateWhitelist(address[] memory accounts, bool[] memory statuses) 
        public 
        onlyOwner 
    {
        require(accounts.length == statuses.length, "Array lengths must match");
        for (uint256 i = 0; i < accounts.length; i++) {
            whitelist[accounts[i]] = statuses[i];
            emit WhitelistUpdated(accounts[i], statuses[i]);
        }
    }
    
    /**
     * @dev 设置转账限制
     */
    function setTransferRestriction(
        bool restricted,
        uint256 minAmount,
        uint256 maxAmount
    ) public onlyOwner {
        require(maxAmount >= minAmount, "Max must be >= min");
        transferRestricted = restricted;
        minTransferAmount = minAmount;
        maxTransferAmount = maxAmount;
        emit TransferRestrictionUpdated(restricted, minAmount, maxAmount);
    }
    
    /**
     * @dev 锁定代币
     */
    function lockTokens(address account, uint256 amount, uint256 unlockTime) 
        public 
        onlyOwner 
    {
        require(unlockTime > block.timestamp, "Unlock time must be in future");
        require(balanceOf(account) >= amount, "Insufficient balance");
        
        lockedTokens[account].push(LockedTokens({
            amount: amount,
            unlockTime: unlockTime
        }));
        
        emit TokensLocked(account, amount, unlockTime);
    }
    
    /**
     * @dev 获取可用余额（扣除锁定部分）
     */
    function availableBalance(address account) public view returns (uint256) {
        uint256 total = balanceOf(account);
        uint256 locked = getLockedAmount(account);
        return total > locked ? total - locked : 0;
    }
    
    /**
     * @dev 获取锁定数量
     */
    function getLockedAmount(address account) public view returns (uint256) {
        uint256 locked = 0;
        LockedTokens[] memory locks = lockedTokens[account];
        
        for (uint256 i = 0; i < locks.length; i++) {
            if (locks[i].unlockTime > block.timestamp) {
                locked += locks[i].amount;
            }
        }
        
        return locked;
    }
    
    /**
     * @dev 解锁已到期的代币
     */
    function unlockExpiredTokens(address account) public {
        LockedTokens[] storage locks = lockedTokens[account];
        uint256 unlocked = 0;
        
        for (uint256 i = 0; i < locks.length; ) {
            if (locks[i].unlockTime <= block.timestamp) {
                unlocked += locks[i].amount;
                // 移除已解锁的记录
                locks[i] = locks[locks.length - 1];
                locks.pop();
            } else {
                i++;
            }
        }
        
        if (unlocked > 0) {
            emit TokensUnlocked(account, unlocked);
        }
    }
    
    /**
     * @dev 分配收益
     */
    function distributeDividends() public payable onlyOwner {
        require(msg.value > 0, "Dividend amount must be greater than 0");
        totalDividends += msg.value;
        emit DividendDistributed(msg.value, block.timestamp);
    }
    
    /**
     * @dev 计算账户应得收益
     */
    function calculateDividend(address account) public view returns (uint256) {
        uint256 supply = totalSupply();
        if (supply == 0) return 0;
        
        uint256 balance = balanceOf(account);
        return totalDividends * balance / supply;
    }
    
    /**
     * @dev 领取收益
     */
    function claimDividend() public {
        uint256 amount = calculateDividend(msg.sender);
        require(amount > 0, "No dividend to claim");
        require(amount > dividends[msg.sender], "Dividend already claimed");
        
        uint256 claimable = amount - dividends[msg.sender];
        require(address(this).balance >= claimable, "Insufficient contract balance");
        
        dividends[msg.sender] = amount;
        payable(msg.sender).transfer(claimable);
        
        emit DividendClaimed(msg.sender, claimable);
    }
    
    /**
     * @dev 创建快照
     */
    function snapshot() public onlyOwner returns (uint256) {
        return _snapshot();
    }
    
    /**
     * @dev 暂停合约
     */
    function pause() public onlyOwner {
        _pause();
    }
    
    /**
     * @dev 恢复合约
     */
    function unpause() public onlyOwner {
        _unpause();
    }
    
    /**
     * @dev 铸造新代币（仅限owner）
     */
    function mint(address to, uint256 amount) public onlyOwner {
        _mint(to, amount);
    }
    
    /**
     * @dev 重写转账前检查
     */
    function _beforeTokenTransfer(
        address from,
        address to,
        uint256 amount
    ) internal override(ERC20, ERC20Snapshot) whenNotPaused {
        super._beforeTokenTransfer(from, to, amount);
        
        // 铸造和销毁时跳过检查
        if (from == address(0) || to == address(0)) {
            return;
        }
        
        // 检查资产是否活跃
        require(assetDetails.isActive, "Asset is not active");
        
        // 白名单检查
        if (whitelistEnabled) {
            require(whitelist[from] && whitelist[to], "Address not in whitelist");
        }
        
        // 转账金额限制
        if (transferRestricted) {
            require(amount >= minTransferAmount, "Amount below minimum");
            require(amount <= maxTransferAmount, "Amount above maximum");
        }
        
        // 检查可用余额（扣除锁定部分）
        require(availableBalance(from) >= amount, "Insufficient available balance");
    }
    
    /**
     * @dev 获取资产详情
     */
    function getAssetDetails() public view returns (
        string memory assetId,
        string memory assetType,
        uint256 totalAssetValue,
        uint256 createdAt,
        bool isActive
    ) {
        return (
            assetDetails.assetId,
            assetDetails.assetType,
            assetDetails.totalAssetValue,
            assetDetails.createdAt,
            assetDetails.isActive
        );
    }
    
    /**
     * @dev 接收ETH
     */
    receive() external payable {
        // 允许合约接收ETH（用于收益分配）
    }
}
