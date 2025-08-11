# Codebase Analysis Template

## Task Context
- **Repository**: {repo_url}
- **Task Type**: CODEBASE_ANALYSIS
- **Priority**: {priority}
- **Assigned**: {assignee}
- **Created**: {created_at}

## Analysis Objective
{query}

## Analysis Framework

### 1. Code Quality Metrics
- **Lines of Code**: Total, per module, per file
- **Cyclomatic Complexity**: Average, maximum, distribution
- **Code Duplication**: Percentage, locations, patterns
- **Test Coverage**: Overall, per module, critical paths
- **Technical Debt**: Estimated hours, priority areas

### 2. Architecture Assessment
- **Design Patterns**: Used patterns, consistency, appropriateness
- **Modularity**: Coupling, cohesion, separation of concerns
- **Dependencies**: Internal, external, circular dependencies
- **Layering**: Architecture layers, violations, improvements

### 3. Code Health Indicators
- **Maintainability Index**: Score and factors
- **Code Smells**: Types, frequency, severity
- **Security Vulnerabilities**: Count, severity, locations
- **Performance Issues**: Bottlenecks, inefficiencies

## Analysis Results

### Executive Summary
- **Overall Health Score**: X/10
- **Key Strengths**: 
- **Critical Issues**: 
- **Recommended Actions**: 

### Detailed Findings

#### Code Quality Analysis
```
Total Lines of Code: X
Average Complexity: X
Duplication Rate: X%
Test Coverage: X%
```

**Quality Distribution by Module:**
| Module | LOC | Complexity | Duplication | Coverage | Score |
|--------|-----|------------|-------------|----------|-------|
| Module A | 1,234 | 5.2 | 2% | 85% | 8/10 |
| Module B | 2,345 | 8.7 | 15% | 60% | 6/10 |

#### Architecture Analysis

**Dependency Graph:**
```
[Visual representation or description of dependencies]
```

**Architecture Violations:**
- Violation 1: Description and impact
- Violation 2: Description and impact

**Design Pattern Usage:**
- Singleton: 5 instances (appropriate: 3, questionable: 2)
- Factory: 8 instances (well-implemented)
- Observer: 3 instances (could be improved)

#### Security Analysis
- **High Severity**: X issues
- **Medium Severity**: X issues
- **Low Severity**: X issues

**Critical Security Issues:**
1. Issue 1: Description, location, impact
2. Issue 2: Description, location, impact

#### Performance Analysis
- **Database Queries**: N+1 problems, slow queries
- **Memory Usage**: Leaks, excessive allocation
- **CPU Usage**: Hot spots, inefficient algorithms
- **Network**: Excessive calls, large payloads

### Code Smells Detected

#### Bloaters
- [ ] Long Method (X instances)
- [ ] Large Class (X instances)
- [ ] Primitive Obsession (X instances)
- [ ] Long Parameter List (X instances)
- [ ] Data Clumps (X instances)

#### Object-Orientation Abusers
- [ ] Switch Statements (X instances)
- [ ] Temporary Field (X instances)
- [ ] Refused Bequest (X instances)
- [ ] Alternative Classes with Different Interfaces (X instances)

#### Change Preventers
- [ ] Divergent Change (X instances)
- [ ] Shotgun Surgery (X instances)

#### Dispensables
- [ ] Comments (X instances)
- [ ] Duplicate Code (X instances)
- [ ] Lazy Class (X instances)
- [ ] Data Class (X instances)
- [ ] Dead Code (X instances)
- [ ] Speculative Generality (X instances)

#### Couplers
- [ ] Feature Envy (X instances)
- [ ] Inappropriate Intimacy (X instances)
- [ ] Message Chains (X instances)
- [ ] Middle Man (X instances)

## Recommendations

### High Priority (Critical)
1. **Issue**: Description
   - **Impact**: High/Medium/Low
   - **Effort**: High/Medium/Low
   - **Action**: Specific steps to resolve
   - **Timeline**: Estimated time to fix

2. **Issue**: Description
   - **Impact**: High/Medium/Low
   - **Effort**: High/Medium/Low
   - **Action**: Specific steps to resolve
   - **Timeline**: Estimated time to fix

### Medium Priority (Important)
1. **Issue**: Description
   - **Impact**: High/Medium/Low
   - **Effort**: High/Medium/Low
   - **Action**: Specific steps to resolve
   - **Timeline**: Estimated time to fix

### Low Priority (Nice to Have)
1. **Issue**: Description
   - **Impact**: High/Medium/Low
   - **Effort**: High/Medium/Low
   - **Action**: Specific steps to resolve
   - **Timeline**: Estimated time to fix

## Improvement Roadmap

### Phase 1: Critical Issues (Weeks 1-2)
- [ ] Fix security vulnerabilities
- [ ] Resolve performance bottlenecks
- [ ] Address architectural violations
- [ ] Improve test coverage for critical paths

### Phase 2: Code Quality (Weeks 3-4)
- [ ] Reduce code duplication
- [ ] Simplify complex methods
- [ ] Improve error handling
- [ ] Add missing documentation

### Phase 3: Architecture Improvements (Weeks 5-8)
- [ ] Refactor tightly coupled modules
- [ ] Implement missing design patterns
- [ ] Improve separation of concerns
- [ ] Optimize dependencies

### Phase 4: Long-term Maintenance (Ongoing)
- [ ] Establish code quality gates
- [ ] Implement automated analysis
- [ ] Regular architecture reviews
- [ ] Continuous refactoring

## Metrics and KPIs

### Before Improvements
- Code Quality Score: X/10
- Technical Debt: X hours
- Test Coverage: X%
- Security Issues: X
- Performance Score: X/10

### Target After Improvements
- Code Quality Score: Y/10
- Technical Debt: Y hours
- Test Coverage: Y%
- Security Issues: Y
- Performance Score: Y/10

## Tools and Analysis Methods

### Static Analysis Tools Used
- [ ] SonarQube/SonarCloud
- [ ] ESLint/Pylint
- [ ] CodeClimate
- [ ] Bandit (Security)
- [ ] Custom scripts

### Metrics Collection
- [ ] Cyclomatic complexity
- [ ] Halstead metrics
- [ ] Maintainability index
- [ ] SLOC (Source Lines of Code)
- [ ] Code churn analysis

### Manual Review Areas
- [ ] Architecture patterns
- [ ] Code organization
- [ ] Documentation quality
- [ ] Test strategy
- [ ] Error handling patterns

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Technical debt accumulation | High | High | Regular refactoring sprints |
| Security vulnerabilities | Medium | High | Security-first development |
| Performance degradation | Medium | Medium | Performance monitoring |
| Maintenance difficulty | High | Medium | Code quality standards |

## Next Steps

### Immediate Actions (This Week)
1. Address critical security issues
2. Fix performance bottlenecks
3. Improve test coverage for core functionality

### Short-term Actions (Next Month)
1. Implement code quality gates
2. Refactor high-complexity modules
3. Establish coding standards

### Long-term Actions (Next Quarter)
1. Architecture modernization
2. Automated quality monitoring
3. Team training and best practices

## Appendices

### A. Detailed Metrics
[Detailed breakdown of all metrics collected]

### B. Code Examples
[Examples of problematic code and suggested improvements]

### C. Tool Configuration
[Configuration files for analysis tools]

### D. Benchmark Comparisons
[Comparison with industry standards or similar projects]

---
**Analysis Status**: In Progress | Complete | Under Review
**Last Updated**: {updated_at}
**Next Review**: {next_review_date}

