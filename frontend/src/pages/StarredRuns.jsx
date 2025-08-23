import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Grid,
  Paper,
  CircularProgress,
  Alert,
  TextField,
  InputAdornment,
  IconButton,
  Divider,
  Chip,
  Button,
  Menu,
  MenuItem
} from '@mui/material';
import {
  Search as SearchIcon,
  FilterList as FilterListIcon,
  Star as StarIcon,
  Refresh as RefreshIcon,
  MoreVert as MoreVertIcon,
  Delete as DeleteIcon
} from '@mui/icons-material';
import { toast } from 'react-toastify';

import AgentRunCard from '../components/agent/AgentRunCard';
import { useApi } from '../hooks/useApi';
import { useStarredRuns } from '../hooks/useStarredRuns';
import { useOrganizations } from '../hooks/useOrganizations';

const StarredRuns = () => {
  const { getAgentRun } = useApi();
  const { starredRunIds, removeStarredRun, clearAllStarredRuns } = useStarredRuns();
  const { currentOrganization } = useOrganizations();
  
  const [starredRuns, setStarredRuns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [menuAnchorEl, setMenuAnchorEl] = useState(null);
  
  // Load starred runs
  useEffect(() => {
    const loadStarredRuns = async () => {
      if (!currentOrganization || starredRunIds.length === 0) {
        setStarredRuns([]);
        setLoading(false);
        return;
      }
      
      setLoading(true);
      setError(null);
      
      try {
        const runs = await Promise.all(
          starredRunIds.map(async (id) => {
            try {
              return await getAgentRun(currentOrganization.id, id);
            } catch (err) {
              console.error(`Error fetching run ${id}:`, err);
              return null;
            }
          })
        );
        
        // Filter out null values (failed fetches)
        const validRuns = runs.filter(run => run !== null);
        setStarredRuns(validRuns);
      } catch (err) {
        setError(err.message || 'Failed to load starred runs');
        toast.error(`Error: ${err.message || 'Failed to load starred runs'}`);
      } finally {
        setLoading(false);
      }
    };
    
    loadStarredRuns();
  }, [currentOrganization, starredRunIds, getAgentRun]);
  
  const handleRefresh = async () => {
    if (!currentOrganization) {
      toast.error('Please select an organization');
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      const runs = await Promise.all(
        starredRunIds.map(async (id) => {
          try {
            return await getAgentRun(currentOrganization.id, id);
          } catch (err) {
            console.error(`Error fetching run ${id}:`, err);
            return null;
          }
        })
      );
      
      // Filter out null values (failed fetches)
      const validRuns = runs.filter(run => run !== null);
      setStarredRuns(validRuns);
      toast.success('Starred runs refreshed');
    } catch (err) {
      setError(err.message || 'Failed to refresh starred runs');
      toast.error(`Error: ${err.message || 'Failed to refresh starred runs'}`);
    } finally {
      setLoading(false);
    }
  };
  
  const handleRemoveStarredRun = (id) => {
    removeStarredRun(id);
    setStarredRuns(prevRuns => prevRuns.filter(run => run.id !== id));
    toast.success('Run removed from starred');
  };
  
  const handleClearAllStarredRuns = () => {
    clearAllStarredRuns();
    setStarredRuns([]);
    toast.success('All starred runs cleared');
    setMenuAnchorEl(null);
  };
  
  const handleMenuOpen = (event) => {
    setMenuAnchorEl(event.currentTarget);
  };
  
  const handleMenuClose = () => {
    setMenuAnchorEl(null);
  };
  
  // Filter runs based on search term and status filter
  const filteredRuns = starredRuns.filter(run => {
    const matchesSearch = searchTerm === '' || 
      (run.prompt && run.prompt.toLowerCase().includes(searchTerm.toLowerCase()));
    
    const matchesStatus = statusFilter === 'all' || run.status === statusFilter;
    
    return matchesSearch && matchesStatus;
  });
  
  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          <StarIcon sx={{ mr: 1, verticalAlign: 'middle', color: 'warning.main' }} />
          Starred Agent Runs
        </Typography>
        
        <Box>
          <IconButton onClick={handleRefresh} disabled={loading}>
            <RefreshIcon />
          </IconButton>
          
          <IconButton onClick={handleMenuOpen}>
            <MoreVertIcon />
          </IconButton>
          
          <Menu
            anchorEl={menuAnchorEl}
            open={Boolean(menuAnchorEl)}
            onClose={handleMenuClose}
          >
            <MenuItem onClick={handleClearAllStarredRuns} disabled={starredRunIds.length === 0}>
              <DeleteIcon fontSize="small" sx={{ mr: 1 }} />
              Clear All Starred Runs
            </MenuItem>
          </Menu>
        </Box>
      </Box>
      
      <Paper sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              placeholder="Search starred runs..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon />
                  </InputAdornment>
                ),
              }}
              size="small"
            />
          </Grid>
          
          <Grid item xs={12} md={6}>
            <Box sx={{ display: 'flex', gap: 1 }}>
              <Chip
                label="All"
                color={statusFilter === 'all' ? 'primary' : 'default'}
                onClick={() => setStatusFilter('all')}
                clickable
              />
              <Chip
                label="Completed"
                color={statusFilter === 'completed' ? 'primary' : 'default'}
                onClick={() => setStatusFilter('completed')}
                clickable
              />
              <Chip
                label="Running"
                color={statusFilter === 'running' ? 'primary' : 'default'}
                onClick={() => setStatusFilter('running')}
                clickable
              />
              <Chip
                label="Failed"
                color={statusFilter === 'failed' ? 'primary' : 'default'}
                onClick={() => setStatusFilter('failed')}
                clickable
              />
            </Box>
          </Grid>
        </Grid>
      </Paper>
      
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}
      
      {loading && starredRuns.length === 0 ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
          <CircularProgress />
        </Box>
      ) : starredRunIds.length === 0 ? (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <StarIcon sx={{ fontSize: 60, color: 'text.secondary', opacity: 0.3, mb: 2 }} />
          <Typography variant="h6" color="text.secondary" gutterBottom>
            No Starred Runs
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Star agent runs to keep track of them here.
          </Typography>
        </Paper>
      ) : filteredRuns.length === 0 ? (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <Typography variant="h6" color="text.secondary" gutterBottom>
            No Matching Runs
          </Typography>
          <Typography variant="body2" color="text.secondary">
            No starred runs match your current filters.
          </Typography>
          <Button 
            variant="outlined" 
            sx={{ mt: 2 }} 
            onClick={() => {
              setSearchTerm('');
              setStatusFilter('all');
            }}
          >
            Clear Filters
          </Button>
        </Paper>
      ) : (
        <Grid container spacing={3}>
          {filteredRuns.map((run) => (
            <Grid item xs={12} sm={6} md={4} key={run.id}>
              <Box sx={{ position: 'relative' }}>
                <AgentRunCard 
                  agentRun={run} 
                  onRefresh={() => handleRefresh()} 
                />
                <IconButton
                  sx={{
                    position: 'absolute',
                    top: 8,
                    right: 8,
                    backgroundColor: 'background.paper',
                    '&:hover': {
                      backgroundColor: 'action.hover',
                    },
                  }}
                  size="small"
                  onClick={() => handleRemoveStarredRun(run.id)}
                >
                  <DeleteIcon fontSize="small" />
                </IconButton>
              </Box>
            </Grid>
          ))}
        </Grid>
      )}
      
      {loading && starredRuns.length > 0 && (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
          <CircularProgress size={24} />
        </Box>
      )}
    </Box>
  );
};

export default StarredRuns;

