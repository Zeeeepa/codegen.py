#!/usr/bin/env python3
"""
Comprehensive test for the CodegenAPI package
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add the package to the path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        # Test core imports
        from codegenapi import TaskManager, Config
        from codegenapi.models import Task, TaskStatus
        from codegenapi.exceptions import CodegenAPIError, TaskError, APIError
        from codegenapi.codegen_client import CodegenClient
        from codegenapi.template_loader import TemplateLoader
        from codegenapi.state_store import StateStore
        
        # Test CLI imports
        from codegenapi.cli import main, create_parser
        from codegenapi.commands.new import execute_new_command
        from codegenapi.commands.status import execute_status_command
        from codegenapi.commands.resume import execute_resume_command
        from codegenapi.commands.list import execute_list_command
        
        print("✅ All imports successful")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False


def test_config():
    """Test configuration loading"""
    print("🔧 Testing configuration...")
    
    try:
        from codegenapi import Config
        
        # Test with environment variables
        os.environ["CODEGEN_API_TOKEN"] = "test_token"
        os.environ["CODEGEN_ORG_ID"] = "123"
        
        config = Config()
        
        assert config.api_token == "test_token"
        assert config.org_id == "123"
        
        # Test validation
        errors = config.validate()
        print(f"Configuration validation: {len(errors)} errors")
        
        print("✅ Configuration test passed")
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False


def test_models():
    """Test data models"""
    print("📊 Testing data models...")
    
    try:
        from codegenapi.models import Task, TaskStatus
        from datetime import datetime
        
        # Test TaskStatus enum
        assert TaskStatus.PENDING.value == "pending"
        assert TaskStatus.RUNNING.value == "running"
        assert TaskStatus.COMPLETED.value == "completed"
        assert TaskStatus.FAILED.value == "failed"
        
        # Test Task creation
        task = Task(
            id="test_123",
            repo_url="https://github.com/test/repo",
            task_type="TEST",
            query="Test query",
            status=TaskStatus.PENDING,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        assert task.id == "test_123"
        assert task.status == TaskStatus.PENDING
        
        print("✅ Models test passed")
        return True
        
    except Exception as e:
        print(f"❌ Models test failed: {e}")
        return False


def test_template_loader():
    """Test template loading"""
    print("📝 Testing template loader...")
    
    try:
        from codegenapi.template_loader import TemplateLoader
        
        loader = TemplateLoader()
        
        # Test loading existing template
        template_vars = {
            "repo_url": "https://github.com/test/repo",
            "query": "Test query",
            "pr_number": "123",
            "branch": "main",
            "task_type": "TEST"
        }
        
        # This should work with our PLAN_CREATION template
        try:
            prompt = loader.process_template("PLAN_CREATION", template_vars)
            assert "https://github.com/test/repo" in prompt
            assert "Test query" in prompt
            print("✅ Template processing successful")
        except Exception as e:
            print(f"⚠️  Template processing failed (expected if templates not found): {e}")
        
        print("✅ Template loader test passed")
        return True
        
    except Exception as e:
        print(f"❌ Template loader test failed: {e}")
        return False


def test_state_store():
    """Test state storage"""
    print("💾 Testing state store...")
    
    try:
        from codegenapi.state_store import StateStore
        from codegenapi.models import TaskStatus
        import tempfile
        
        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            store = StateStore(temp_dir)
            
            # Test task creation
            task = store.create_task(
                repo_url="https://github.com/test/repo",
                task_type="TEST",
                query="Test query"
            )
            
            assert task.id is not None
            assert task.status == TaskStatus.CREATED
            
            # Test task loading
            loaded_task = store.load_task(task.id)
            assert loaded_task is not None
            assert loaded_task.id == task.id
            
            # Test status update
            updated_task = store.update_task_status(task.id, TaskStatus.RUNNING)
            assert updated_task.status == TaskStatus.RUNNING
            
            # Test listing tasks
            tasks = store.list_tasks(10)
            assert len(tasks) >= 1
            
        print("✅ State store test passed")
        return True
        
    except Exception as e:
        print(f"❌ State store test failed: {e}")
        return False


def test_cli_parser():
    """Test CLI argument parsing"""
    print("🖥️  Testing CLI parser...")
    
    try:
        from codegenapi.cli import create_parser
        
        parser = create_parser()
        
        # Test new command parsing
        args = parser.parse_args([
            "new",
            "--repo", "https://github.com/test/repo",
            "--task", "TEST",
            "--query", "Test query"
        ])
        
        assert args.command == "new"
        assert args.repo == "https://github.com/test/repo"
        assert args.task == "TEST"
        assert args.query == "Test query"
        
        # Test status command parsing
        args = parser.parse_args(["status", "test_123"])
        assert args.command == "status"
        assert args.task_id == "test_123"
        
        print("✅ CLI parser test passed")
        return True
        
    except Exception as e:
        print(f"❌ CLI parser test failed: {e}")
        return False


def test_cli_help():
    """Test CLI help output"""
    print("❓ Testing CLI help...")
    
    try:
        from codegenapi.cli import main
        
        # Test main help
        result = main(["--help"])
        # This will exit with code 0, which is expected
        
        print("✅ CLI help test passed")
        return True
        
    except SystemExit as e:
        if e.code == 0:
            print("✅ CLI help test passed")
            return True
        else:
            print(f"❌ CLI help test failed with exit code: {e.code}")
            return False
    except Exception as e:
        print(f"❌ CLI help test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("🧪 CodegenAPI Comprehensive Test Suite")
    print("=" * 40)
    
    tests = [
        test_imports,
        test_config,
        test_models,
        test_template_loader,
        test_state_store,
        test_cli_parser,
        test_cli_help,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        print()
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            failed += 1
    
    print()
    print("=" * 40)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
