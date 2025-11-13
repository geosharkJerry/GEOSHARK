import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  Grid,
  CircularProgress,
} from '@mui/material';
import { Add, Edit, Delete, Refresh } from '@mui/icons-material';
import { assetAPI } from '../services/api';

const assetTypeLabels = {
  npl: '不良贷款',
  real_estate: '房地产',
  inventory: '库存资产',
  collateral: '抵押资产',
  receivables: '应收账款',
  equipment: '设备资产',
  others: '其他',
};

const statusLabels = {
  idle: '闲置',
  distressed: '困境',
  liquidating: '清算中',
  tokenized: '已代币化',
  sold: '已出售',
  restructuring: '重组中',
};

const riskLevelColors = {
  A: 'success',
  B: 'info',
  C: 'warning',
  D: 'error',
  E: 'error',
};

function AssetsPage() {
  const [assets, setAssets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [openDialog, setOpenDialog] = useState(false);
  const [newAsset, setNewAsset] = useState({
    name: '',
    asset_type: 'npl',
    original_value: 0,
    description: '',
    location: '',
  });

  useEffect(() => {
    loadAssets();
  }, []);

  const loadAssets = async () => {
    try {
      setLoading(true);
      const response = await assetAPI.listAssets();
      setAssets(response.data);
    } catch (error) {
      console.error('加载资产失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateAsset = async () => {
    try {
      await assetAPI.createAsset(newAsset);
      setOpenDialog(false);
      setNewAsset({
        name: '',
        asset_type: 'npl',
        original_value: 0,
        description: '',
        location: '',
      });
      loadAssets();
    } catch (error) {
      console.error('创建资产失败:', error);
      alert('创建资产失败: ' + error.message);
    }
  };

  const handleDeleteAsset = async (assetId) => {
    if (window.confirm('确定要删除此资产吗？')) {
      try {
        await assetAPI.deleteAsset(assetId);
        loadAssets();
      } catch (error) {
        console.error('删除资产失败:', error);
      }
    }
  };

  const handleCreateSample = async () => {
    try {
      await assetAPI.createSampleAssets();
      alert('示例资产创建成功！');
      loadAssets();
    } catch (error) {
      console.error('创建示例资产失败:', error);
    }
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('zh-CN', {
      style: 'currency',
      currency: 'CNY',
      minimumFractionDigits: 0,
    }).format(value);
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">资产管理</Typography>
        <Box>
          <Button
            variant="outlined"
            startIcon={<Add />}
            onClick={handleCreateSample}
            sx={{ mr: 1 }}
          >
            创建示例数据
          </Button>
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={loadAssets}
            sx={{ mr: 1 }}
          >
            刷新
          </Button>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => setOpenDialog(true)}
          >
            创建资产
          </Button>
        </Box>
      </Box>

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
          <CircularProgress />
        </Box>
      ) : assets.length === 0 ? (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <Typography variant="h6" color="textSecondary">
            暂无资产数据
          </Typography>
          <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
            点击"创建示例数据"按钮快速添加示例资产
          </Typography>
        </Paper>
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>资产名称</TableCell>
                <TableCell>类型</TableCell>
                <TableCell>原始价值</TableCell>
                <TableCell>当前估值</TableCell>
                <TableCell>状态</TableCell>
                <TableCell>风险等级</TableCell>
                <TableCell>位置</TableCell>
                <TableCell>操作</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {assets.map((asset) => (
                <TableRow key={asset.id}>
                  <TableCell>{asset.name}</TableCell>
                  <TableCell>{assetTypeLabels[asset.asset_type] || asset.asset_type}</TableCell>
                  <TableCell>{formatCurrency(asset.original_value)}</TableCell>
                  <TableCell>
                    {asset.current_value ? formatCurrency(asset.current_value) : '-'}
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={statusLabels[asset.status] || asset.status}
                      size="small"
                      color="default"
                    />
                  </TableCell>
                  <TableCell>
                    {asset.risk_level ? (
                      <Chip
                        label={asset.risk_level}
                        size="small"
                        color={riskLevelColors[asset.risk_level] || 'default'}
                      />
                    ) : (
                      '-'
                    )}
                  </TableCell>
                  <TableCell>{asset.location || '-'}</TableCell>
                  <TableCell>
                    <IconButton size="small" color="primary">
                      <Edit />
                    </IconButton>
                    <IconButton
                      size="small"
                      color="error"
                      onClick={() => handleDeleteAsset(asset.id)}
                    >
                      <Delete />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {/* 创建资产对话框 */}
      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>创建新资产</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="资产名称"
                value={newAsset.name}
                onChange={(e) => setNewAsset({ ...newAsset, name: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                select
                label="资产类型"
                value={newAsset.asset_type}
                onChange={(e) => setNewAsset({ ...newAsset, asset_type: e.target.value })}
              >
                {Object.entries(assetTypeLabels).map(([value, label]) => (
                  <MenuItem key={value} value={value}>
                    {label}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                type="number"
                label="原始价值（元）"
                value={newAsset.original_value}
                onChange={(e) =>
                  setNewAsset({ ...newAsset, original_value: parseFloat(e.target.value) })
                }
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="位置"
                value={newAsset.location}
                onChange={(e) => setNewAsset({ ...newAsset, location: e.target.value })}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={3}
                label="资产描述"
                value={newAsset.description}
                onChange={(e) => setNewAsset({ ...newAsset, description: e.target.value })}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>取消</Button>
          <Button onClick={handleCreateAsset} variant="contained">
            创建
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default AssetsPage;
