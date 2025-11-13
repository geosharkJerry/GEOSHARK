# RWA低效资产模型系统

## 项目概述

这是一个针对低效资产（Real World Assets - Underperforming/Distressed Assets）的区块链代币化管理系统。系统支持对不良资产、闲置资产、抵押资产等进行评估、代币化和交易管理。

## 核心功能

### 1. 资产类型支持
- **不良贷款资产**：银行不良贷款、信用卡坏账等
- **闲置房产**：长期空置的商业/住宅地产
- **库存资产**：积压库存、滞销商品
- **抵押资产**：待处置的抵押物
- **应收账款**：逾期应收款项

### 2. 估值模型
- **DCF折现现金流法**：基于未来现金流预测
- **市场比较法**：参考类似资产市场价格
- **清算价值法**：快速处置价值评估
- **成本法**：基于重置成本计算
- **AI智能估值**：机器学习辅助估值

### 3. 代币化功能
- 资产NFT铸造（ERC-721）
- 资产份额化代币（ERC-20）
- 智能合约自动化管理
- 链上资产权益证明

### 4. 风险管理
- 多维度信用评分（0-1000分）
- 风险等级分类（A-E级）
- 违约概率计算（PD）
- 损失率预测（LGD）

### 5. 交易管理
- 资产发布与上架
- 竞价交易机制
- 资产包组合
- 收益分配

## 技术栈

### 后端
- **Python 3.9+**
- **FastAPI**：RESTful API框架
- **SQLAlchemy**：ORM数据库
- **Web3.py**：区块链交互
- **Pandas**：数据分析
- **Scikit-learn**：机器学习

### 前端
- **React 18**
- **TypeScript**
- **Material-UI**
- **Web3.js/Ethers.js**
- **Recharts**：数据可视化

### 区块链
- **Solidity**：智能合约
- **Hardhat**：开发框架
- **ERC-721/ERC-20**：代币标准

## 项目结构

```
/home/user/webapp/
├── backend/                 # 后端服务
│   ├── models/             # 数据模型
│   │   ├── asset.py        # 资产模型
│   │   ├── valuation.py    # 估值模型
│   │   ├── risk.py         # 风险模型
│   │   └── token.py        # 代币模型
│   ├── services/           # 业务逻辑
│   │   ├── asset_service.py
│   │   ├── valuation_service.py
│   │   ├── tokenization_service.py
│   │   └── risk_service.py
│   ├── api/                # API路由
│   │   └── routes.py
│   ├── contracts/          # 智能合约
│   │   ├── AssetNFT.sol
│   │   └── AssetToken.sol
│   ├── utils/              # 工具函数
│   └── main.py             # 应用入口
├── frontend/               # 前端应用
│   ├── src/
│   │   ├── components/     # React组件
│   │   ├── pages/          # 页面
│   │   └── services/       # API服务
│   └── public/
├── tests/                  # 测试用例
├── docs/                   # 文档
├── data/                   # 数据文件
└── requirements.txt        # Python依赖
```

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/geosharkJerry/GEOSHARK.git
cd GEOSHARK
```

### 2. 安装依赖

```bash
# 后端依赖
pip install -r requirements.txt

# 前端依赖
cd frontend && npm install
```

### 3. 配置环境

复制 `.env.example` 并重命名为 `.env`：

```bash
cp .env.example .env
```

编辑 `.env` 文件，配置必要的参数：

```env
# 数据库配置
DATABASE_URL=sqlite:///./data/rwa_assets.db

# 区块链配置
BLOCKCHAIN_RPC_URL=http://localhost:8545
BLOCKCHAIN_NETWORK=ethereum
PRIVATE_KEY=your_private_key

# 合约地址（部署后填写）
ASSET_NFT_CONTRACT=0x...
ASSET_TOKEN_CONTRACT=0x...

# API配置
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=true
```

### 4. 启动服务

```bash
# 启动后端API（端口8000）
cd /home/user/webapp
python backend/main.py

# 或使用uvicorn
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

### 5. 访问系统

- **API文档（Swagger）**：http://localhost:8000/docs
- **API文档（ReDoc）**：http://localhost:8000/redoc
- **API根路径**：http://localhost:8000/

## API接口示例

### 创建资产

```bash
POST /api/assets
{
  "name": "某商业地产不良资产包",
  "asset_type": "real_estate",
  "original_value": 50000000,
  "description": "位于一线城市核心商圈的商业物业",
  "location": "北京市朝阳区",
  "area": 5000,
  "status": "idle"
}
```

### 资产估值

```bash
POST /api/valuation/estimate
{
  "asset_id": "asset_123",
  "method": "dcf",
  "parameters": {
    "projected_cash_flows": [1000000, 1200000, 1500000],
    "discount_rate": 0.08
  }
}
```

### 代币化资产

```bash
POST /api/tokenization/mint
{
  "asset_id": "asset_123",
  "token_type": "nft",
  "total_supply": 1,
  "metadata_uri": "ipfs://..."
}
```

## 核心算法

### DCF估值公式

```
PV = Σ(CFt / (1 + r)^t)
其中：
- PV = 现值
- CFt = 第t期现金流
- r = 折现率
- t = 时间期数
```

### 信用评分模型

```python
credit_score = (
    payment_history * 0.35 +
    debt_ratio * 0.30 +
    credit_age * 0.15 +
    credit_mix * 0.10 +
    new_credit * 0.10
) * 1000
```

### 风险等级划分

- **A级（800-1000分）**：优质资产，低风险
- **B级（650-799分）**：良好资产，较低风险
- **C级（500-649分）**：中等资产，中等风险
- **D级（350-499分）**：次级资产，较高风险
- **E级（0-349分）**：不良资产，高风险

## 智能合约

### AssetNFT合约

每个低效资产铸造为唯一的NFT，包含：
- 资产基本信息
- 估值数据
- 权益证明
- 交易历史

### AssetToken合约

将大额资产分割为可交易的ERC-20代币：
- 降低投资门槛
- 提高流动性
- 自动分配收益

## 安全考虑

1. **智能合约审计**：专业审计防止漏洞
2. **权限管理**：多签名控制关键操作
3. **数据加密**：敏感信息加密存储
4. **KYC/AML**：合规身份验证
5. **价格预言机**：防止价格操纵

## 监管合规

- 符合当地资产证券化法规
- 满足数据隐私保护要求（GDPR等）
- 实现投资者适当性管理
- 建立资产托管机制

## 未来规划

- [ ] 接入更多公链（Polygon、BSC等）
- [ ] 集成DeFi协议（借贷、流动性挖矿）
- [ ] AI智能定价优化
- [ ] 跨境资产交易支持
- [ ] 移动端App开发

## 许可证

MIT License

## 联系方式

- 项目维护：RWA Development Team
- Email: contact@rwa-platform.com
- 文档：https://docs.rwa-platform.com

---

**注意**：本系统用于低效资产的数字化管理和交易，使用前请确保符合当地法律法规要求。
