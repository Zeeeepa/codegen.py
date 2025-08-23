import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

// Components
import Header from './components/layout/Header';
import Sidebar from './components/layout/Sidebar';
import Dashboard from './pages/Dashboard';
import AgentRuns from './pages/AgentRuns';
import AgentRunDetail from './pages/AgentRunDetail';
import CreateAgent from './pages/CreateAgent';
import Projects from './pages/Projects';
import Settings from './pages/Settings';
import Login from './pages/Login';
import StarredRuns from './pages/StarredRuns';
import MultiRunAgent from './pages/MultiRunAgent';

// Context
import { AuthProvider } from './context/AuthContext';
import { ApiProvider } from './context/ApiContext';
import { ThemeProvider as CustomThemeProvider } from './context/ThemeContext';

// Styles
import './App.css';

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  return (
    <CustomThemeProvider>
      <ThemeConsumer>
        {({ theme }) => (
          <ThemeProvider theme={theme}>
            <CssBaseline />
            <AuthProvider>
              <ApiProvider>
                <Router>
                  <div className="app">
                    <ToastContainer position="top-right" autoClose={5000} />
                    <Routes>
                      <Route path="/login" element={<Login />} />
                      <Route
                        path="/*"
                        element={
                          <PrivateRoutes 
                            sidebarOpen={sidebarOpen} 
                            toggleSidebar={toggleSidebar} 
                          />
                        }
                      />
                    </Routes>
                  </div>
                </Router>
              </ApiProvider>
            </AuthProvider>
          </ThemeProvider>
        )}
      </ThemeConsumer>
    </CustomThemeProvider>
  );
}

// Theme consumer component
function ThemeConsumer({ children }) {
  const { currentTheme } = React.useContext(CustomThemeProvider.context);
  
  const theme = createTheme({
    palette: {
      mode: currentTheme,
      primary: {
        main: currentTheme === 'dark' ? '#90caf9' : '#1976d2',
      },
      secondary: {
        main: currentTheme === 'dark' ? '#f48fb1' : '#dc004e',
      },
      background: {
        default: currentTheme === 'dark' ? '#121212' : '#f5f5f5',
        paper: currentTheme === 'dark' ? '#1e1e1e' : '#ffffff',
      },
    },
  });
  
  return children({ theme });
}

// Private routes component
function PrivateRoutes({ sidebarOpen, toggleSidebar }) {
  const { isAuthenticated, loading } = React.useContext(AuthProvider.context);
  
  if (loading) {
    return <div>Loading...</div>;
  }
  
  if (!isAuthenticated) {
    return <Navigate to="/login" />;
  }
  
  return (
    <>
      <Header toggleSidebar={toggleSidebar} />
      <div className="container">
        <Sidebar open={sidebarOpen} />
        <main className={`main-content ${sidebarOpen ? '' : 'expanded'}`}>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/agent-runs" element={<AgentRuns />} />
            <Route path="/agent-runs/:id" element={<AgentRunDetail />} />
            <Route path="/create-agent" element={<CreateAgent />} />
            <Route path="/projects" element={<Projects />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="/starred-runs" element={<StarredRuns />} />
            <Route path="/multi-run" element={<MultiRunAgent />} />
            <Route path="*" element={<Navigate to="/" />} />
          </Routes>
        </main>
      </div>
    </>
  );
}

export default App;

