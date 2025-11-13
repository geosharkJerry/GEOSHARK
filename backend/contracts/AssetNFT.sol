// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721Burnable.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/Pausable.sol";

/**
 * @title AssetNFT
 * @dev NFT合约用于低效资产代币化
 * 每个NFT代表一个独特的真实世界资产
 */
contract AssetNFT is ERC721, ERC721URIStorage, ERC721Burnable, Ownable, Pausable {
    // 代币计数器
    uint256 private _tokenIdCounter;
    
    // 资产信息结构
    struct AssetInfo {
        string assetId;           // 资产ID
        string assetType;         // 资产类型
        uint256 originalValue;    // 原始价值（以wei为单位）
        uint256 currentValue;     // 当前估值
        uint256 mintedAt;         // 铸造时间
        bool isActive;            // 是否活跃
    }
    
    // tokenId => AssetInfo
    mapping(uint256 => AssetInfo) public assetInfo;
    
    // 资产ID => tokenId（确保一个资产只能铸造一次）
    mapping(string => uint256) public assetIdToTokenId;
    
    // 白名单功能
    mapping(address => bool) public whitelist;
    bool public whitelistEnabled;
    
    // 事件
    event AssetMinted(uint256 indexed tokenId, string assetId, address owner, uint256 value);
    event AssetValueUpdated(uint256 indexed tokenId, uint256 oldValue, uint256 newValue);
    event AssetDeactivated(uint256 indexed tokenId);
    event WhitelistUpdated(address indexed account, bool status);
    
    constructor() ERC721("RWA Asset NFT", "RWANFT") {
        _tokenIdCounter = 1;
        whitelistEnabled = false;
    }
    
    /**
     * @dev 铸造新的资产NFT
     * @param to 接收者地址
     * @param assetId 资产ID
     * @param assetType 资产类型
     * @param originalValue 原始价值
     * @param currentValue 当前估值
     * @param uri 元数据URI
     */
    function mintAsset(
        address to,
        string memory assetId,
        string memory assetType,
        uint256 originalValue,
        uint256 currentValue,
        string memory uri
    ) public onlyOwner whenNotPaused returns (uint256) {
        require(bytes(assetId).length > 0, "Asset ID cannot be empty");
        require(assetIdToTokenId[assetId] == 0, "Asset already tokenized");
        require(originalValue > 0, "Value must be greater than 0");
        
        uint256 tokenId = _tokenIdCounter;
        _tokenIdCounter++;
        
        _safeMint(to, tokenId);
        _setTokenURI(tokenId, uri);
        
        // 记录资产信息
        assetInfo[tokenId] = AssetInfo({
            assetId: assetId,
            assetType: assetType,
            originalValue: originalValue,
            currentValue: currentValue,
            mintedAt: block.timestamp,
            isActive: true
        });
        
        assetIdToTokenId[assetId] = tokenId;
        
        emit AssetMinted(tokenId, assetId, to, currentValue);
        
        return tokenId;
    }
    
    /**
     * @dev 批量铸造资产NFT
     */
    function batchMintAssets(
        address[] memory recipients,
        string[] memory assetIds,
        string[] memory assetTypes,
        uint256[] memory originalValues,
        uint256[] memory currentValues,
        string[] memory uris
    ) public onlyOwner whenNotPaused {
        require(
            recipients.length == assetIds.length &&
            assetIds.length == assetTypes.length &&
            assetTypes.length == originalValues.length &&
            originalValues.length == currentValues.length &&
            currentValues.length == uris.length,
            "Array lengths must match"
        );
        
        for (uint256 i = 0; i < recipients.length; i++) {
            mintAsset(
                recipients[i],
                assetIds[i],
                assetTypes[i],
                originalValues[i],
                currentValues[i],
                uris[i]
            );
        }
    }
    
    /**
     * @dev 更新资产估值
     */
    function updateAssetValue(uint256 tokenId, uint256 newValue) 
        public 
        onlyOwner 
    {
        require(_exists(tokenId), "Token does not exist");
        require(newValue > 0, "Value must be greater than 0");
        
        uint256 oldValue = assetInfo[tokenId].currentValue;
        assetInfo[tokenId].currentValue = newValue;
        
        emit AssetValueUpdated(tokenId, oldValue, newValue);
    }
    
    /**
     * @dev 停用资产
     */
    function deactivateAsset(uint256 tokenId) public onlyOwner {
        require(_exists(tokenId), "Token does not exist");
        require(assetInfo[tokenId].isActive, "Asset already deactivated");
        
        assetInfo[tokenId].isActive = false;
        emit AssetDeactivated(tokenId);
    }
    
    /**
     * @dev 获取资产详细信息
     */
    function getAssetInfo(uint256 tokenId) 
        public 
        view 
        returns (
            string memory assetId,
            string memory assetType,
            uint256 originalValue,
            uint256 currentValue,
            uint256 mintedAt,
            bool isActive
        ) 
    {
        require(_exists(tokenId), "Token does not exist");
        AssetInfo memory info = assetInfo[tokenId];
        return (
            info.assetId,
            info.assetType,
            info.originalValue,
            info.currentValue,
            info.mintedAt,
            info.isActive
        );
    }
    
    /**
     * @dev 通过资产ID获取tokenId
     */
    function getTokenIdByAssetId(string memory assetId) 
        public 
        view 
        returns (uint256) 
    {
        uint256 tokenId = assetIdToTokenId[assetId];
        require(tokenId > 0, "Asset not tokenized");
        return tokenId;
    }
    
    /**
     * @dev 启用/禁用白名单
     */
    function setWhitelistEnabled(bool enabled) public onlyOwner {
        whitelistEnabled = enabled;
    }
    
    /**
     * @dev 添加/移除白名单地址
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
     * @dev 重写转账函数以支持白名单
     */
    function _beforeTokenTransfer(
        address from,
        address to,
        uint256 tokenId,
        uint256 batchSize
    ) internal override whenNotPaused {
        super._beforeTokenTransfer(from, to, tokenId, batchSize);
        
        // 检查白名单（铸造时跳过检查）
        if (whitelistEnabled && from != address(0)) {
            require(whitelist[to], "Recipient not in whitelist");
        }
        
        // 检查资产是否活跃
        if (from != address(0)) {
            require(assetInfo[tokenId].isActive, "Asset is not active");
        }
    }
    
    // 以下函数为必需的重写
    function _burn(uint256 tokenId) internal override(ERC721, ERC721URIStorage) {
        super._burn(tokenId);
    }
    
    function tokenURI(uint256 tokenId)
        public
        view
        override(ERC721, ERC721URIStorage)
        returns (string memory)
    {
        return super.tokenURI(tokenId);
    }
    
    function supportsInterface(bytes4 interfaceId)
        public
        view
        override(ERC721, ERC721URIStorage)
        returns (bool)
    {
        return super.supportsInterface(interfaceId);
    }
    
    /**
     * @dev 获取下一个tokenId
     */
    function nextTokenId() public view returns (uint256) {
        return _tokenIdCounter;
    }
    
    /**
     * @dev 获取总铸造数量
     */
    function totalMinted() public view returns (uint256) {
        return _tokenIdCounter - 1;
    }
}
