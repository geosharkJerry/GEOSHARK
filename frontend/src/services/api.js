/**
 * API服务模块
 * 封装后端API调用
 */

import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 资产管理API
export const assetAPI = {
  // 创建资产
  createAsset: (assetData) => api.post('/api/assets', assetData),
  
  // 获取单个资产
  getAsset: (assetId) => api.get(`/api/assets/${assetId}`),
  
  // 更新资产
  updateAsset: (assetId, updates) => api.put(`/api/assets/${assetId}`, updates),
  
  // 删除资产
  deleteAsset: (assetId) => api.delete(`/api/assets/${assetId}`),
  
  // 列出资产
  listAssets: (params = {}) => api.get('/api/assets', { params }),
  
  // 搜索资产
  searchAssets: (keyword) => api.get('/api/assets/search', { params: { q: keyword } }),
  
  // 获取统计信息
  getStatistics: () => api.get('/api/assets/statistics'),
  
  // 创建示例数据
  createSampleAssets: () => api.post('/api/demo/create-sample-assets'),
};

// 估值API
export const valuationAPI = {
  // DCF估值
  dcfValuation: (params) => api.post('/api/valuation/dcf', params),
  
  // 市场比较法估值
  marketComparison: (params) => api.post('/api/valuation/market-comparison', params),
  
  // 清算价值法估值
  liquidation: (params) => api.post('/api/valuation/liquidation', params),
  
  // 收益法估值
  income: (params) => api.post('/api/valuation/income', params),
  
  // 估算资产价值
  estimateAsset: (assetId, method, parameters) =>
    api.post('/api/valuation/estimate', { asset_id: assetId, method, parameters }),
};

// 风险评估API
export const riskAPI = {
  // 计算信用评分
  calculateCreditScore: (factors) => api.post('/api/risk/credit-score', factors),
  
  // 综合风险评估
  assessRisk: (assetId, data) =>
    api.post('/api/risk/assess', {
      asset_id: assetId,
      credit_factors: data.creditFactors,
      overdue_days: data.overdueDays || 0,
      collateral_value: data.collateralValue || 0,
      volatility: data.volatility || 0.2,
    }),
};

// 交易API
export const transactionAPI = {
  // 记录交易
  recordTransaction: (transactionData) => api.post('/api/transactions', transactionData),
  
  // 获取资产交易历史
  getAssetTransactions: (assetId) => api.get(`/api/transactions/${assetId}`),
};

// 资产池API
export const poolAPI = {
  // 创建资产池
  createPool: (poolData) => api.post('/api/pools', poolData),
  
  // 获取资产池
  getPool: (poolId) => api.get(`/api/pools/${poolId}`),
  
  // 列出资产池
  listPools: () => api.get('/api/pools'),
};

// 健康检查
export const healthCheck = () => api.get('/health');

export default api;
