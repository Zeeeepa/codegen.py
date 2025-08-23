import React from 'react';
import { Link } from 'react-router-dom';
import { 
  Card, 
  CardContent, 
  CardActions, 
  Typography, 
  Button, 
  Chip, 
  IconButton,
  Tooltip,
  Box
} from '@mui/material';
import { 
  AccessTime as AccessTimeIcon,
  Star as StarIcon,
  StarBorder as StarBorderIcon,
  Refresh as RefreshIcon,
  Visibility as VisibilityIcon,
  Code as CodeIcon
} from '@mui/icons-material';
import { formatDistanceToNow } from 'date-fns';

import StatusBadge from '../common/StatusBadge';
import { useApi } from '../../hooks/useApi';
import { useStarredRuns } from '../../hooks/useStarredRuns';

const AgentRunCard = ({ agentRun, onResume, onRefresh }) => {
  const { resumeAgentRun } = useApi();
  const { isStarred, toggleStar } = useStarredRuns();
  
  const handleResume = async () => {
    try {
      const resumed = await resumeAgentRun(agentRun.organization_id, agentRun.id);
      if (onResume) {
        onResume(resumed);
      }
    } catch (error) {
      console.error('Error resuming agent run:', error);
    }
  };
  
  const handleRefresh = () => {
    if (onRefresh) {
      onRefresh(agentRun.id);
    }
  };
  
  const handleToggleStar = () => {
    toggleStar(agentRun.id);
  };
  
  const starred = isStarred(agentRun.id);
  
  return (
    <Card 
      sx={{ 
        height: '100%', 
        display: 'flex', 
        flexDirection: 'column',
        transition: 'transform 0.2s, box-shadow 0.2s',
        '&:hover': {
          transform: 'translateY(-4px)',
          boxShadow: 4
        }
      }}
    >
      <CardContent sx={{ flexGrow: 1 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
          <Typography variant="h6" component="div" noWrap sx={{ maxWidth: '80%' }}>
            {agentRun.prompt ? (
              agentRun.prompt.substring(0, 50) + (agentRun.prompt.length > 50 ? '...' : '')
            ) : (
              `Agent Run #${agentRun.id}`
            )}
          </Typography>
          <IconButton 
            size="small" 
            onClick={handleToggleStar}
            color={starred ? 'warning' : 'default'}
          >
            {starred ? <StarIcon /> : <StarBorderIcon />}
          </IconButton>
        </Box>
        
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
          <StatusBadge status={agentRun.status} />
          <Typography variant="body2" color="text.secondary" sx={{ ml: 1, display: 'flex', alignItems: 'center' }}>
            <AccessTimeIcon fontSize="small" sx={{ mr: 0.5 }} />
            {formatDistanceToNow(new Date(agentRun.created_at), { addSuffix: true })}
          </Typography>
        </Box>
        
        {agentRun.repo_id && (
          <Chip 
            icon={<CodeIcon fontSize="small" />}
            label={`Repo: ${agentRun.repo_id}`}
            size="small"
            sx={{ mt: 1, mr: 1 }}
          />
        )}
        
        {agentRun.model && (
          <Chip 
            label={`Model: ${agentRun.model}`}
            size="small"
            sx={{ mt: 1 }}
          />
        )}
        
        {agentRun.github_pull_requests && agentRun.github_pull_requests.length > 0 && (
          <Box sx={{ mt: 2 }}>
            <Typography variant="body2" color="text.secondary">
              Pull Requests:
            </Typography>
            {agentRun.github_pull_requests.map(pr => (
              <Chip 
                key={pr.id}
                label={`#${pr.id}: ${pr.title.substring(0, 20)}...`}
                component="a"
                href={pr.url}
                target="_blank"
                rel="noopener noreferrer"
                clickable
                size="small"
                sx={{ mt: 0.5, mr: 0.5 }}
              />
            ))}
          </Box>
        )}
      </CardContent>
      
      <CardActions>
        <Button 
          component={Link} 
          to={`/agent-runs/${agentRun.id}`}
          startIcon={<VisibilityIcon />}
          size="small"
        >
          View
        </Button>
        
        {agentRun.status === 'completed' && (
          <Button 
            onClick={handleResume}
            startIcon={<RefreshIcon />}
            size="small"
          >
            Resume
          </Button>
        )}
        
        <Tooltip title="Refresh">
          <IconButton size="small" onClick={handleRefresh}>
            <RefreshIcon fontSize="small" />
          </IconButton>
        </Tooltip>
        
        {agentRun.web_url && (
          <Button 
            component="a"
            href={agentRun.web_url}
            target="_blank"
            rel="noopener noreferrer"
            size="small"
            sx={{ ml: 'auto' }}
          >
            Open in Codegen
          </Button>
        )}
      </CardActions>
    </Card>
  );
};

export default AgentRunCard;

