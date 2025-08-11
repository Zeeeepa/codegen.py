<!-- TEMPLATE METADATA
Description: Generate comprehensive test suites for existing code
Variables: repository, workspace, priority, custom_message
-->

# Test Generation Task

You are tasked with generating comprehensive tests for the repository: **{repository}**

## Context
- **Repository**: {repository}
- **Workspace**: {workspace}
- **Priority**: {priority}
- **Timestamp**: {timestamp}

## Objective
Create a comprehensive test suite that ensures code quality, reliability, and maintainability:

1. **Test Strategy Planning**
   - Analyze existing codebase and identify testable components
   - Determine appropriate testing levels (unit, integration, e2e)
   - Plan test coverage goals and priorities
   - Select appropriate testing frameworks and tools

2. **Unit Test Generation**
   - Create unit tests for individual functions and methods
   - Test both happy path and edge cases
   - Mock external dependencies appropriately
   - Ensure high code coverage for critical components

3. **Integration Test Development**
   - Test component interactions and data flow
   - Verify API endpoints and database operations
   - Test external service integrations
   - Validate system behavior under various conditions

4. **Test Data Management**
   - Create realistic test data and fixtures
   - Implement test data factories and builders
   - Ensure test isolation and repeatability
   - Handle test database setup and teardown

5. **Test Automation**
   - Set up continuous integration for tests
   - Configure test reporting and coverage metrics
   - Implement test performance monitoring
   - Create test maintenance guidelines

## Testing Guidelines
- **Comprehensive Coverage**: Aim for high test coverage on critical paths
- **Test Quality**: Write clear, maintainable, and reliable tests
- **Performance**: Ensure tests run efficiently and don't slow down development
- **Maintainability**: Structure tests for easy updates and debugging
- **Documentation**: Document test scenarios and expected behaviors

## Test Types to Include
- **Unit Tests**: Individual function and method testing
- **Integration Tests**: Component interaction testing
- **API Tests**: Endpoint validation and contract testing
- **Database Tests**: Data persistence and retrieval testing
- **Error Handling Tests**: Exception and error condition testing
- **Performance Tests**: Load and stress testing (if applicable)

## Deliverables
- Comprehensive test suite with high coverage
- Test documentation and guidelines
- CI/CD integration for automated testing
- Test data management system
- Performance benchmarks and monitoring

## Additional Instructions
{custom_message}

Focus on creating tests that provide confidence in code changes and catch regressions early in the development process.

