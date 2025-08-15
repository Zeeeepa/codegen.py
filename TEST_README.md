# Codegen API Test Suite

This directory contains test scripts for the Codegen API Python client.

## Test Files

1. `test_codegen_api.py` - Basic test script that verifies:
   - Module imports work correctly
   - Agent class can be initialized
   - MCP tool integration is functioning

2. `test_codegen_api_mock.py` - Mock-based unit tests that verify:
   - Agent initialization with mocked client
   - Agent.run functionality
   - Task properties and methods
   - Task.wait_for_completion functionality

## Running the Tests

### Basic Test

```bash
python test_codegen_api.py
```

This test will attempt to initialize the Agent class with environment variables if available, and with explicit parameters. It will also verify that the module can be imported and the Agent class is accessible.

### Mock Tests

```bash
python test_codegen_api_mock.py
```

These tests use Python's unittest framework with mocked responses to test the functionality of the Agent and Task classes without requiring actual API credentials.

## Test Results

### Basic Test

The basic test will output:
- Python version
- Environment variable status (redacted for security)
- Agent initialization test results
- MCP integration test results

### Mock Tests

The mock tests will run a series of unit tests and report:
- Number of tests run
- Number of tests passed/failed
- Any errors or failures

## MCP Integration

These tests confirm that the Codegen API client can be successfully executed from an MCP tool. The successful execution of these test scripts demonstrates that:

1. The MCP tool can execute Python scripts
2. The scripts can import the Codegen API module
3. The module's classes and functions are accessible
4. The basic functionality works as expected

## Next Steps

For more comprehensive testing, consider:

1. Setting up integration tests with actual API credentials
2. Testing asynchronous functionality
3. Testing error handling and edge cases
4. Adding more mock tests for other client methods

