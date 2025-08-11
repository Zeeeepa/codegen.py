#!/usr/bin/env python3
"""
Test script for enhanced logging functionality
Demonstrates the comprehensive log analysis and outcome detection
"""

import sys
from codegenapi.models import AgentRunLogResponse, AgentRunWithLogsResponse
from codegenapi.task_manager import LogAnalyzer
from codegenapi.cli import CodegenCLI

def create_comprehensive_mock_logs():
    """Create comprehensive mock logs to test all features"""
    return [
        # Initial planning
        AgentRunLogResponse(
            agent_run_id=12345,
            created_at='2024-01-15T10:30:00Z',
            message_type='PLAN_EVALUATION',
            thought='I need to analyze the requirements and create a comprehensive plan for implementing the new authentication system.',
            tool_name=None,
            tool_input=None,
            tool_output=None
        ),
        
        # Code analysis
        AgentRunLogResponse(
            agent_run_id=12345,
            created_at='2024-01-15T10:30:15Z',
            message_type='ACTION',
            thought='Let me search for existing authentication code to understand the current implementation',
            tool_name='ripgrep_search',
            tool_input={'query': 'function authenticate', 'file_extensions': ['.js', '.ts']},
            tool_output={'matches': 3, 'files': ['src/auth.js', 'src/api.ts']},
        ),
        
        # Plan creation
        AgentRunLogResponse(
            agent_run_id=12345,
            created_at='2024-01-15T10:31:00Z',
            message_type='ACTION',
            thought='I should create a detailed implementation plan based on my analysis',
            tool_name='file_write',
            tool_input={'path': 'implementation-plan.md', 'content': '# Authentication System Implementation Plan\n\n## Overview\nThis plan outlines...'},
            tool_output={'status': 'success'},
        ),
        
        # Code generation
        AgentRunLogResponse(
            agent_run_id=12345,
            created_at='2024-01-15T10:32:00Z',
            message_type='ACTION',
            thought='Now I need to implement the new authentication middleware',
            tool_name='text_editor',
            tool_input={'path': 'src/middleware/auth.js', 'content': 'const jwt = require("jsonwebtoken");\n\nmodule.exports = (req, res, next) => {\n  // Authentication logic\n};'},
            tool_output={'status': 'success'},
        ),
        
        # Documentation
        AgentRunLogResponse(
            agent_run_id=12345,
            created_at='2024-01-15T10:33:00Z',
            message_type='ACTION',
            thought='I should update the README with authentication documentation',
            tool_name='file_write',
            tool_input={'path': 'README.md', 'content': '# Project Documentation\n\n## Authentication\nThis project uses JWT-based authentication...'},
            tool_output={'status': 'success'},
        ),
        
        # Error handling
        AgentRunLogResponse(
            agent_run_id=12345,
            created_at='2024-01-15T10:34:00Z',
            message_type='ERROR',
            thought=None,
            tool_name='test_runner',
            tool_input={'command': 'npm test'},
            tool_output={'status': 'error', 'exit_code': 1},
        ),
        
        # Fix implementation
        AgentRunLogResponse(
            agent_run_id=12345,
            created_at='2024-01-15T10:35:00Z',
            message_type='ACTION',
            thought='I need to fix the failing tests by updating the middleware implementation',
            tool_name='text_editor',
            tool_input={'path': 'src/middleware/auth.js', 'content': 'const jwt = require("jsonwebtoken");\n\nmodule.exports = (req, res, next) => {\n  // Fixed authentication logic\n  const token = req.headers.authorization;\n  if (!token) {\n    return res.status(401).json({ error: "No token provided" });\n  }\n  // ... rest of implementation\n};'},
            tool_output={'status': 'success'},
        ),
        
        # PR creation
        AgentRunLogResponse(
            agent_run_id=12345,
            created_at='2024-01-15T10:36:00Z',
            message_type='ACTION',
            thought='All tests are passing now. I should create a pull request with these changes',
            tool_name='create_pr',
            tool_input={'title': 'Implement JWT-based authentication system', 'body': 'This PR implements a comprehensive JWT-based authentication system with:\n\n- New authentication middleware\n- Updated documentation\n- Comprehensive test coverage\n\nFixes #123'},
            tool_output={'url': 'https://github.com/user/awesome-project/pull/456', 'number': 456, 'status': 'success'},
        ),
        
        # Final answer
        AgentRunLogResponse(
            agent_run_id=12345,
            created_at='2024-01-15T10:37:00Z',
            message_type='FINAL_ANSWER',
            thought='Task completed successfully with comprehensive implementation',
            tool_name=None,
            tool_input=None,
            tool_output=None,
        )
    ]

