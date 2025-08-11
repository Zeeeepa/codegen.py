#!/usr/bin/env python3
"""
Complete Dashboard Validation
Tests the complete real dashboard functionality end-to-end.
"""

import sys
import os
import time
import json
import traceback
from datetime import datetime
from typing import Dict, List, Any
import logging

# Add parent directories to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from services.real_api_service import RealCodegenAPI

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CompleteDashboardValidator:
    """Complete dashboard functionality validator using real API"""
    
    def __init__(self):
        self.api = RealCodegenAPI()
        self.test_results = []
        self.start_time = datetime.now()
        
    def log_test(self, test_name: str, success: bool, details: str = "", duration: float = 0):
        """Log test result"""
        result = {
            'test_name': test_name,
            'success': success,
            'details': details,
            'duration': duration,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{status} {test_name} ({duration:.3f}s) - {details}")
    
    def test_dashboard_data_loading(self) -> bool:
        """Test dashboard data loading functionality"""
        start_time = time.time()
        
        try:
            # Test all data sources the dashboard needs
            
            # 1. User authentication
            user = self.api.get_current_user()
            user_ok = user and hasattr(user, 'github_username')
            
            # 2. Organizations
            orgs = self.api.get_organizations()
            orgs_ok = orgs and len(orgs) > 0
            
            # 3. Agent runs listing
            runs = self.api.list_agent_runs(323, limit=10)
            runs_ok = runs and 'items' in runs and len(runs['items']) > 0
            
            # 4. Projects
            projects = self.api.get_projects(323)
            projects_ok = projects and len(projects) > 0
            
            # 5. Statistics
            stats = self.api.get_run_statistics(323, days=7)
            stats_ok = stats and 'total_runs' in stats
            
            all_data_loaded = all([user_ok, orgs_ok, runs_ok, projects_ok, stats_ok])
            
            details = f"User: {'✓' if user_ok else '✗'}, Orgs: {'✓' if orgs_ok else '✗'}, Runs: {'✓' if runs_ok else '✗'}, Projects: {'✓' if projects_ok else '✗'}, Stats: {'✓' if stats_ok else '✗'}"
            
            self.log_test(
                "Dashboard Data Loading",
                all_data_loaded,
                details,
                time.time() - start_time
            )
            return all_data_loaded
            
        except Exception as e:
            self.log_test(
                "Dashboard Data Loading",
                False,
                f"Data loading failed: {str(e)}",
                time.time() - start_time
            )
            return False
    
    def test_run_management_operations(self) -> bool:
        """Test run management operations"""
        start_time = time.time()
        
        try:
            # Create a test run
            test_prompt = f"Complete dashboard validation test - {datetime.now().isoformat()}"
            new_run = self.api.create_agent_run(323, test_prompt, metadata={"test": "complete_validation"})
            
            if not new_run or 'id' not in new_run:
                self.log_test(
                    "Run Management Operations",
                    False,
                    "Failed to create test run",
                    time.time() - start_time
                )
                return False
            
            run_id = new_run['id']
            operations = []
            
            # Test get run details
            try:
                run_details = self.api.get_agent_run(323, run_id)
                operations.append(f"get_details: {'✓' if run_details else '✗'}")
            except Exception as e:
                operations.append(f"get_details: ✗ ({str(e)[:30]})")
            
            # Test resume operation (this should work)
            try:
                resume_result = self.api.resume_agent_run(323, run_id, "Continue test")
                operations.append(f"resume: {'✓' if resume_result else '✗'}")
            except Exception as e:
                operations.append(f"resume: ✗ ({str(e)[:30]})")
            
            # Test cancel operation
            try:
                cancel_result = self.api.cancel_agent_run(323, run_id)
                operations.append(f"cancel: {'✓' if cancel_result else '✗'}")
            except Exception as e:
                operations.append(f"cancel: ✗ ({str(e)[:30]})")
            
            # Consider successful if at least 2 operations work
            success_count = sum(1 for op in operations if '✓' in op)
            success = success_count >= 2
            
            self.log_test(
                "Run Management Operations",
                success,
                f"Operations: {', '.join(operations)} ({success_count}/3 successful)",
                time.time() - start_time
            )
            return success
            
        except Exception as e:
            self.log_test(
                "Run Management Operations",
                False,
                f"Management operations failed: {str(e)}",
                time.time() - start_time
            )
            return False
    
    def test_filtering_and_search(self) -> bool:
        """Test filtering and search functionality"""
        start_time = time.time()
        
        try:
            # Test status filtering
            all_runs = self.api.list_agent_runs(323, limit=20)
            active_runs = self.api.list_agent_runs(323, limit=20, status='ACTIVE')
            complete_runs = self.api.list_agent_runs(323, limit=20, status='COMPLETE')
            
            filtering_works = (
                len(active_runs['items']) <= len(all_runs['items']) and
                len(complete_runs['items']) <= len(all_runs['items'])
            )
            
            # Test search functionality
            search_results = self.api.search_runs(323, "test", limit=5)
            search_works = isinstance(search_results, list)
            
            # Test pagination
            page1 = self.api.list_agent_runs(323, limit=5, skip=0)
            page2 = self.api.list_agent_runs(323, limit=5, skip=5)
            pagination_works = (
                len(page1['items']) <= 5 and
                len(page2['items']) <= 5
            )
            
            all_features_work = filtering_works and search_works and pagination_works
            
            details = f"Filtering: {'✓' if filtering_works else '✗'}, Search: {'✓' if search_works else '✗'}, Pagination: {'✓' if pagination_works else '✗'}"
            
            self.log_test(
                "Filtering and Search",
                all_features_work,
                details,
                time.time() - start_time
            )
            return all_features_work
            
        except Exception as e:
            self.log_test(
                "Filtering and Search",
                False,
                f"Filtering and search failed: {str(e)}",
                time.time() - start_time
            )
            return False
    
    def test_analytics_and_statistics(self) -> bool:
        """Test analytics and statistics functionality"""
        start_time = time.time()
        
        try:
            # Test statistics for different periods
            stats_7d = self.api.get_run_statistics(323, days=7)
            stats_30d = self.api.get_run_statistics(323, days=30)
            
            stats_work = (
                stats_7d and 'total_runs' in stats_7d and
                stats_30d and 'total_runs' in stats_30d
            )
            
            # Test project data
            projects = self.api.get_projects(323)
            projects_work = projects and len(projects) > 0
            
            # Test data structure completeness
            required_fields = ['total_runs', 'status_breakdown', 'success_rate', 'total_cost']
            stats_complete = all(field in stats_7d for field in required_fields)
            
            all_analytics_work = stats_work and projects_work and stats_complete
            
            details = f"Stats: {'✓' if stats_work else '✗'}, Projects: {'✓' if projects_work else '✗'}, Complete: {'✓' if stats_complete else '✗'}"
            
            self.log_test(
                "Analytics and Statistics",
                all_analytics_work,
                details,
                time.time() - start_time
            )
            return all_analytics_work
            
        except Exception as e:
            self.log_test(
                "Analytics and Statistics",
                False,
                f"Analytics failed: {str(e)}",
                time.time() - start_time
            )
            return False
    
    def test_real_time_data_updates(self) -> bool:
        """Test real-time data update capability"""
        start_time = time.time()
        
        try:
            # Get initial state
            initial_runs = self.api.list_agent_runs(323, limit=5)
            initial_count = len(initial_runs['items'])
            
            # Create a new run
            new_run = self.api.create_agent_run(
                323,
                "Real-time update test",
                metadata={"test": "realtime"}
            )
            
            if not new_run:
                self.log_test(
                    "Real-time Data Updates",
                    False,
                    "Could not create test run for real-time test",
                    time.time() - start_time
                )
                return False
            
            # Wait a moment and check if the new run appears
            time.sleep(2)
            updated_runs = self.api.list_agent_runs(323, limit=5)
            updated_count = len(updated_runs['items'])
            
            # Check if we can see the new run
            new_run_visible = any(run['id'] == new_run['id'] for run in updated_runs['items'])
            
            # Test getting specific run details
            run_details = self.api.get_agent_run(323, new_run['id'])
            details_available = run_details and run_details['id'] == new_run['id']
            
            real_time_works = new_run_visible and details_available
            
            details = f"New run visible: {'✓' if new_run_visible else '✗'}, Details available: {'✓' if details_available else '✗'}"
            
            self.log_test(
                "Real-time Data Updates",
                real_time_works,
                details,
                time.time() - start_time
            )
            return real_time_works
            
        except Exception as e:
            self.log_test(
                "Real-time Data Updates",
                False,
                f"Real-time updates failed: {str(e)}",
                time.time() - start_time
            )
            return False
    
    def test_error_handling_and_resilience(self) -> bool:
        """Test error handling and system resilience"""
        start_time = time.time()
        
        try:
            error_handling_tests = []
            
            # Test invalid run ID
            try:
                invalid_run = self.api.get_agent_run(323, 999999)
                error_handling_tests.append("invalid_run_id: ✗ (no error)")
            except Exception:
                error_handling_tests.append("invalid_run_id: ✓ (handled)")
            
            # Test empty prompt
            try:
                empty_run = self.api.create_agent_run(323, "")
                error_handling_tests.append("empty_prompt: ✗ (no error)")
            except Exception:
                error_handling_tests.append("empty_prompt: ✓ (handled)")
            
            # Test invalid organization
            try:
                invalid_org_runs = self.api.list_agent_runs(999999, limit=5)
                error_handling_tests.append("invalid_org: ✗ (no error)")
            except Exception:
                error_handling_tests.append("invalid_org: ✓ (handled)")
            
            # Test API resilience with multiple rapid requests
            try:
                for i in range(3):
                    self.api.list_agent_runs(323, limit=1)
                error_handling_tests.append("rapid_requests: ✓ (handled)")
            except Exception:
                error_handling_tests.append("rapid_requests: ✗ (failed)")
            
            # Consider successful if most error cases are handled
            handled_count = sum(1 for test in error_handling_tests if '✓' in test)
            success = handled_count >= 3
            
            self.log_test(
                "Error Handling and Resilience",
                success,
                f"Error handling: {', '.join(error_handling_tests)} ({handled_count}/4 handled)",
                time.time() - start_time
            )
            return success
            
        except Exception as e:
            self.log_test(
                "Error Handling and Resilience",
                False,
                f"Error handling test failed: {str(e)}",
                time.time() - start_time
            )
            return False
    
    def run_complete_validation(self) -> Dict[str, Any]:
        """Run complete dashboard validation"""
        logger.info("🚀 Starting Complete Dashboard Validation with Real API")
        logger.info(f"API Token: {self.api.api_token[:8]}...{self.api.api_token[-4:]}")
        logger.info(f"Organization ID: {self.api.org_id}")
        logger.info(f"Base URL: {self.api.base_url}")
        logger.info("=" * 60)
        
        # Define comprehensive test suite
        tests = [
            ("Dashboard Data Loading", self.test_dashboard_data_loading),
            ("Run Management Operations", self.test_run_management_operations),
            ("Filtering and Search", self.test_filtering_and_search),
            ("Analytics and Statistics", self.test_analytics_and_statistics),
            ("Real-time Data Updates", self.test_real_time_data_updates),
            ("Error Handling and Resilience", self.test_error_handling_and_resilience),
        ]
        
        # Run all tests
        passed_tests = 0
        total_tests = len(tests)
        
        for test_name, test_func in tests:
            logger.info(f"Running test: {test_name}")
            try:
                if test_func():
                    passed_tests += 1
            except Exception as e:
                logger.error(f"Test {test_name} crashed: {str(e)}")
                logger.error(traceback.format_exc())
        
        # Calculate results
        end_time = datetime.now()
        total_duration = (end_time - self.start_time).total_seconds()
        success_rate = (passed_tests / total_tests) * 100
        
        # Generate summary
        summary = {
            "validation_start": self.start_time.isoformat(),
            "validation_end": end_time.isoformat(),
            "total_duration": total_duration,
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "success_rate": success_rate,
            "status": "PASS" if success_rate >= 80 else "FAIL",
            "detailed_results": self.test_results,
            "api_config": {
                "base_url": self.api.base_url,
                "org_id": self.api.org_id,
                "token_preview": f"{self.api.api_token[:8]}...{self.api.api_token[-4:]}"
            }
        }
        
        # Log summary
        logger.info("=" * 60)
        logger.info("📊 COMPLETE DASHBOARD VALIDATION SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Passed: {passed_tests}")
        logger.info(f"Failed: {total_tests - passed_tests}")
        logger.info(f"Success Rate: {success_rate:.1f}%")
        logger.info(f"Total Duration: {total_duration:.2f}s")
        logger.info(f"Overall Status: {summary['status']}")
        logger.info("=" * 60)
        
        if success_rate >= 80:
            logger.info("✅ Complete dashboard validation PASSED! Dashboard is production-ready with real API.")
        else:
            logger.warning("⚠️ Complete dashboard validation FAILED. Review failed tests before deployment.")
        
        return summary

def main():
    """Main validation function"""
    print("🚀 Complete Codegen Dashboard Validation with Real API")
    print("=" * 60)
    
    validator = CompleteDashboardValidator()
    summary = validator.run_complete_validation()
    
    # Save results
    results_file = os.path.join(os.path.dirname(__file__), 'complete_dashboard_validation_results.json')
    with open(results_file, 'w') as f:
        json.dump(summary, f, indent=2, default=str)
    
    print(f"\n📄 Results saved to: {results_file}")
    
    return summary['status'] == 'PASS'

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

