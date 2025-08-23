import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Divider,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Chip,
  IconButton,
  Button,
  CircularProgress,
  Grid,
  Card,
  CardContent,
  CardActions,
  Tooltip
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  ContentCopy as CopyIcon,
  Visibility as VisibilityIcon,
  Check as CheckIcon,
  Error as ErrorIcon,
  Pending as PendingIcon,
  Star as StarIcon,
  StarBorder as StarBorderIcon
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';

const MultiRunResults = ({ 
  results, 
  loading, 
  originalPrompt,
  onViewRun,
  onStarRun,
  starredRuns = []
}) => {
  const navigate = useNavigate();
  const [expandedThread, setExpandedThread] = useState(null);

  const handleCopyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    toast.success('Copied to clipboard!');
  };

  const handleExpandThread = (threadId) => {
    setExpandedThread(expandedThread === threadId ? null : threadId);
  };

  const handleViewRun = (runId) => {
    if (onViewRun) {
      onViewRun(runId);
    } else {
      navigate(`/agent-runs/${runId}`);
    }
  };

  const handleStarRun = (runId) => {
    if (onStarRun) {
      onStarRun(runId);
    }
  };

  const isStarred = (runId) => {
    return starredRuns.includes(runId);
  };

  if (loading) {
    return (
      <Paper sx={{ p: 4, textAlign: 'center' }}>
        <CircularProgress size={40} sx={{ mb: 2 }} />
        <Typography variant="h6">
          Processing Multi-Agent Run
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Synthesizing results from all agent threads...
        </Typography>
      </Paper>
    );
  }

  if (!results) {
    return null;
  }

  return (
    <Paper sx={{ p: 3, mt: 3 }}>
      <Typography variant="h5" gutterBottom>
        Multi-Agent Results
      </Typography>
      
      <Box sx={{ mb: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
          <Typography variant="h6">
            Final Synthesized Response
          </Typography>
          <Tooltip title="Copy to clipboard">
            <IconButton onClick={() => handleCopyToClipboard(results.final)}>
              <CopyIcon />
            </IconButton>
          </Tooltip>
        </Box>
        
        <Paper 
          variant="outlined" 
          sx={{ 
            p: 3, 
            backgroundColor: theme => theme.palette.mode === 'dark' ? '#1e1e1e' : '#f8f8f8',
            whiteSpace: 'pre-wrap',
            borderRadius: 2,
            borderWidth: 2,
            borderColor: 'primary.main'
          }}
        >
          {results.final}
        </Paper>
      </Box>
      
      <Divider sx={{ my: 3 }} />
      
      <Box sx={{ mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Original Prompt
        </Typography>
        <Paper 
          variant="outlined" 
          sx={{ 
            p: 2, 
            backgroundColor: theme => theme.palette.mode === 'dark' ? '#1e1e1e' : '#f8f8f8',
            whiteSpace: 'pre-wrap'
          }}
        >
          {originalPrompt}
        </Paper>
      </Box>
      
      <Divider sx={{ my: 3 }} />
      
      <Typography variant="h6" gutterBottom>
        Individual Thread Results ({results.candidates.length})
      </Typography>
      
      <Grid container spacing={2}>
        {results.agent_runs.map((run, index) => (
          <Grid item xs={12} sm={6} md={4} key={run.id}>
            <Card 
              sx={{ 
                height: '100%', 
                display: 'flex', 
                flexDirection: 'column',
                transition: 'transform 0.2s',
                '&:hover': {
                  transform: 'translateY(-4px)',
                  boxShadow: 3
                }
              }}
            >
              <CardContent sx={{ flexGrow: 1 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                  <Typography variant="h6" component="div">
                    Thread #{index + 1}
                  </Typography>
                  <IconButton 
                    size="small" 
                    onClick={() => handleStarRun(run.id)}
                    color={isStarred(run.id) ? 'warning' : 'default'}
                  >
                    {isStarred(run.id) ? <StarIcon /> : <StarBorderIcon />}
                  </IconButton>
                </Box>
                
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Chip 
                    icon={
                      run.status === 'completed' ? <CheckIcon /> :
                      run.status === 'failed' ? <ErrorIcon /> :
                      <PendingIcon />
                    }
                    label={run.status}
                    color={
                      run.status === 'completed' ? 'success' :
                      run.status === 'failed' ? 'error' :
                      'default'
                    }
                    size="small"
                  />
                  
                  {run.metadata && run.metadata.multi_run_synthesis && (
                    <Chip 
                      label="Synthesis" 
                      color="primary"
                      size="small"
                      sx={{ ml: 1 }}
                    />
                  )}
                </Box>
                
                {run.status === 'completed' && index < results.candidates.length && (
                  <Accordion 
                    expanded={expandedThread === run.id}
                    onChange={() => handleExpandThread(run.id)}
                    sx={{ mb: 1 }}
                  >
                    <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                      <Typography variant="body2">View Response</Typography>
                    </AccordionSummary>
                    <AccordionDetails>
                      <Box sx={{ 
                        maxHeight: 200, 
                        overflow: 'auto',
                        whiteSpace: 'pre-wrap',
                        fontSize: '0.875rem',
                        p: 1,
                        backgroundColor: theme => theme.palette.mode === 'dark' ? '#1e1e1e' : '#f8f8f8',
                        borderRadius: 1
                      }}>
                        {results.candidates[index]}
                      </Box>
                      <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 1 }}>
                        <IconButton 
                          size="small" 
                          onClick={() => handleCopyToClipboard(results.candidates[index])}
                        >
                          <CopyIcon fontSize="small" />
                        </IconButton>
                      </Box>
                    </AccordionDetails>
                  </Accordion>
                )}
              </CardContent>
              
              <CardActions>
                <Button 
                  size="small" 
                  startIcon={<VisibilityIcon />}
                  onClick={() => handleViewRun(run.id)}
                >
                  View Details
                </Button>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Paper>
  );
};

export default MultiRunResults;

