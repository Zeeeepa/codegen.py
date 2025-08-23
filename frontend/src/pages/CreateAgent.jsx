import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Slider,
  CircularProgress,
  Alert,
  Divider,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  Send as SendIcon,
  Settings as SettingsIcon,
  Info as InfoIcon
} from '@mui/icons-material';
import { toast } from 'react-toastify';

import { useApi } from '../hooks/useApi';
import { useOrganizations } from '../hooks/useOrganizations';
import { useRepositories } from '../hooks/useRepositories';
import MultiRunToggle from '../components/agent/MultiRunToggle';
import MultiRunResults from '../components/agent/MultiRunResults';
import { useStarredRuns } from '../hooks/useStarredRuns';

const CreateAgent = () => {
  const navigate = useNavigate();
  const { createAgentRun, createMultiRun } = useApi();
  const { organizations, currentOrganization, setCurrentOrganization } = useOrganizations();
  const { repositories } = useRepositories(currentOrganization?.id);
  const { starredRunIds, toggleStar } = useStarredRuns();
  
  const [prompt, setPrompt] = useState('');
  const [repoId, setRepoId] = useState('');
  const [model, setModel] = useState('');
  const [temperature, setTemperature] = useState(0.7);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [advancedSettingsOpen, setAdvancedSettingsOpen] = useState(false);
  
  // Multi-run state
  const [multiRunEnabled, setMultiRunEnabled] = useState(false);
  const [threadCount, setThreadCount] = useState(3);
  const [completedThreads, setCompletedThreads] = useState(0);
  const [multiRunResults, setMultiRunResults] = useState(null);
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!prompt) {
      toast.error('Please enter a prompt');
      return;
    }
    
    if (!currentOrganization) {
      toast.error('Please select an organization');
      return;
    }
    
    try {
      setLoading(true);
      setError(null);
      setResult(null);
      setMultiRunResults(null);
      
      if (multiRunEnabled) {
        // Run multi-agent
        setCompletedThreads(0);
        
        const data = {
          prompt,
          concurrency: threadCount,
          temperature
        };
        
        if (repoId) {
          data.repo_id = parseInt(repoId, 10);
        }
        
        if (model) {
          data.model = model;
        }
        
        // Start progress simulation
        const progressInterval = setInterval(() => {
          setCompletedThreads(prev => {
            if (prev >= threadCount) {
              clearInterval(progressInterval);
              return threadCount;
            }
            return Math.min(prev + 1, threadCount - 1);
          });
        }, 1500);
        
        const response = await createMultiRun(currentOrganization.id, data);
        
        // Clear interval and set completed
        clearInterval(progressInterval);
        setCompletedThreads(threadCount);
        
        setMultiRunResults({
          ...response,
          originalPrompt: prompt
        });
        
        toast.success('Multi-agent run completed successfully!');
      } else {
        // Run single agent
        const data = {
          prompt,
          temperature
        };
        
        if (repoId) {
          data.repo_id = parseInt(repoId, 10);
        }
        
        if (model) {
          data.model = model;
        }
        
        const response = await createAgentRun(currentOrganization.id, data);
        setResult(response);
        
        toast.success('Agent run created successfully!');
        
        // Navigate to agent run detail
        navigate(`/agent-runs/${response.id}`);
      }
    } catch (err) {
      setError(err.message || 'Failed to create agent run');
      toast.error(`Error: ${err.message || 'Failed to create agent run'}`);
    } finally {
      setLoading(false);
    }
  };
  
  const handleStarRun = (runId) => {
    toggleStar(runId);
  };
  
  const handleViewRun = (runId) => {
    navigate(`/agent-runs/${runId}`);
  };
  
  return (
    <Box sx={{ p: 3, maxWidth: 1200, mx: 'auto' }}>
      <Typography variant="h4" gutterBottom>
        Create Agent Run
      </Typography>
      
      <Typography variant="body1" color="text.secondary" paragraph>
        Create a new agent run with your prompt and settings.
      </Typography>
      
      <MultiRunToggle
        enabled={multiRunEnabled}
        setEnabled={setMultiRunEnabled}
        threadCount={threadCount}
        setThreadCount={setThreadCount}
        completedThreads={completedThreads}
        totalThreads={threadCount}
        isRunning={loading && multiRunEnabled}
      />
      
      <Paper sx={{ p: 3, mb: 4 }}>
        <form onSubmit={handleSubmit}>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel id="organization-label">Organization</InputLabel>
                <Select
                  labelId="organization-label"
                  value={currentOrganization?.id || ''}
                  onChange={(e) => {
                    const org = organizations.find(o => o.id === e.target.value);
                    setCurrentOrganization(org);
                  }}
                  label="Organization"
                  required
                  disabled={loading}
                >
                  {organizations.map((org) => (
                    <MenuItem key={org.id} value={org.id}>
                      {org.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12}>
              <TextField
                label="Prompt"
                multiline
                rows={6}
                fullWidth
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                required
                disabled={loading}
                placeholder="Enter your prompt here..."
              />
            </Grid>
            
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel id="repository-label">Repository (Optional)</InputLabel>
                <Select
                  labelId="repository-label"
                  value={repoId}
                  onChange={(e) => setRepoId(e.target.value)}
                  label="Repository (Optional)"
                  disabled={loading || !currentOrganization}
                >
                  <MenuItem value="">
                    <em>None</em>
                  </MenuItem>
                  {repositories.map((repo) => (
                    <MenuItem key={repo.id} value={repo.id}>
                      {repo.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel id="model-label">Model (Optional)</InputLabel>
                <Select
                  labelId="model-label"
                  value={model}
                  onChange={(e) => setModel(e.target.value)}
                  label="Model (Optional)"
                  disabled={loading}
                >
                  <MenuItem value="">
                    <em>Default</em>
                  </MenuItem>
                  <MenuItem value="gpt-4">GPT-4</MenuItem>
                  <MenuItem value="gpt-3.5-turbo">GPT-3.5 Turbo</MenuItem>
                  <MenuItem value="claude-3-opus">Claude 3 Opus</MenuItem>
                  <MenuItem value="claude-3-sonnet">Claude 3 Sonnet</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12}>
              <Typography gutterBottom>
                Temperature: {temperature}
              </Typography>
              <Slider
                value={temperature}
                onChange={(e, newValue) => setTemperature(newValue)}
                min={0}
                max={1}
                step={0.1}
                marks={[
                  { value: 0, label: '0' },
                  { value: 0.5, label: '0.5' },
                  { value: 1, label: '1' }
                ]}
                disabled={loading}
              />
              <Typography variant="caption" color="text.secondary">
                Controls randomness (0 = deterministic, 1 = creative)
              </Typography>
            </Grid>
            
            <Grid item xs={12}>
              <Accordion 
                expanded={advancedSettingsOpen} 
                onChange={() => setAdvancedSettingsOpen(!advancedSettingsOpen)}
              >
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <SettingsIcon sx={{ mr: 1 }} />
                    <Typography>Advanced Settings</Typography>
                  </Box>
                </AccordionSummary>
                <AccordionDetails>
                  <Grid container spacing={3}>
                    <Grid item xs={12}>
                      <TextField
                        label="Metadata (JSON)"
                        multiline
                        rows={4}
                        fullWidth
                        placeholder='{"key": "value"}'
                        disabled={loading}
                      />
                      <Typography variant="caption" color="text.secondary">
                        Optional metadata to include with the agent run (JSON format)
                      </Typography>
                    </Grid>
                  </Grid>
                </AccordionDetails>
              </Accordion>
            </Grid>
            
            <Grid item xs={12}>
              <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
                <Button
                  type="submit"
                  variant="contained"
                  color="primary"
                  size="large"
                  disabled={loading || !prompt || !currentOrganization}
                  startIcon={loading ? <CircularProgress size={20} /> : <SendIcon />}
                >
                  {loading ? 'Running...' : multiRunEnabled ? 'Run Multi-Agent' : 'Create Agent Run'}
                </Button>
              </Box>
            </Grid>
          </Grid>
        </form>
      </Paper>
      
      {error && (
        <Alert severity="error" sx={{ mb: 4 }}>
          {error}
        </Alert>
      )}
      
      {multiRunResults && (
        <MultiRunResults
          results={multiRunResults}
          loading={false}
          originalPrompt={prompt}
          onViewRun={handleViewRun}
          onStarRun={handleStarRun}
          starredRuns={starredRunIds}
        />
      )}
    </Box>
  );
};

export default CreateAgent;

