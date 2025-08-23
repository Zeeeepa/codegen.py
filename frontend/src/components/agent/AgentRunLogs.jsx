import React, { useState, useEffect, useRef } from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  Divider, 
  CircularProgress,
  FormControlLabel,
  Switch,
  Chip,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  AutoScroll as AutoScrollIcon,
  FilterList as FilterListIcon,
  Code as CodeIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
  CheckCircle as CheckCircleIcon
} from '@mui/icons-material';
import { formatDistanceToNow } from 'date-fns';
import ReactJson from 'react-json-view';

import { useApi } from '../../hooks/useApi';

const LogTypeIcon = ({ type }) => {
  switch (type) {
    case 'ACTION':
      return <CodeIcon fontSize="small" color="primary" />;
    case 'ERROR':
      return <ErrorIcon fontSize="small" color="error" />;
    case 'FINAL_ANSWER':
      return <CheckCircleIcon fontSize="small" color="success" />;
    default:
      return <InfoIcon fontSize="small" color="info" />;
  }
};

const AgentRunLogs = ({ organizationId, agentRunId }) => {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [autoScroll, setAutoScroll] = useState(true);
  const [expandedLogs, setExpandedLogs] = useState({});
  const [filters, setFilters] = useState({
    ACTION: true,
    ERROR: true,
    PLAN_EVALUATION: true,
    FINAL_ANSWER: true,
    USER_MESSAGE: true,
    OTHER: true
  });
  
  const logsEndRef = useRef(null);
  const { getAgentRunLogs } = useApi();
  
  // Fetch initial logs
  useEffect(() => {
    const fetchLogs = async () => {
      try {
        setLoading(true);
        const response = await getAgentRunLogs(organizationId, agentRunId);
        setLogs(response.logs || []);
        setError(null);
      } catch (err) {
        setError(err.message || 'Failed to fetch logs');
      } finally {
        setLoading(false);
      }
    };
    
    fetchLogs();
  }, [organizationId, agentRunId, getAgentRunLogs]);
  
  // Set up log streaming
  useEffect(() => {
    const eventSource = new EventSource(
      `${process.env.REACT_APP_API_URL}/organizations/${organizationId}/agent/run/${agentRunId}/logs/stream`
    );
    
    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      if (data.event === 'end') {
        eventSource.close();
        return;
      }
      
      if (data.event === 'error') {
        setError(data.message || 'Error streaming logs');
        eventSource.close();
        return;
      }
      
      setLogs(prevLogs => {
        // Check if log already exists
        const exists = prevLogs.some(log => log.id === data.id);
        if (exists) return prevLogs;
        
        return [...prevLogs, data];
      });
    };
    
    eventSource.onerror = () => {
      eventSource.close();
    };
    
    return () => {
      eventSource.close();
    };
  }, [organizationId, agentRunId]);
  
  // Auto-scroll to bottom when new logs arrive
  useEffect(() => {
    if (autoScroll && logsEndRef.current) {
      logsEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs, autoScroll]);
  
  const toggleLogExpansion = (logId) => {
    setExpandedLogs(prev => ({
      ...prev,
      [logId]: !prev[logId]
    }));
  };
  
  const toggleFilter = (filterType) => {
    setFilters(prev => ({
      ...prev,
      [filterType]: !prev[filterType]
    }));
  };
  
  const filteredLogs = logs.filter(log => {
    if (filters[log.message_type]) return true;
    if (!filters.OTHER) return false;
    
    // If message_type is not in our predefined filters, check OTHER
    return !['ACTION', 'ERROR', 'PLAN_EVALUATION', 'FINAL_ANSWER', 'USER_MESSAGE'].includes(log.message_type);
  });
  
  if (loading && logs.length === 0) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
        <CircularProgress />
      </Box>
    );
  }
  
  if (error) {
    return (
      <Box sx={{ p: 2 }}>
        <Typography color="error">Error: {error}</Typography>
      </Box>
    );
  }
  
  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ p: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h6">Agent Run Logs</Typography>
        
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <Tooltip title="Filter Logs">
            <IconButton 
              size="small" 
              onClick={() => {
                // Toggle filter panel
              }}
            >
              <FilterListIcon />
            </IconButton>
          </Tooltip>
          
          <FormControlLabel
            control={
              <Switch
                checked={autoScroll}
                onChange={() => setAutoScroll(!autoScroll)}
                size="small"
              />
            }
            label={
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <AutoScrollIcon fontSize="small" sx={{ mr: 0.5 }} />
                <Typography variant="body2">Auto-scroll</Typography>
              </Box>
            }
          />
        </Box>
      </Box>
      
      <Box sx={{ p: 1, display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
        {Object.keys(filters).map(filterType => (
          <Chip
            key={filterType}
            label={filterType}
            color={filters[filterType] ? 'primary' : 'default'}
            onClick={() => toggleFilter(filterType)}
            size="small"
          />
        ))}
      </Box>
      
      <Divider />
      
      <Box 
        sx={{ 
          flexGrow: 1, 
          overflow: 'auto', 
          p: 2,
          backgroundColor: theme => theme.palette.mode === 'dark' ? '#121212' : '#f5f5f5'
        }}
      >
        {filteredLogs.length === 0 ? (
          <Typography variant="body2" color="text.secondary" align="center">
            No logs available
          </Typography>
        ) : (
          filteredLogs.map((log, index) => (
            <Paper 
              key={log.id || index} 
              elevation={1} 
              sx={{ 
                p: 2, 
                mb: 2,
                borderLeft: '4px solid',
                borderColor: theme => {
                  switch (log.message_type) {
                    case 'ERROR':
                      return theme.palette.error.main;
                    case 'ACTION':
                      return theme.palette.primary.main;
                    case 'FINAL_ANSWER':
                      return theme.palette.success.main;
                    default:
                      return theme.palette.info.main;
                  }
                }
              }}
            >
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <LogTypeIcon type={log.message_type} />
                  <Typography variant="subtitle2" sx={{ ml: 1 }}>
                    {log.message_type}
                  </Typography>
                  {log.tool_name && (
                    <Chip 
                      label={log.tool_name} 
                      size="small" 
                      sx={{ ml: 1 }} 
                    />
                  )}
                </Box>
                <Typography variant="caption" color="text.secondary">
                  {formatDistanceToNow(new Date(log.created_at), { addSuffix: true })}
                </Typography>
              </Box>
              
              {log.thought && (
                <Box sx={{ mt: 1, mb: 1 }}>
                  <Typography variant="body2" fontWeight="bold">Thought:</Typography>
                  <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                    {log.thought}
                  </Typography>
                </Box>
              )}
              
              {log.tool_input && (
                <Box sx={{ mt: 1, mb: 1 }}>
                  <Typography variant="body2" fontWeight="bold">Tool Input:</Typography>
                  <Box sx={{ 
                    backgroundColor: theme => theme.palette.mode === 'dark' ? '#1e1e1e' : '#f8f8f8',
                    borderRadius: 1,
                    p: 1
                  }}>
                    <ReactJson 
                      src={log.tool_input} 
                      name={false} 
                      collapsed={!expandedLogs[log.id]} 
                      enableClipboard={false}
                      displayDataTypes={false}
                      theme={theme => theme.palette.mode === 'dark' ? 'monokai' : 'rjv-default'}
                    />
                  </Box>
                </Box>
              )}
              
              {log.tool_output && (
                <Box sx={{ mt: 1, mb: 1 }}>
                  <Typography variant="body2" fontWeight="bold">Tool Output:</Typography>
                  <Box sx={{ 
                    backgroundColor: theme => theme.palette.mode === 'dark' ? '#1e1e1e' : '#f8f8f8',
                    borderRadius: 1,
                    p: 1
                  }}>
                    <ReactJson 
                      src={log.tool_output} 
                      name={false} 
                      collapsed={!expandedLogs[log.id]} 
                      enableClipboard={false}
                      displayDataTypes={false}
                      theme={theme => theme.palette.mode === 'dark' ? 'monokai' : 'rjv-default'}
                    />
                  </Box>
                </Box>
              )}
              
              {log.observation && (
                <Box sx={{ mt: 1 }}>
                  <Typography variant="body2" fontWeight="bold">Observation:</Typography>
                  {typeof log.observation === 'object' ? (
                    <Box sx={{ 
                      backgroundColor: theme => theme.palette.mode === 'dark' ? '#1e1e1e' : '#f8f8f8',
                      borderRadius: 1,
                      p: 1
                    }}>
                      <ReactJson 
                        src={log.observation} 
                        name={false} 
                        collapsed={!expandedLogs[log.id]} 
                        enableClipboard={false}
                        displayDataTypes={false}
                        theme={theme => theme.palette.mode === 'dark' ? 'monokai' : 'rjv-default'}
                      />
                    </Box>
                  ) : (
                    <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                      {log.observation}
                    </Typography>
                  )}
                </Box>
              )}
              
              <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 1 }}>
                <Tooltip title={expandedLogs[log.id] ? "Collapse" : "Expand"}>
                  <IconButton 
                    size="small" 
                    onClick={() => toggleLogExpansion(log.id)}
                  >
                    {expandedLogs[log.id] ? (
                      <span>-</span>
                    ) : (
                      <span>+</span>
                    )}
                  </IconButton>
                </Tooltip>
              </Box>
            </Paper>
          ))
        )}
        <div ref={logsEndRef} />
      </Box>
      
      {loading && logs.length > 0 && (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 2 }}>
          <CircularProgress size={24} />
        </Box>
      )}
    </Box>
  );
};

export default AgentRunLogs;

