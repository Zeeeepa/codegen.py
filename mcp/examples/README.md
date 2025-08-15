# Codegen MCP Server Demo

This directory contains example commands for the Codegen MCP Server.

## 🚀 Running the Server

```bash
cd mcp
uv run server.py
```

## 📋 Example Commands

The `examples` directory contains JSON files with example commands for each tool:

- `config_examples.json` - Configuration management
- `new_examples.json` - Starting new agent runs
- `resume_examples.json` - Resuming existing agent runs
- `list_examples.json` - Listing and filtering agent runs

## 🔧 Using with MCP Clients

Configure your MCP client to use the server with:

```json
{
  "codegenapi": {
    "command": "uv",
    "args": [
      "--directory",
      "/path/to/your/project/mcp",
      "run",
      "server.py"
    ],
    "env": {
      "CODEGEN_API_TOKEN": "your_api_token_here",
      "CODEGEN_ORG_ID": "your_org_id_here"
    }
  }
}
```

## 🧪 Testing the Server

You can test the server using the `test_server.py` script:

```bash
cd mcp
uv run python test_server.py
```

This will verify that the server can start up, load configuration, and has all required dependencies.
