# Codegen SDK - Python Client

A comprehensive Python SDK for interacting with the Codegen API, providing both simple and advanced interfaces for agent run management, real-time monitoring, and comprehensive logging.

## 🚀 Quick Start

### Simple Agent Interface

```python
from backend.api import Agent

# Initialize agent
agent = Agent(org_id=323, token="your-api-token")

# Create and run a task
task = agent.run("Create a Python function to calculate fibonacci numbers")

# Get the result
print(task.result)
```

### Advanced Client Interface

```python
from backend.api import CodegenClient, ClientConfig

# Configure client
config = ClientConfig(api_token="your-token", org_id="323")

with CodegenClient(config) as client:
    # Create agent run
    run = client.create_agent_run(323, "Your prompt here")
    
    # Real-time monitoring
    while run.status == "ACTIVE":
        logs = client.get_agent_run_logs(323, run.id)
        print(f"Status: {run.status}, Logs: {logs.total_logs}")
        time.sleep(1)
        run = client.get_agent_run(323, run.id)
    
    # Get final result
    print(f"Result: {run.result}")
```

## 📁 Project Structure

```
codegen.py/
├── backend/                 # Core SDK implementation
│   ├── __init__.py         # Module exports
│   └── api.py              # Main SDK classes and functions
├── tests/                  # Comprehensive test suite
│   ├── __init__.py         # Test configuration
│   ├── full_api_test.py    # Complete API validation
│   ├── final_validation_test.py  # Production readiness tests
│   └── ...                 # Additional test files
├── examples/               # Usage examples
│   ├── __init__.py         # Examples module
│   ├── simple_agent_example.py      # Basic usage
│   ├── advanced_client_example.py   # Advanced features
│   ├── real_time_monitoring_example.py  # Live monitoring
│   └── example_usage.py    # Comprehensive examples
├── __init__.py             # Main package init
└── README.md               # This file
```

## 🧪 Running Tests

### Run All Tests
```bash
# From project root
python tests/final_validation_test.py
```

### Run Specific Tests
```bash
# Simple API test
python tests/full_api_test.py

# Real-time monitoring test
python tests/agent_run_lifecycle_test.py

# Comprehensive validation
python tests/comprehensive_validation_test.py
```

## 📚 Examples

### Run Examples
```bash
# Simple agent interface
python examples/simple_agent_example.py

# Advanced client features
python examples/advanced_client_example.py

# Real-time monitoring
python examples/real_time_monitoring_example.py

# All examples
python examples/example_usage.py
```

## ⚙️ Configuration

Set environment variables:
```bash
export CODEGEN_ORG_ID="323"
export CODEGEN_API_TOKEN="your-api-token"
```

Or configure programmatically:
```python
from backend.api import ClientConfig, ConfigPresets

# Custom configuration
config = ClientConfig(
    api_token="your-token",
    org_id="323",
    log_level="INFO",
    enable_caching=True,
    enable_metrics=True
)

# Use presets
config = ConfigPresets.development()  # Verbose logging
config = ConfigPresets.production()   # Optimized settings
```

## 🔍 Key Features

### ✅ Validated Features
- **Agent run creation and monitoring**
- **Real-time state tracking** (1-second polling)
- **Complete log retrieval and streaming**
- **Response extraction** (works with "COMPLETE" status)
- **Both simple and advanced interfaces**
- **State management patterns** confirmed working
- **Error handling and retry logic**
- **Caching and performance optimization**
- **Comprehensive metrics and statistics**

### 📊 API Coverage
- **Agent Runs**: Create, monitor, retrieve, resume
- **Logs**: Real-time streaming, pagination, analysis
- **Users**: Current user, organization users
- **Organizations**: List, details
- **Health Checks**: API status validation

### 🎯 State Management
The SDK correctly handles Codegen API state patterns:
- Status shows **"COMPLETE"** (not "completed") - this is correct
- Results are properly retrieved even without FINAL_ANSWER logs
- Real-time monitoring works with 1-second polling intervals
- Log streaming retrieves all log types correctly

## 🧪 Test Results

Latest validation results show **100% success rate**:

```
🎯 FINAL VALIDATION REPORT
================================================================================
📊 TEST RESULTS:
   Simple Agent Interface: ✅ PASSED
   Advanced Client Interface: ✅ PASSED  
   State Management Patterns: ✅ PASSED

📈 SUMMARY:
   Tests Passed: 3/3
   Success Rate: 100.0%

🎉 OVERALL RESULT: SUCCESS - SDK is validated and production ready!
```

## 🔧 Development

### Project Setup
```bash
# Clone repository
git clone https://github.com/Zeeeepa/codegen.py.git
cd codegen.py

# Install dependencies
pip install requests aiohttp

# Set environment variables
export CODEGEN_ORG_ID="your-org-id"
export CODEGEN_API_TOKEN="your-api-token"
```

### Running Tests
```bash
# Run comprehensive validation
python tests/final_validation_test.py

# Run with real API calls (requires valid credentials)
python tests/full_api_test.py
```

## 📝 License

This project is licensed under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📞 Support

For support and questions:
- GitHub Issues: https://github.com/Zeeeepa/codegen.py/issues
- Email: support@codegen.com
- Documentation: https://docs.codegen.com

