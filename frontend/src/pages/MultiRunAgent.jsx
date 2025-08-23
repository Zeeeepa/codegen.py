import React, { useState } from 'react';
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
  Chip,
  CircularProgress,
  Divider,
  Alert,
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
  Info as InfoIcon,
  Refresh as RefreshIcon,
  Save as SaveIcon,
  ContentCopy as CopyIcon,
  Visibility as VisibilityIcon
} from '@mui/icons-material';
import { toast } from 'react-toastify';

import { useApi } from '../hooks/useApi';
import { useOrganizations } from '../hooks/useOrganizations';
import { useRepositories } from '../hooks/useRepositories';

const MultiRunAgent = () => {
  const navigate = useNavigate();
  const { createMultiRun } = useApi();
  const { organizations, currentOrganization, setCurrentOrganization } = useOrganizations();
  const { repositories } = useRepositories(currentOrganization?.id);
  
  const [prompt, setPrompt] = useState('');
  const [concurrency, setConcurrency] = useState(3);
  const [repoId, setRepoId] = useState('');
  const [model, setModel] = useState('');
  const [temperature, setTemperature] = useState(0.7);
  const [synthesisTemperature, setSynthesisTemperature] = useState(0.2);
  const [customSynthesisPrompt, setCustomSynthesisPrompt] = useState('');
  const [useCustomSynthesis, setUseCustomSynthesis] = useState(false);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [advancedSettingsOpen, setAdvancedSettingsOpen] = useState(false);
  
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
      
      const data = {
        prompt,
        concurrency,
        temperature,
        synthesis_temperature: synthesisTemperature
      };
      
      if (repoId) {
        data.repo_id = parseInt(repoId, 10);
      }
      
      if (model) {
        data.model = model;
      }
      
      if (useCustomSynthesis && customSynthesisPrompt) {
        data.synthesis_prompt = customSynthesisPrompt;
      }
      
      const response = await createMultiRun(currentOrganization.id, data);
      setResult(response);
      toast.success('Multi-run completed successfully!');
    } catch (err) {
      setError(err.message || 'Failed to create multi-run');
      toast.error(`Error: ${err.message || 'Failed to create multi-run'}`);
    } finally {
      setLoading(false);
    }
  };
  
  const handleCopyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    toast.success('Copied to clipboard!');
  };
  
  const handleViewAgentRun = (agentRunId) => {
    navigate(`/agent-runs/${agentRunId}`);
  };
  
  return (
    <Box sx={{ p: 3, maxWidth: 1200, mx: 'auto' }}>
      <Typography variant="h4" gutterBottom>
        Multi-Run Agent
      </Typography>
      
      <Typography variant="body1" color="text.secondary" paragraph>
        Run multiple agent instances concurrently and synthesize their outputs for better results.
      </Typography>
      
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
            
            <Grid item xs={12} md={6}>
              <Typography gutterBottom>
                Concurrency: {concurrency}
              </Typography>
              <Slider
                value={concurrency}
                onChange={(e, newValue) => setConcurrency(newValue)}
                min={1}
                max={20}
                step={1}
                marks={[
                  { value: 1, label: '1' },
                  { value: 5, label: '5' },
                  { value: 10, label: '10' },
                  { value: 20, label: '20' }
                ]}
                disabled={loading}
              />
              <Typography variant="caption" color="text.secondary">
                Number of concurrent agent runs (1-20)
              </Typography>
            </Grid>
            
            <Grid item xs={12} md={6}>
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
                      <Typography gutterBottom>
                        Synthesis Temperature: {synthesisTemperature}
                      </Typography>
                      <Slider
                        value={synthesisTemperature}
                        onChange={(e, newValue) => setSynthesisTemperature(newValue)}
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
                        Temperature for synthesis (lower values produce more consistent results)
                      </Typography>
                    </Grid>
                    
                    <Grid item xs={12}>
                      <FormControl fullWidth component="fieldset">
                        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                          <Button
                            size="small"
                            variant={useCustomSynthesis ? "contained" : "outlined"}
                            onClick={() => setUseCustomSynthesis(!useCustomSynthesis)}
                            startIcon={useCustomSynthesis ? <InfoIcon /> : null}
                            disabled={loading}
                          >
                            {useCustomSynthesis ? "Using Custom Synthesis" : "Use Custom Synthesis Prompt"}
                          </Button>
                          
                          <Tooltip title="By default, the system will generate an appropriate synthesis prompt. Enable this to provide your own custom prompt for synthesizing the results.">
                            <IconButton size="small" sx={{ ml: 1 }}>
                              <InfoIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        </Box>
                        
                        {useCustomSynthesis && (
                          <TextField
                            label="Custom Synthesis Prompt"
                            multiline
                            rows={4}
                            fullWidth
                            value={customSynthesisPrompt}
                            onChange={(e) => setCustomSynthesisPrompt(e.target.value)}
                            disabled={loading}
                            placeholder="Enter custom prompt for synthesizing the results..."
                          />
                        )}
                      </FormControl>
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
                  {loading ? 'Running...' : 'Run Multi-Agent'}
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
      
      {result && (
        <Paper sx={{ p: 3 }}>
          <Typography variant="h5" gutterBottom>
            Results
          </Typography>
          
          <Box sx={{ mb: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
              <Typography variant="h6">
                Final Synthesized Output
              </Typography>
              <IconButton 
                onClick={() => handleCopyToClipboard(result.final)}
                size="small"
              >
                <CopyIcon fontSize="small" />
              </IconButton>
            </Box>
            <Paper 
              variant="outlined" 
              sx={{ 
                p: 2, 
                backgroundColor: theme => theme.palette.mode === 'dark' ? '#1e1e1e' : '#f8f8f8',
                whiteSpace: 'pre-wrap'
              }}
            >
              {result.final}
            </Paper>
          </Box>
          
          <Divider sx={{ my: 3 }} />
          
          <Typography variant="h6" gutterBottom>
            Candidate Outputs ({result.candidates.length})
          </Typography>
          
          <Box sx={{ mb: 3 }}>
            {result.candidates.map((candidate, index) => (
              <Accordion key={index} sx={{ mb: 1 }}>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Typography>
                    Candidate {index + 1}
                  </Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 1 }}>
                    <IconButton 
                      onClick={() => handleCopyToClipboard(candidate)}
                      size="small"
                    >
                      <CopyIcon fontSize="small" />
                    </IconButton>
                  </Box>
                  <Paper 
                    variant="outlined" 
                    sx={{ 
                      p: 2, 
                      backgroundColor: theme => theme.palette.mode === 'dark' ? '#1e1e1e' : '#f8f8f8',
                      whiteSpace: 'pre-wrap'
                    }}
                  >
                    {candidate}
                  </Paper>
                </AccordionDetails>
              </Accordion>
            ))}
          </Box>
          
          <Divider sx={{ my: 3 }} />
          
          <Typography variant="h6" gutterBottom>
            Agent Runs
          </Typography>
          
          <Box sx={{ mb: 3 }}>
            <Grid container spacing={2}>
              {result.agent_runs.map((run, index) => (
                <Grid item xs={12} sm={6} md={4} key={index}>
                  <Paper 
                    variant="outlined" 
                    sx={{ 
                      p: 2,
                      display: 'flex',
                      flexDirection: 'column',
                      height: '100%'
                    }}
                  >
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="subtitle1">
                        Run #{index + 1}
                      </Typography>
                      <Chip 
                        label={run.status} 
                        color={
                          run.status === 'completed' ? 'success' :
                          run.status === 'failed' ? 'error' :
                          run.status === 'running' ? 'info' :
                          'default'
                        }
                        size="small"
                      />
                    </Box>
                    
                    {run.metadata && run.metadata.multi_run_synthesis && (
                      <Chip 
                        label="Synthesis Run" 
                        color="primary"
                        size="small"
                        sx={{ alignSelf: 'flex-start', mb: 1 }}
                      />
                    )}
                    
                    <Box sx={{ flexGrow: 1 }} />
                    
                    <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 2 }}>
                      <Button
                        size="small"
                        onClick={() => handleViewAgentRun(run.id)}
                        startIcon={<VisibilityIcon />}
                      >
                        View
                      </Button>
                    </Box>
                  </Paper>
                </Grid>
              ))}
            </Grid>
          </Box>
        </Paper>
      )}
    </Box>
  );
};

export default MultiRunAgent;

