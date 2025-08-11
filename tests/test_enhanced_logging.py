#!/usr/bin/env python3
"""
Test script for enhanced logging functionality
Demonstrates the comprehensive log analysis and outcome detection
"""

import sys
from codegen_api import AgentRunLogResponse, AgentRunWithLogsResponse, LogAnalyzer
from cli import CodegenCLI

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
            tool_output=None,
            observation='Starting analysis of authentication requirements'
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
            observation={'status': 'success', 'results': ['Found 3 matches in authentication files']}
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
            observation='Implementation plan created successfully'
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
            observation='Authentication middleware created'
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
            observation='README updated with authentication documentation'
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
            observation='Test failed: Authentication middleware test suite failed with 2 failing tests'
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
            observation='Authentication middleware updated with proper error handling'
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
            observation='Successfully created PR #456: Implement JWT-based authentication system'
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
            observation='I have successfully implemented a JWT-based authentication system with:\n\n✅ Created implementation plan (implementation-plan.md)\n✅ Implemented authentication middleware (src/middleware/auth.js)\n✅ Updated documentation (README.md)\n✅ Fixed failing tests\n✅ Created PR #456 (https://github.com/user/awesome-project/pull/456)\n\nThe authentication system is now ready for review and deployment.'
        )
    ]

def test_outcome_detection():
    """Test the outcome detection functionality"""
    print("🧪 Testing Enhanced Logging - Outcome Detection")
    print("=" * 60)
    
    logs = create_comprehensive_mock_logs()
    outcomes = LogAnalyzer.detect_outcomes(logs)
    
    print(f"📊 Summary: {outcomes.summary}")
    print()
    
    print("🎯 Detected Outcomes:")
    print(f"   ✅ PR Created: {outcomes.pr_created}")
    if outcomes.pr_urls:
        print(f"      📋 URLs: {', '.join(outcomes.pr_urls)}")
    
    print(f"   🧪 Plan Created: {outcomes.plan_created}")
    if outcomes.plan_files:
        print(f"      📝 Files: {', '.join(outcomes.plan_files)}")
    
    print(f"   💻 Code Generated: {outcomes.code_generated}")
    if outcomes.code_files:
        print(f"      📁 Files: {', '.join(outcomes.code_files)}")
    
    print(f"   📚 Documentation Created: {outcomes.documentation_created}")
    if outcomes.doc_files:
        print(f"      📄 Files: {', '.join(outcomes.doc_files)}")
    
    print(f"   ❌ Errors Encountered: {outcomes.errors_encountered}")
    if outcomes.error_messages:
        print(f"      🚨 Messages: {len(outcomes.error_messages)} errors")
    
    print(f"   🔧 Tools Used: {', '.join(outcomes.tools_used)}")
    print()

def test_cli_formatting():
    """Test the CLI formatting functionality"""
    print("🖥️  Testing Enhanced Logging - CLI Formatting")
    print("=" * 60)
    
    logs = create_comprehensive_mock_logs()
    
    # Create mock response
    mock_response = AgentRunWithLogsResponse(
        id=12345,
        organization_id=67890,
        logs=logs,
        status="completed",
        created_at="2024-01-15T10:30:00Z",
        web_url="https://app.codegen.com/agent/trace/12345",
        result="Authentication system implemented successfully",
        metadata={"task_type": "FEATURE_IMPLEMENTATION"},
        total_logs=len(logs),
        page=1,
        size=100,
        pages=1
    )
    
    # Test CLI helper methods
    cli = CodegenCLI()
    
    print("📋 Mock Task Logs Display:")
    print(f"📊 Status: {mock_response.status}")
    print(f"📄 Total logs: {mock_response.total_logs}")
    
    # Show detected outcomes
    outcomes = mock_response.detected_outcomes
    print(f"🎯 Outcomes: {outcomes.summary}")
    
    if outcomes.pr_created and outcomes.pr_urls:
        print(f"   📋 PRs: {', '.join(outcomes.pr_urls)}")
    if outcomes.plan_created and outcomes.plan_files:
        print(f"   📝 Plans: {', '.join(outcomes.plan_files)}")
    if outcomes.code_generated and outcomes.code_files:
        print(f"   💻 Code: {', '.join(outcomes.code_files[:3])}{'...' if len(outcomes.code_files) > 3 else ''}")
    if outcomes.documentation_created and outcomes.doc_files:
        print(f"   📚 Docs: {', '.join(outcomes.doc_files[:3])}{'...' if len(outcomes.doc_files) > 3 else ''}")
    if outcomes.errors_encountered:
        print(f"   ❌ Errors: {len(outcomes.error_messages)} found")
    
    print(f"🔧 Tools used: {', '.join(outcomes.tools_used[:5])}{'...' if len(outcomes.tools_used) > 5 else ''}")
    print()
    
    # Show formatted log entries (first 3)
    print("📝 Log Entries (showing first 3):")
    for i, log in enumerate(logs[:3], 1):
        timestamp = log.created_at.split('T')[1][:8] if 'T' in log.created_at else log.created_at
        type_emoji = cli._get_message_type_emoji(log.message_type)
        print(f"{i:2d}. [{timestamp}] {type_emoji} {log.message_type}")
        
        if log.thought:
            thought_preview = log.thought[:100] + "..." if len(log.thought) > 100 else log.thought
            print(f"    💭 {thought_preview}")
        
        if log.tool_name:
            print(f"    🔧 Tool: {log.tool_name}")
            
            if log.tool_input:
                key_inputs = cli._extract_key_inputs(log.tool_input)
                if key_inputs:
                    print(f"    📥 Input: {key_inputs}")
            
            if log.tool_output:
                result_summary = cli._extract_tool_result(log.tool_output)
                if result_summary:
                    print(f"    📤 Output: {result_summary}")
        
        if log.observation:
            obs_text = str(log.observation)
            if len(obs_text) > 150:
                obs_text = obs_text[:150] + "..."
            print(f"    👁️  Observation: {obs_text}")
        
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
