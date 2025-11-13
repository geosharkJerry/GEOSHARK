import React, { useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  TextField,
  Button,
  MenuItem,
  Card,
  CardContent,
  Divider,
  Alert,
} from '@mui/material';
import { Calculate, TrendingUp } from '@mui/icons-material';
import { valuationAPI } from '../services/api';

const valuationMethods = [
  { value: 'dcf', label: 'DCF折现现金流法' },
  { value: 'market_comparison', label: '市场比较法' },
  { value: 'liquidation', label: '清算价值法' },
  { value: 'income', label: '收益法' },
];

function ValuationPage() {
  const [method, setMethod] = useState('dcf');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  // DCF参数
  const [dcfParams, setDcfParams] = useState({
    projected_cash_flows: '100000, 120000, 150000, 180000, 200000',
    discount_rate: '0.08',
    terminal_growth_rate: '0.02',
  });

  // 清算价值法参数
  const [liquidationParams, setLiquidationParams] = useState({
    asset_book_value: '5000000',
    liquidation_type: 'orderly',
    discount_rate: '0.3',
    time_to_liquidate: '6',
    liquidation_costs: '100000',
  });

  // 收益法参数
  const [incomeParams, setIncomeParams] = useState({
    annual_income: '1000000',
    capitalization_rate: '0.08',
    vacancy_rate: '0.1',
    operating_expenses_ratio: '0.3',
  });

  const handleCalculate = async () => {
    try {
      setLoading(true);
      let response;

      switch (method) {
        case 'dcf':
          const cashFlows = dcfParams.projected_cash_flows
            .split(',')
            .map((cf) => parseFloat(cf.trim()));
          response = await valuationAPI.dcfValuation({
            projected_cash_flows: cashFlows,
            discount_rate: parseFloat(dcfParams.discount_rate),
            terminal_growth_rate: parseFloat(dcfParams.terminal_growth_rate),
          });
          break;

        case 'liquidation':
          response = await valuationAPI.liquidation({
            asset_book_value: parseFloat(liquidationParams.asset_book_value),
            liquidation_type: liquidationParams.liquidation_type,
            discount_rate: parseFloat(liquidationParams.discount_rate),
            time_to_liquidate: parseInt(liquidationParams.time_to_liquidate),
            liquidation_costs: parseFloat(liquidationParams.liquidation_costs),
          });
          break;

        case 'income':
          response = await valuationAPI.income({
            annual_income: parseFloat(incomeParams.annual_income),
            capitalization_rate: parseFloat(incomeParams.capitalization_rate),
            vacancy_rate: parseFloat(incomeParams.vacancy_rate),
            operating_expenses_ratio: parseFloat(incomeParams.operating_expenses_ratio),
          });
          break;

        default:
          alert('暂不支持该估值方法');
          return;
      }

      setResult(response.data);
    } catch (error) {
      console.error('估值计算失败:', error);
      alert('估值计算失败: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const renderParameterForm = () => {
    switch (method) {
      case 'dcf':
        return (
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="预测现金流（逗号分隔）"
                value={dcfParams.projected_cash_flows}
                onChange={(e) =>
                  setDcfParams({ ...dcfParams, projected_cash_flows: e.target.value })
                }
                helperText="例如: 100000, 120000, 150000, 180000, 200000"
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                type="number"
                label="折现率"
                value={dcfParams.discount_rate}
                onChange={(e) => setDcfParams({ ...dcfParams, discount_rate: e.target.value })}
                helperText="例如: 0.08 表示 8%"
                inputProps={{ step: '0.01' }}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                type="number"
                label="永续增长率"
                value={dcfParams.terminal_growth_rate}
                onChange={(e) =>
                  setDcfParams({ ...dcfParams, terminal_growth_rate: e.target.value })
                }
                helperText="例如: 0.02 表示 2%"
                inputProps={{ step: '0.01' }}
              />
            </Grid>
          </Grid>
        );

      case 'liquidation':
        return (
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                type="number"
                label="资产账面价值（元）"
                value={liquidationParams.asset_book_value}
                onChange={(e) =>
                  setLiquidationParams({ ...liquidationParams, asset_book_value: e.target.value })
                }
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                select
                label="清算类型"
                value={liquidationParams.liquidation_type}
                onChange={(e) =>
                  setLiquidationParams({ ...liquidationParams, liquidation_type: e.target.value })
                }
              >
                <MenuItem value="orderly">有序清算</MenuItem>
                <MenuItem value="forced">强制清算</MenuItem>
              </TextField>
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField
                fullWidth
                type="number"
                label="清算折扣率"
                value={liquidationParams.discount_rate}
                onChange={(e) =>
                  setLiquidationParams({ ...liquidationParams, discount_rate: e.target.value })
                }
                inputProps={{ step: '0.01' }}
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField
                fullWidth
                type="number"
                label="清算时间（月）"
                value={liquidationParams.time_to_liquidate}
                onChange={(e) =>
                  setLiquidationParams({
                    ...liquidationParams,
                    time_to_liquidate: e.target.value,
                  })
                }
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField
                fullWidth
                type="number"
                label="清算费用（元）"
                value={liquidationParams.liquidation_costs}
                onChange={(e) =>
                  setLiquidationParams({
                    ...liquidationParams,
                    liquidation_costs: e.target.value,
                  })
                }
              />
            </Grid>
          </Grid>
        );

      case 'income':
        return (
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                type="number"
                label="年收益（元）"
                value={incomeParams.annual_income}
                onChange={(e) =>
                  setIncomeParams({ ...incomeParams, annual_income: e.target.value })
                }
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                type="number"
                label="资本化率"
                value={incomeParams.capitalization_rate}
                onChange={(e) =>
                  setIncomeParams({ ...incomeParams, capitalization_rate: e.target.value })
                }
                inputProps={{ step: '0.01' }}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                type="number"
                label="空置率"
                value={incomeParams.vacancy_rate}
                onChange={(e) =>
                  setIncomeParams({ ...incomeParams, vacancy_rate: e.target.value })
                }
                inputProps={{ step: '0.01' }}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                type="number"
                label="运营费用率"
                value={incomeParams.operating_expenses_ratio}
                onChange={(e) =>
                  setIncomeParams({
                    ...incomeParams,
                    operating_expenses_ratio: e.target.value,
                  })
                }
                inputProps={{ step: '0.01' }}
              />
            </Grid>
          </Grid>
        );

      default:
        return <Alert severity="info">请选择估值方法</Alert>;
    }
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('zh-CN', {
      style: 'currency',
      currency: 'CNY',
      minimumFractionDigits: 2,
    }).format(value);
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        资产估值
      </Typography>

      <Grid container spacing={3}>
        {/* 估值参数输入 */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              估值参数
            </Typography>
            <Divider sx={{ mb: 3 }} />

            <Grid container spacing={2}>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  select
                  label="估值方法"
                  value={method}
                  onChange={(e) => setMethod(e.target.value)}
                >
                  {valuationMethods.map((option) => (
                    <MenuItem key={option.value} value={option.value}>
                      {option.label}
                    </MenuItem>
                  ))}
                </TextField>
              </Grid>
            </Grid>

            <Box sx={{ mt: 3 }}>{renderParameterForm()}</Box>

            <Button
              fullWidth
              variant="contained"
              startIcon={<Calculate />}
              onClick={handleCalculate}
              disabled={loading}
              sx={{ mt: 3 }}
            >
              {loading ? '计算中...' : '计算估值'}
            </Button>
          </Paper>
        </Grid>

        {/* 估值结果 */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              估值结果
            </Typography>
            <Divider sx={{ mb: 3 }} />

            {result ? (
              <Box>
                <Card sx={{ mb: 2, bgcolor: '#f5f5f5' }}>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                      <TrendingUp color="primary" sx={{ mr: 1 }} />
                      <Typography variant="subtitle2" color="textSecondary">
                        估值结果
                      </Typography>
                    </Box>
                    <Typography variant="h4" color="primary">
                      {formatCurrency(result.estimated_value)}
                    </Typography>
                    <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                      置信度: {(result.confidence_level * 100).toFixed(0)}%
                    </Typography>
                  </CardContent>
                </Card>

                <Typography variant="subtitle2" gutterBottom>
                  价值区间
                </Typography>
                <Typography variant="body2" paragraph>
                  {formatCurrency(result.value_range[0])} - {formatCurrency(result.value_range[1])}
                </Typography>

                {result.breakdown && (
                  <>
                    <Typography variant="subtitle2" gutterBottom>
                      估值明细
                    </Typography>
                    <Box sx={{ bgcolor: '#fafafa', p: 2, borderRadius: 1 }}>
                      <pre style={{ margin: 0, fontSize: '0.875rem', overflowX: 'auto' }}>
                        {JSON.stringify(result.breakdown, null, 2)}
                      </pre>
                    </Box>
                  </>
                )}
              </Box>
            ) : (
              <Alert severity="info">输入参数后点击"计算估值"查看结果</Alert>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}

export default ValuationPage;
