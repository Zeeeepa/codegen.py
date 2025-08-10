# Codegen Agent Run Management System

Complete FastAPI backend and Reflex UI dashboard for managing Codegen agent runs with full logging and monitoring capabilities.

## 🚀 Features

### ✅ **Unified Backend API (`api.py`)**
- **Official SDK Compatibility**: Supports both official and comprehensive SDK patterns
- **Complete Agent Run Management**: Create, retrieve, list, resume, and monitor runs
- **Agent Run Logs API**: Full access to detailed execution logs with pagination
- **Environment Variable Configuration**: Secure credential management
- **FastAPI Documentation**: Auto-generated interactive API docs

### ✅ **Reflex UI Dashboard (`dashboard.py`)**
- **Environment Variable Management**: Set API token and org ID through UI
- **Agent Run Cards**: Visual cards showing status, prompts, and actions
- **Real-time Log Viewing**: Detailed logs with thought processes and tool usage
- **Resume Functionality**: Resume completed/failed runs with new prompts
- **Pagination**: Navigate through large lists of agent runs
- **Responsive Design**: Modern, clean interface

### ✅ **Key Capabilities**
- 🔄 **Resume Agent Runs**: Continue from where previous runs left off
- 📊 **Detailed Logging**: View agent thoughts, tool usage, and execution flow
- 🎯 **Status Monitoring**: Real-time status updates and progress tracking
- 🔧 **Environment Management**: Easy credential configuration
- 📱 **Mobile-Friendly**: Responsive design works on all devices

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/Zeeeepa/codegen.py.git
cd codegen.py

# Install dependencies
pip install -r requirements.txt

# Or install individual packages
pip install fastapi uvicorn reflex python-dotenv requests
```

## ⚙️ Configuration

### Method 1: Environment Variables
```bash
export CODEGEN_API_TOKEN="sk-your-token-here"
export CODEGEN_ORG_ID="your-org-id"
```

### Method 2: .env File
Create a `.env` file in the project root:
```env
CODEGEN_API_TOKEN=sk-your-token-here
CODEGEN_ORG_ID=your-org-id
CODEGEN_BASE_URL=https://api.codegen.com/v1
```

### Method 3: UI Settings Panel
Configure credentials directly through the dashboard settings panel.

## 🚀 Quick Start

### 1. Start the Backend API
```bash
python api.py
```
- **API Server**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

### 2. Start the Dashboard (New Terminal)
```bash
python dashboard.py
```
- **Dashboard**: http://localhost:3000

### 3. Configure Credentials
- Click "Settings" in the dashboard
- Enter your API token and organization ID
- Click "Save Settings"

## 📚 API Endpoints

### **Core Endpoints**
- `GET /health` - Health check with configuration status
- `GET /users/me` - Current user information
- `GET /agent_runs` - List agent runs (paginated)
- `POST /agent_runs` - Create new agent run
- `GET /agent_runs/{id}` - Get specific agent run details
- `GET /agent_runs/{id}/logs` - Get agent run logs (paginated)
- `POST /agent_runs/{id}/resume` - Resume an agent run

### **Path-Based Endpoints**
- `POST /create_agent_run/{mode}/{query}` - Create run with path parameters
- `POST /resume_agent_run/{id}/{query}` - Resume run with path parameters

### **Legacy Compatibility**
- `GET /status` - Get current task status (official SDK compatibility)

## 🎯 Usage Examples

### **Using the API Directly**

#### Create Agent Run
```bash
curl -X POST "http://localhost:8000/agent_runs" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Create a Python function that calculates fibonacci numbers"}'
```

#### Get Agent Run Logs
```bash
curl "http://localhost:8000/agent_runs/12345/logs?limit=50"
```

#### Resume Agent Run
```bash
curl -X POST "http://localhost:8000/agent_runs/12345/resume" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Add error handling to the function"}'
```

### **Using the Python SDK**

#### Official SDK Pattern
```python
from api import CodegenClient

client = CodegenClient()

# Create agent run
run = client.create_agent_run("Write a hello world function")
print(f"Created run {run['id']} with status {run['status']}")

# Get logs
logs = client.get_agent_run_logs(run['id'])
for log in logs['logs']:
    print(f"[{log['message_type']}] {log.get('thought', '')}")

