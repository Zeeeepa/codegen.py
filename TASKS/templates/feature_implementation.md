# Feature Implementation Template

## Task Context
- **Repository**: {repo_url}
- **Branch**: {target_branch}
- **Task Type**: FEATURE_IMPLEMENTATION
- **Priority**: {priority}
- **Assigned**: {assignee}
- **Created**: {created_at}

## Feature Specification
{query}

## Implementation Checklist

### 1. Pre-Implementation Analysis
- [ ] Review existing codebase architecture
- [ ] Identify affected components and modules
- [ ] Check for existing similar implementations
- [ ] Review coding standards and patterns
- [ ] Identify potential conflicts or dependencies

### 2. Design Phase
- [ ] Create detailed technical design
- [ ] Define API contracts and interfaces
- [ ] Design database schema changes (if applicable)
- [ ] Plan component interactions
- [ ] Design error handling strategy
- [ ] Plan logging and monitoring

### 3. Development Setup
- [ ] Create feature branch: `{target_branch}`
- [ ] Set up development environment
- [ ] Install required dependencies
- [ ] Configure development tools
- [ ] Set up local testing environment

### 4. Core Implementation
- [ ] Implement core functionality
- [ ] Add input validation
- [ ] Implement error handling
- [ ] Add logging and monitoring
- [ ] Implement security measures
- [ ] Add configuration options

### 5. Testing Implementation
- [ ] Write unit tests (target: 90% coverage)
- [ ] Write integration tests
- [ ] Write end-to-end tests
- [ ] Add performance tests (if applicable)
- [ ] Add security tests
- [ ] Test error scenarios

### 6. Documentation
- [ ] Update API documentation
- [ ] Update README if necessary
- [ ] Add inline code documentation
- [ ] Create usage examples
- [ ] Update changelog
- [ ] Update migration guides (if applicable)

### 7. Code Quality
- [ ] Run linting and formatting
- [ ] Perform static code analysis
- [ ] Check test coverage
- [ ] Review performance implications
- [ ] Security scan
- [ ] Dependency audit

### 8. Integration
- [ ] Test with existing features
- [ ] Verify backward compatibility
- [ ] Test database migrations
- [ ] Test deployment process
- [ ] Verify monitoring and alerting

## Implementation Details

### Architecture Changes
```
[Describe any architectural changes or additions]
```

### API Changes
```
[Document new or modified API endpoints]
```

### Database Changes
```sql
-- Add any database schema changes here
```

### Configuration Changes
```yaml
# Add any new configuration options
```

### Dependencies
- New dependencies added:
  - dependency-name: version (reason)
- Dependencies updated:
  - dependency-name: old-version → new-version (reason)

## Testing Strategy

### Unit Tests
- [ ] Test core business logic
- [ ] Test edge cases and error conditions
- [ ] Test input validation
- [ ] Mock external dependencies

### Integration Tests
- [ ] Test API endpoints
- [ ] Test database interactions
- [ ] Test external service integrations
- [ ] Test authentication and authorization

### End-to-End Tests
- [ ] Test complete user workflows
- [ ] Test cross-component interactions
- [ ] Test performance under load
- [ ] Test error recovery scenarios

## Security Considerations
- [ ] Input sanitization and validation
- [ ] Authentication and authorization
- [ ] Data encryption (in transit and at rest)
- [ ] SQL injection prevention
- [ ] XSS prevention
- [ ] CSRF protection
- [ ] Rate limiting
- [ ] Audit logging

## Performance Considerations
- [ ] Database query optimization
- [ ] Caching strategy
- [ ] Memory usage optimization
- [ ] CPU usage optimization
- [ ] Network request optimization
- [ ] Load testing results

## Deployment Checklist
- [ ] Environment variables configured
- [ ] Database migrations ready
- [ ] Feature flags configured
- [ ] Monitoring and alerting set up
- [ ] Rollback plan prepared
- [ ] Documentation updated

## Rollback Plan
1. **Immediate Rollback**:
   - Revert to previous deployment
   - Disable feature flags
   - Rollback database migrations (if safe)

2. **Data Recovery**:
   - Backup current state
   - Restore from backup if necessary
   - Verify data integrity

3. **Communication**:
   - Notify stakeholders
   - Update status page
   - Document lessons learned

## Success Criteria
- [ ] All tests pass
- [ ] Code coverage meets requirements (90%)
- [ ] Performance benchmarks met
- [ ] Security scan passes
- [ ] Documentation complete
- [ ] Peer review approved

## Files Modified
- `path/to/file1.py` - Description of changes
- `path/to/file2.js` - Description of changes
- `path/to/test_file.py` - New test file

## Related Issues/PRs
- Closes #123
- Related to #456
- Depends on #789

---
**Implementation Status**: Not Started | In Progress | Code Complete | Testing | Review | Deployed
**Last Updated**: {updated_at}
**Estimated Completion**: {estimated_completion}

