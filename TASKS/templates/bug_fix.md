# Bug Fix Template

## Task Context
- **Repository**: {repo_url}
- **Branch/PR**: {target_branch}
- **Task Type**: BUG_FIX
- **Priority**: {priority}
- **Assigned**: {assignee}
- **Created**: {created_at}

## Bug Description
{query}

## Bug Analysis

### 1. Problem Statement
- **Summary**: Brief description of the bug
- **Impact**: Who/what is affected
- **Severity**: Critical | High | Medium | Low
- **Frequency**: Always | Often | Sometimes | Rare

### 2. Reproduction Steps
1. Step 1
2. Step 2
3. Step 3
4. Expected result vs Actual result

### 3. Environment Information
- **OS**: 
- **Browser/Runtime**: 
- **Version**: 
- **Configuration**: 

### 4. Error Information
```
[Paste error logs, stack traces, or error messages here]
```

### 5. Root Cause Analysis
- **Primary Cause**: 
- **Contributing Factors**: 
- **Code Location**: 
- **Introduced In**: Commit/PR where bug was introduced

## Fix Strategy

### 1. Approach
- [ ] Quick hotfix
- [ ] Comprehensive fix
- [ ] Refactoring required
- [ ] Architecture change needed

### 2. Impact Assessment
- **Files to be modified**: 
- **Potential side effects**: 
- **Backward compatibility**: 
- **Performance impact**: 

### 3. Testing Strategy
- [ ] Unit tests for the fix
- [ ] Integration tests
- [ ] Regression tests
- [ ] Manual testing scenarios

## Implementation Checklist

### 1. Investigation
- [ ] Reproduce the bug locally
- [ ] Identify root cause
- [ ] Analyze impact and scope
- [ ] Review related code
- [ ] Check for similar issues

### 2. Fix Development
- [ ] Create fix branch
- [ ] Implement the fix
- [ ] Add error handling
- [ ] Add logging for debugging
- [ ] Optimize performance if needed

### 3. Testing
- [ ] Write/update unit tests
- [ ] Test the specific bug scenario
- [ ] Test edge cases
- [ ] Run regression tests
- [ ] Test in different environments

### 4. Code Quality
- [ ] Code review
- [ ] Static analysis
- [ ] Security review (if applicable)
- [ ] Performance testing
- [ ] Documentation update

### 5. Deployment Preparation
- [ ] Prepare deployment plan
- [ ] Create rollback plan
- [ ] Update monitoring/alerting
- [ ] Prepare communication plan

## Fix Details

### Code Changes
```diff
// Show the key code changes here
- old code
+ new code
```

### Database Changes
```sql
-- Any database changes required
```

### Configuration Changes
```yaml
# Any configuration changes
```

## Testing Results

### Unit Tests
- [ ] All existing tests pass
- [ ] New tests added for the bug
- [ ] Test coverage maintained/improved

### Integration Tests
- [ ] API tests pass
- [ ] Database integration tests pass
- [ ] External service integration tests pass

### Manual Testing
- [ ] Bug scenario resolved
- [ ] No regression in related features
- [ ] Performance impact acceptable
- [ ] User experience improved

## Prevention Measures

### 1. Code Improvements
- [ ] Add input validation
- [ ] Improve error handling
- [ ] Add defensive programming
- [ ] Improve logging

### 2. Process Improvements
- [ ] Add automated tests
- [ ] Improve code review process
- [ ] Add monitoring/alerting
- [ ] Update documentation

### 3. Monitoring
- [ ] Add metrics for early detection
- [ ] Set up alerts for similar issues
- [ ] Improve error reporting
- [ ] Add health checks

## Verification Plan

### 1. Pre-Deployment
- [ ] Code review approved
- [ ] All tests pass
- [ ] Security scan clean
- [ ] Performance benchmarks met

### 2. Post-Deployment
- [ ] Monitor error rates
- [ ] Check performance metrics
- [ ] Verify user reports
- [ ] Monitor for regressions

### 3. Success Criteria
- [ ] Bug no longer reproducible
- [ ] No new related issues
- [ ] Performance maintained
- [ ] User satisfaction improved

## Rollback Plan

### Immediate Actions
1. Revert the deployment
2. Restore previous version
3. Notify stakeholders
4. Monitor system stability

### Data Recovery
1. Check data integrity
2. Restore from backup if needed
3. Verify system consistency

### Communication
1. Update status page
2. Notify affected users
3. Document incident
4. Schedule post-mortem

## Files Modified
- `path/to/buggy_file.py` - Fixed the main issue
- `path/to/related_file.js` - Added defensive checks
- `tests/test_bug_fix.py` - Added regression tests

## Related Issues
- Fixes #123
- Related to #456
- Prevents #789

## Post-Fix Actions
- [ ] Update documentation
- [ ] Share learnings with team
- [ ] Update coding guidelines
- [ ] Schedule follow-up review

---
**Fix Status**: Investigating | Fixing | Testing | Review | Deployed | Verified
**Last Updated**: {updated_at}
**Verification Date**: {verification_date}