# Resume run
resumed = client.resume_agent_run(run['id'], "Add documentation")
```

#### Context Manager Pattern
```python
from api import CodegenClient

with CodegenClient() as client:
    task = client.run("Create a REST API endpoint")
    task.refresh()
    print(f"Status: {task.status}")
```

## 🔍 Agent Run Logs API

The logs API provides detailed insights into agent execution:

### **Log Types**
- **ACTION**: Tool executions (file operations, searches, etc.)
- **PLAN_EVALUATION**: Agent reasoning and planning
- **FINAL_ANSWER**: Agent's final response
- **ERROR**: Execution errors
- **USER_MESSAGE**: User interactions

### **Log Fields**
- `thought`: Agent's internal reasoning
- `tool_name`: Name of executed tool
- `tool_input`: Parameters passed to tool
- `tool_output`: Tool execution results
- `observation`: Agent's observation of results

### **Example Log Entry**
```json
{
  "agent_run_id": 12345,
  "created_at": "2024-01-15T10:30:15Z",
  "message_type": "ACTION",
  "thought": "I need to search for the user's function in the codebase",
  "tool_name": "ripgrep_search",
  "tool_input": {
    "query": "function getUserData",
    "file_extensions": [".js", ".ts"]
  },
  "tool_output": {
    "matches": 3,
    "files": ["src/user.js", "src/api.ts"]
  },
  "observation": {
    "status": "success",
    "results": ["Found 3 matches..."]
  }
}
```

## 🎨 Dashboard Features

### **Main Dashboard**
- **Agent Run Cards**: Visual representation of all runs
- **Status Badges**: Color-coded status indicators
- **Quick Actions**: View logs, resume runs, visit Codegen
- **Pagination**: Navigate through large lists

### **Log Viewer**
- **Detailed Logs**: Full execution timeline
- **Thought Processes**: See agent reasoning
- **Tool Usage**: Track all tool executions
- **Error Tracking**: Identify and debug issues

### **Settings Panel**
- **Credential Management**: Secure token and org ID storage
- **Environment Variables**: Automatic .env file generation
- **Configuration Validation**: Real-time validation

## 🔧 Development

### **Project Structure**
```
codegen.py/
├── api.py                 # Unified FastAPI backend
├── dashboard.py           # Reflex UI dashboard
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (create this)
└── README_COMPLETE.md     # This documentation
```

### **Running in Development**
```bash
# Backend with auto-reload
python api.py

# Dashboard with auto-reload
python dashboard.py
```

### **Testing the API**
```bash
# Test health endpoint
curl http://localhost:8000/health

# Test with your credentials
curl -H "Authorization: Bearer your-token" \
     http://localhost:8000/users/me
```

## 🚨 Important Notes

### **API Endpoint Discovery**
- ❌ **Official docs URL**: `https://codegen-sh-rest-api.modal.run` (returns 404)
- ✅ **Working URL**: `https://api.codegen.com/v1` (fully functional)

### **SDK Compatibility**
The system supports both patterns:
```python
# Official pattern (from documentation)
from codegen.agents.agent import Agent
agent = Agent(token="...", org_id="323")

# Comprehensive pattern (this implementation)
from api import CodegenClient
client = CodegenClient()
```

### **Security**
- API tokens are stored securely in environment variables
- The dashboard saves credentials to `.env` file
- All API requests use proper authentication headers

## 🎯 Use Cases

### **Development Teams**
- Monitor agent runs across projects
- Debug failed executions with detailed logs
- Resume interrupted workflows
- Track agent performance and usage

### **Individual Developers**
- Manage personal agent runs
- Experiment with different prompts
- Learn from agent reasoning processes
- Build on previous work by resuming runs

### **CI/CD Integration**
- Automate agent run creation
- Monitor execution status
- Integrate with deployment pipelines
- Generate reports from logs

## 🔗 Links

- **API Documentation**: http://localhost:8000/docs
- **Dashboard**: http://localhost:3000
- **Health Check**: http://localhost:8000/health
- **Codegen Platform**: https://codegen.com

## 📝 License

This project is open source and available under the MIT License.

---

**Ready to manage your Codegen agent runs like a pro!** 🚀

Start both servers and visit the dashboard to begin creating and monitoring your agent runs with full logging capabilities.
