import React, { useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  TextField,
  Button,
  Card,
  CardContent,
  Divider,
  Alert,
  LinearProgress,
  Chip,
} from '@mui/material';
import { Assessment, Warning } from '@mui/icons-material';
import { riskAPI } from '../services/api';

const riskLevelInfo = {
  A: { label: 'A级 - 低风险', color: 'success', range: '800-1000分' },
  B: { label: 'B级 - 较低风险', color: 'info', range: '650-799分' },
  C: { label: 'C级 - 中等风险', color: 'warning', range: '500-649分' },
  D: { label: 'D级 - 较高风险', color: 'error', range: '350-499分' },
  E: { label: 'E级 - 高风险', color: 'error', range: '0-349分' },
};

function RiskPage() {
  const [factors, setFactors] = useState({
    payment_history: 80,
    debt_ratio: 70,
    credit_age: 75,
    credit_mix: 80,
    new_credit: 85,
  });
  
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleCalculate = async () => {
    try {
      setLoading(true);
      const response = await riskAPI.calculateCreditScore(factors);
      setResult(response.data);
    } catch (error) {
      console.error('风险评估失败:', error);
      alert('风险评估失败: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleFactorChange = (factor, value) => {
    const numValue = parseFloat(value);
    if (numValue >= 0 && numValue <= 100) {
      setFactors({ ...factors, [factor]: numValue });
    }
  };

  const getScoreColor = (score) => {
    if (score >= 800) return 'success';
    if (score >= 650) return 'info';
    if (score >= 500) return 'warning';
    return 'error';
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        风险评估
      </Typography>

      <Grid container spacing={3}>
        {/* 评分因子输入 */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              信用评分因子
            </Typography>
            <Divider sx={{ mb: 3 }} />

            <Grid container spacing={3}>
              <Grid item xs={12}>
                <Typography variant="body2" color="textSecondary" gutterBottom>
                  还款历史 (35%权重)
                </Typography>
                <TextField
                  fullWidth
                  type="number"
                  value={factors.payment_history}
                  onChange={(e) => handleFactorChange('payment_history', e.target.value)}
                  inputProps={{ min: 0, max: 100 }}
                  helperText={`当前: ${factors.payment_history}/100`}
                />
                <LinearProgress
                  variant="determinate"
                  value={factors.payment_history}
                  sx={{ mt: 1 }}
                />
              </Grid>

              <Grid item xs={12}>
                <Typography variant="body2" color="textSecondary" gutterBottom>
                  负债比率 (30%权重)
                </Typography>
                <TextField
                  fullWidth
                  type="number"
                  value={factors.debt_ratio}
                  onChange={(e) => handleFactorChange('debt_ratio', e.target.value)}
                  inputProps={{ min: 0, max: 100 }}
                  helperText={`当前: ${factors.debt_ratio}/100`}
                />
                <LinearProgress
                  variant="determinate"
                  value={factors.debt_ratio}
                  sx={{ mt: 1 }}
                />
              </Grid>

              <Grid item xs={12}>
                <Typography variant="body2" color="textSecondary" gutterBottom>
                  信用历史长度 (15%权重)
                </Typography>
                <TextField
                  fullWidth
                  type="number"
                  value={factors.credit_age}
                  onChange={(e) => handleFactorChange('credit_age', e.target.value)}
                  inputProps={{ min: 0, max: 100 }}
                  helperText={`当前: ${factors.credit_age}/100`}
                />
                <LinearProgress
                  variant="determinate"
                  value={factors.credit_age}
                  sx={{ mt: 1 }}
                />
              </Grid>

              <Grid item xs={12}>
                <Typography variant="body2" color="textSecondary" gutterBottom>
                  信用组合 (10%权重)
                </Typography>
                <TextField
                  fullWidth
                  type="number"
                  value={factors.credit_mix}
                  onChange={(e) => handleFactorChange('credit_mix', e.target.value)}
                  inputProps={{ min: 0, max: 100 }}
                  helperText={`当前: ${factors.credit_mix}/100`}
                />
                <LinearProgress
                  variant="determinate"
                  value={factors.credit_mix}
                  sx={{ mt: 1 }}
                />
              </Grid>

              <Grid item xs={12}>
                <Typography variant="body2" color="textSecondary" gutterBottom>
                  新增信用 (10%权重)
                </Typography>
                <TextField
                  fullWidth
                  type="number"
                  value={factors.new_credit}
                  onChange={(e) => handleFactorChange('new_credit', e.target.value)}
                  inputProps={{ min: 0, max: 100 }}
                  helperText={`当前: ${factors.new_credit}/100`}
                />
                <LinearProgress
                  variant="determinate"
                  value={factors.new_credit}
                  sx={{ mt: 1 }}
                />
              </Grid>
            </Grid>

            <Button
              fullWidth
              variant="contained"
              startIcon={<Assessment />}
              onClick={handleCalculate}
              disabled={loading}
              sx={{ mt: 3 }}
            >
              {loading ? '评估中...' : '计算信用评分'}
            </Button>
          </Paper>
        </Grid>

        {/* 评估结果 */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              评估结果
            </Typography>
            <Divider sx={{ mb: 3 }} />

            {result ? (
              <Box>
                {/* 信用评分 */}
                <Card sx={{ mb: 2, bgcolor: '#f5f5f5' }}>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                      <Assessment color="primary" sx={{ mr: 1 }} />
                      <Typography variant="subtitle2" color="textSecondary">
                        信用评分
                      </Typography>
                    </Box>
                    <Typography variant="h3" color={getScoreColor(result.credit_score)}>
                      {result.credit_score}
                    </Typography>
                    <LinearProgress
                      variant="determinate"
                      value={(result.credit_score / 1000) * 100}
                      color={getScoreColor(result.credit_score)}
                      sx={{ mt: 2, height: 8, borderRadius: 4 }}
                    />
                    <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                      满分: 1000分
                    </Typography>
                  </CardContent>
                </Card>

                {/* 风险等级 */}
                <Card sx={{ mb: 2 }}>
                  <CardContent>
                    <Typography variant="subtitle2" gutterBottom>
                      风险等级
                    </Typography>
                    <Chip
                      label={riskLevelInfo[result.risk_level]?.label || result.risk_level}
                      color={riskLevelInfo[result.risk_level]?.color || 'default'}
                      sx={{ fontSize: '1rem', py: 2.5, px: 2 }}
                    />
                    <Typography variant="body2" color="textSecondary" sx={{ mt: 2 }}>
                      分数范围: {riskLevelInfo[result.risk_level]?.range}
                    </Typography>
                  </CardContent>
                </Card>

                {/* 信用评级 */}
                <Card sx={{ mb: 2 }}>
                  <CardContent>
                    <Typography variant="subtitle2" gutterBottom>
                      信用评级
                    </Typography>
                    <Typography variant="h5" color="primary">
                      {result.credit_rating}
                    </Typography>
                  </CardContent>
                </Card>

                {/* 风险等级说明 */}
                <Alert severity="info" icon={<Warning />}>
                  <Typography variant="body2">
                    <strong>风险等级说明：</strong>
                  </Typography>
                  <Box component="ul" sx={{ mt: 1, pl: 2, mb: 0 }}>
                    <li>A级 (800-1000): 优质资产，低风险</li>
                    <li>B级 (650-799): 良好资产，较低风险</li>
                    <li>C级 (500-649): 中等资产，中等风险</li>
                    <li>D级 (350-499): 次级资产，较高风险</li>
                    <li>E级 (0-349): 不良资产，高风险</li>
                  </Box>
                </Alert>
              </Box>
            ) : (
              <Alert severity="info">设置评分因子后点击"计算信用评分"查看结果</Alert>
            )}
          </Paper>

          {/* 评分模型说明 */}
          <Paper sx={{ p: 3, mt: 3 }}>
            <Typography variant="h6" gutterBottom>
              评分模型说明
            </Typography>
            <Divider sx={{ mb: 2 }} />
            <Typography variant="body2" paragraph>
              信用评分采用多维度加权模型计算：
            </Typography>
            <Box component="ul" sx={{ pl: 2 }}>
              <li>
                <Typography variant="body2">
                  <strong>还款历史 (35%)</strong>: 历史还款记录和违约情况
                </Typography>
              </li>
              <li>
                <Typography variant="body2">
                  <strong>负债比率 (30%)</strong>: 当前负债与总资产的比例
                </Typography>
              </li>
              <li>
                <Typography variant="body2">
                  <strong>信用历史长度 (15%)</strong>: 信用记录的时间跨度
                </Typography>
              </li>
              <li>
                <Typography variant="body2">
                  <strong>信用组合 (10%)</strong>: 信用类型的多样性
                </Typography>
              </li>
              <li>
                <Typography variant="body2">
                  <strong>新增信用 (10%)</strong>: 近期新开立的信用账户
                </Typography>
              </li>
            </Box>
            <Typography variant="body2" sx={{ mt: 2 }} color="textSecondary">
              计算公式: Score = (Σ 因子 × 权重) × 10
            </Typography>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}

export default RiskPage;