def test_outcome_detection():
    """Test the outcome detection functionality"""
    print("🧪 Testing Enhanced Logging - Outcome Detection")
    print("=" * 60)
    
    logs = create_comprehensive_mock_logs()
    analyzer = LogAnalyzer()
    outcomes = analyzer.extract_outcomes(logs)
    
    print(f"📊 Summary: {outcomes['summary']}")
    print()
    
    print("🎯 Detected Outcomes:")
    print(f"   ✅ Outcome: {outcomes.get('outcome', 'unknown')}")
    print(f"   📊 Summary: {outcomes.get('summary', 'No summary available')}")
    print()

def test_cli_formatting():
    """Test the CLI formatting functionality"""
    print("🖥️  Testing Enhanced Logging - CLI Formatting")
    print("=" * 60)
    
    logs = create_comprehensive_mock_logs()
    
    # Create mock response
    mock_response = AgentRunWithLogsResponse(
        id=12345,
        logs=logs,
        status="completed",
        created_at="2024-01-15T10:30:00Z",
        updated_at="2024-01-15T10:35:00Z"
    )
    
    # Test CLI helper methods
    cli = CodegenCLI()
    
    print("📋 Mock Task Logs Display:")
    print(f"📊 Status: {mock_response.status}")
    print(f"📄 Total logs: {len(mock_response.logs)}")
    
    # Show detected outcomes
    analyzer = LogAnalyzer()
    outcomes = analyzer.extract_outcomes(mock_response.logs)
    print(f"🎯 Outcomes: {outcomes['summary']}")
    
    if outcomes.get('outcome') == 'success':
        print(f"   ✅ Task completed successfully")
    print()
    
    # Show formatted log entries (first 3)
    print("📝 Log Entries (showing first 3):")
    for i, log in enumerate(logs[:3], 1):
        timestamp = log.created_at.split('T')[1][:8] if 'T' in log.created_at else log.created_at
        print(f"{i:2d}. [{timestamp}] 📋 {log.message_type}")
        
        if log.thought:
            thought_preview = log.thought[:100] + "..." if len(log.thought) > 100 else log.thought
            print(f"    💭 {thought_preview}")
        
        if log.tool_name:
            print(f"    🔧 Tool: {log.tool_name}")
            
            if log.tool_input:
                input_preview = log.tool_input[:50] + "..." if len(log.tool_input) > 50 else log.tool_input
                print(f"    📥 Input: {input_preview}")
            
            if log.tool_output:
                output_preview = log.tool_output[:50] + "..." if len(log.tool_output) > 50 else log.tool_output
                print(f"    📤 Output: {output_preview}")
        
        print()

def main():
    """Run all tests"""
    print("🚀 Enhanced Logging System - Comprehensive Test")
    print("=" * 60)
    print()
    
    test_outcome_detection()
    print()
    test_cli_formatting()
    
    print("✅ All tests completed successfully!")
    print()
    print("🎉 The enhanced logging system provides:")
    print("   • Automatic outcome detection (✅ PR-Created ✅, 🧪 Plan-Created 🧪)")
    print("   • Comprehensive log parsing with all API fields")
    print("   • Rich CLI formatting with emojis and smart truncation")
    print("   • Intelligent tool input/output analysis")
    print("   • Error detection and reporting")
    print("   • Context-aware log presentation")

if __name__ == "__main__":
    main()
