import React, { useState } from 'react';
import {
  Box,
  FormControlLabel,
  Switch,
  Typography,
  TextField,
  Slider,
  Paper,
  Tooltip,
  IconButton,
  Collapse,
  LinearProgress,
  Chip
} from '@mui/material';
import {
  Info as InfoIcon,
  Settings as SettingsIcon
} from '@mui/icons-material';

const MultiRunToggle = ({ 
  enabled, 
  setEnabled, 
  threadCount, 
  setThreadCount,
  completedThreads = 0,
  totalThreads = 0,
  isRunning = false
}) => {
  const [showSettings, setShowSettings] = useState(false);

  const handleToggleChange = (event) => {
    setEnabled(event.target.checked);
  };

  const handleThreadCountChange = (event) => {
    const value = parseInt(event.target.value, 10);
    if (!isNaN(value) && value >= 1 && value <= 20) {
      setThreadCount(value);
    }
  };

  const handleSliderChange = (event, newValue) => {
    setThreadCount(newValue);
  };

  return (
    <Paper sx={{ p: 2, mb: 3, position: 'relative' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <FormControlLabel
            control={
              <Switch
                checked={enabled}
                onChange={handleToggleChange}
                color="primary"
              />
            }
            label={
              <Typography variant="subtitle1" fontWeight="bold">
                Multi-Agent Run
              </Typography>
            }
          />
          <Tooltip title="Run your query through multiple parallel agents and synthesize the results into a single best answer. This can provide more comprehensive and accurate responses.">
            <IconButton size="small">
              <InfoIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </Box>
        
        {enabled && (
          <IconButton 
            size="small" 
            onClick={() => setShowSettings(!showSettings)}
            color={showSettings ? "primary" : "default"}
          >
            <SettingsIcon />
          </IconButton>
        )}
      </Box>
      
      <Collapse in={enabled}>
        <Box sx={{ mt: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
            <Typography variant="body2" sx={{ mr: 2 }}>
              Thread Count:
            </Typography>
            <TextField
              value={threadCount}
              onChange={handleThreadCountChange}
              type="number"
              InputProps={{ 
                inputProps: { min: 1, max: 20 } 
              }}
              size="small"
              sx={{ width: 70, mr: 2 }}
            />
            <Slider
              value={threadCount}
              onChange={handleSliderChange}
              min={1}
              max={20}
              step={1}
              marks={[
                { value: 1, label: '1' },
                { value: 5, label: '5' },
                { value: 10, label: '10' },
                { value: 20, label: '20' }
              ]}
              sx={{ flexGrow: 1 }}
            />
          </Box>
          
          <Collapse in={showSettings}>
            <Box sx={{ mt: 2 }}>
              <Typography variant="body2" gutterBottom>
                Advanced Settings:
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                <Chip 
                  label="Diverse Models" 
                  variant="outlined" 
                  onClick={() => {}} 
                />
                <Chip 
                  label="Temperature Variation" 
                  variant="outlined" 
                  onClick={() => {}} 
                />
                <Chip 
                  label="Custom Synthesis" 
                  variant="outlined" 
                  onClick={() => {}} 
                />
              </Box>
            </Box>
          </Collapse>
          
          {isRunning && (
            <Box sx={{ mt: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                <Typography variant="body2">
                  Progress: {completedThreads}/{totalThreads} threads complete
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {Math.round((completedThreads / totalThreads) * 100)}%
                </Typography>
              </Box>
              <LinearProgress 
                variant="determinate" 
                value={(completedThreads / totalThreads) * 100} 
                sx={{ height: 8, borderRadius: 4 }}
              />
            </Box>
          )}
        </Box>
      </Collapse>
    </Paper>
  );
};

export default MultiRunToggle;

