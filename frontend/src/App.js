import React, { useState } from 'react';
import {
  ThemeProvider,
  createTheme,
  CssBaseline,
  Box,
  AppBar,
  Toolbar,
  Typography,
  Container,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemButton,
} from '@mui/material';
import {
  Dashboard,
  AccountBalance,
  Assessment,
  TrendingUp,
  Gavel,
  Token,
} from '@mui/icons-material';

// 导入页面组件
import DashboardPage from './pages/DashboardPage';
import AssetsPage from './pages/AssetsPage';
import ValuationPage from './pages/ValuationPage';
import RiskPage from './pages/RiskPage';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

const drawerWidth = 240;

const menuItems = [
  { text: '仪表盘', icon: <Dashboard />, page: 'dashboard' },
  { text: '资产管理', icon: <AccountBalance />, page: 'assets' },
  { text: '资产估值', icon: <Assessment />, page: 'valuation' },
  { text: '风险评估', icon: <TrendingUp />, page: 'risk' },
  { text: '资产交易', icon: <Gavel />, page: 'trading' },
  { text: '代币管理', icon: <Token />, page: 'tokens' },
];

function App() {
  const [currentPage, setCurrentPage] = useState('dashboard');

  const renderPage = () => {
    switch (currentPage) {
      case 'dashboard':
        return <DashboardPage />;
      case 'assets':
        return <AssetsPage />;
      case 'valuation':
        return <ValuationPage />;
      case 'risk':
        return <RiskPage />;
      default:
        return <DashboardPage />;
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ display: 'flex' }}>
        {/* 顶部导航栏 */}
        <AppBar
          position="fixed"
          sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}
        >
          <Toolbar>
            <Typography variant="h6" noWrap component="div">
              RWA低效资产管理系统
            </Typography>
          </Toolbar>
        </AppBar>

        {/* 侧边栏 */}
        <Drawer
          variant="permanent"
          sx={{
            width: drawerWidth,
            flexShrink: 0,
            '& .MuiDrawer-paper': {
              width: drawerWidth,
              boxSizing: 'border-box',
            },
          }}
        >
          <Toolbar />
          <Box sx={{ overflow: 'auto' }}>
            <List>
              {menuItems.map((item) => (
                <ListItem key={item.page} disablePadding>
                  <ListItemButton
                    selected={currentPage === item.page}
                    onClick={() => setCurrentPage(item.page)}
                  >
                    <ListItemIcon>{item.icon}</ListItemIcon>
                    <ListItemText primary={item.text} />
                  </ListItemButton>
                </ListItem>
              ))}
            </List>
          </Box>
        </Drawer>

        {/* 主内容区 */}
        <Box
          component="main"
          sx={{
            flexGrow: 1,
            bgcolor: 'background.default',
            p: 3,
          }}
        >
          <Toolbar />
          <Container maxWidth="xl">
            {renderPage()}
          </Container>
        </Box>
      </Box>
    </ThemeProvider>
  );
}

export default App;
