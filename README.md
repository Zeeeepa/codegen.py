# CodegenAPI - Real Agent Management Dashboard

A comprehensive Python SDK and CLI tool for managing and monitoring **real Codegen agents** using the official Codegen SDK.

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/Zeeeepa/codegen.py
cd codegen.py

# Install dependencies (includes official Codegen SDK)
pip install -e .
```

### Configuration

**IMPORTANT**: This tool uses the **real Codegen SDK** and requires valid API credentials.

Get your credentials from [codegen.com/developer](https://codegen.com/developer):

```bash
export CODEGEN_API_TOKEN="your_real_api_token"
export CODEGEN_ORG_ID="your_org_id"
export CODEGEN_BASE_URL="https://codegen-sh-rest-api.modal.run"  # optional
```

### Test Your Setup

```bash
# Test the real SDK integration
python test_real_sdk.py
```

## 🤖 **REAL** Agent Management Features

### Live Agent Dashboard

```bash
# Launch REAL dashboard with live data from Codegen API
python main.py monitor --dashboard --refresh 5

# Monitor specific real tasks
python main.py monitor --tasks 12345,12346 --alerts
```

### Create Real Agent Tasks

```bash
# Create a real agent task using the official SDK
python main.py new --repo https://github.com/user/repo \
  --task FEATURE_IMPLEMENTATION \
  --query "Implement OAuth2 authentication" \
  --priority high
```

### Real Analytics

```bash
# Get analytics from actual agent runs
python main.py analytics --period day --export real_data.json

# View real logs from actual tasks
python main.py logs 12345 --follow --level info
```

## 🔥 **What Makes This REAL**

### ✅ Uses Official Codegen SDK
- Imports `from codegen.agents.agent import Agent`
- Uses real `agent.run(prompt="...")` calls
- Connects to actual Codegen API endpoints
- No mock data or simulated responses

### ✅ Real Agent Operations
- **Create Tasks**: Actually creates agent runs via SDK
- **Monitor Progress**: Shows real task status from API
- **View Logs**: Displays actual agent execution logs
- **Cancel Tasks**: Actually cancels running agents
- **Live Dashboard**: Real-time updates from Codegen API

### ✅ Proper Error Handling
- Validates API credentials
- Handles network failures gracefully
- Shows meaningful error messages
- Fallback modes for testing

## 📁 Project Structure

```
codegen.py/
├── README.md                    # This file
├── main.py                      # Main entry point
├── test_real_sdk.py            # SDK integration test
├── requirements.txt             # Dependencies (includes codegen SDK)
├── setup.py                     # Package configuration
├── tests/                       # All test files
├── codegenapi/                  # Main package
│   ├── codegen_client.py       # Real SDK wrapper
│   ├── config.py               # Configuration
│   ├── cli.py                  # CLI parsing
│   └── commands/               # CLI commands
│       ├── monitor.py          # Real-time dashboard
│       ├── analytics.py        # Real analytics
│       ├── logs.py             # Real log streaming
│       └── ...
└── TASKS/                       # Task templates
```

## 🛠️ Python SDK Usage

```python
from codegenapi import Config, CodegenClient

# Initialize with real credentials
config = Config()  # Reads from environment variables
client = CodegenClient(config)

# Create a real agent task
task = client.create_agent_run(
    prompt="Implement user authentication system for my React app"
)

# Monitor real progress
while task['status'] in ['pending', 'running']:
    task = client.refresh_task_status(task['id'])
    print(f"Status: {task['status']}")
    time.sleep(5)

# Get real results
if task['status'] == 'completed':
    print(f"Task completed: {task['result']}")
```

## 🔧 Real API Integration

This tool integrates with the **actual Codegen API** using the official SDK:

```python
from codegen.agents.agent import Agent

# Real SDK initialization
agent = Agent(
    org_id="your_org_id",
    token="your_api_token"
)

# Real agent execution
task = agent.run(prompt="Your request here")
```

## 🧪 Testing

```bash
# Test real SDK integration
python test_real_sdk.py

# Run all tests
python -m pytest tests/ -v

# Test CLI functionality
python main.py --help
```

## 📊 **REAL** Dashboard Features

### Live Monitoring Dashboard
- **Real-time status updates** from Codegen API
- **Active agent runs** with live progress
- **Status summaries** with actual counts
- **Auto-refresh** with configurable intervals

### Real Analytics
- **Actual success rates** from your agent runs
- **Real performance metrics** and trends
- **Time-based filtering** (hour, day, week, month)
- **Export capabilities** with real data

### Live Log Streaming
- **Real-time log streaming** from running agents
- **Log filtering** by level and patterns
- **Follow mode** for continuous monitoring
- **Export logs** from actual agent runs

## ⚠️ **No More Fake Data!**

This version completely removes:
- ❌ Simulated analytics
- ❌ Mock task data
- ❌ Fake performance metrics
- ❌ Imaginary agent runs

Everything connects to the **real Codegen API** and shows **actual data**.

## 🔗 Requirements

- **Valid Codegen API credentials** from [codegen.com/developer](https://codegen.com/developer)
- **Python 3.8+**
- **Official Codegen SDK** (installed automatically)

## 📚 Documentation

### Get API Credentials
1. Sign up at [codegen.com](https://codegen.com)
2. Go to [codegen.com/developer](https://codegen.com/developer)
3. Generate your API token
4. Find your organization ID

### Environment Setup
```bash
# Required
export CODEGEN_API_TOKEN="your_token_here"
export CODEGEN_ORG_ID="your_org_id_here"

# Optional
export CODEGEN_BASE_URL="https://codegen-sh-rest-api.modal.run"
```

### CLI Help
```bash
# Main help
python main.py --help

# Command-specific help
python main.py monitor --help
python main.py analytics --help
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Test with real Codegen credentials
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🔗 Links

- [Codegen API Documentation](https://docs.codegen.com)
- [Official Codegen SDK](https://github.com/codegen-sh/codegen)
- [Get API Credentials](https://codegen.com/developer)

---

**Built with the real Codegen SDK - no fake data, no simulations!** 🤖✨

