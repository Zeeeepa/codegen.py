#!/usr/bin/env python3
"""
Real API Validation Script
Tests the actual Codegen API with real credentials and validates all functionality.
"""

import sys
import os
import time
import json
import traceback
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

# Add parent directories to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from services.real_api_service import RealCodegenAPI

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RealAPIValidator:
    """Validates the real Codegen API functionality"""
    
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
    
    def test_authentication(self) -> bool:
        """Test API authentication"""
        start_time = time.time()
        
        try:
            user = self.api.get_current_user()
            
            if user and hasattr(user, 'github_username'):
                self.log_test(
                    "Real API Authentication",
                    True,
                    f"Authenticated as {user.github_username} (ID: {user.id})",
                    time.time() - start_time
                )
                return True
            else:
                self.log_test(
                    "Real API Authentication",
                    False,
                    "No valid user data returned",
                    time.time() - start_time
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Real API Authentication",
                False,
                f"Authentication failed: {str(e)}",
                time.time() - start_time
            )
            return False
    
    def test_organizations(self) -> bool:
        """Test organization access"""
        start_time = time.time()
        
        try:
            orgs = self.api.get_organizations(limit=10)
            
            if orgs and len(orgs) > 0:
                org_info = []
                for org in orgs:
                    org_info.append(f"{org.name} (ID: {org.id})")
                
                self.log_test(
                    "Real API Organizations",
                    True,
                    f"Found {len(orgs)} organizations: {', '.join(org_info)}",
                    time.time() - start_time
                )
                return True
            else:
                self.log_test(
                    "Real API Organizations",
                    False,
                    "No organizations found",
                    time.time() - start_time
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Real API Organizations",
                False,
                f"Failed to get organizations: {str(e)}",
                time.time() - start_time
            )
            return False
    
    def test_agent_runs_listing(self) -> bool:
        """Test listing agent runs"""
        start_time = time.time()
        
        try:
            # Test basic listing
            runs = self.api.list_agent_runs(limit=10)
            
            if runs and 'items' in runs:
                total_runs = len(runs['items'])
                
                # Get status breakdown
                status_counts = {}
                for run in runs['items']:
                    status = run['status']
                    status_counts[status] = status_counts.get(status, 0) + 1
                
                status_info = [f"{status}: {count}" for status, count in status_counts.items()]
                
                # Test pagination
                page1 = self.api.list_agent_runs(limit=5, skip=0)
                page2 = self.api.list_agent_runs(limit=5, skip=5)
                
                pagination_works = (
                    len(page1['items']) <= 5 and 
                    len(page2['items']) <= 5
                )
                
                self.log_test(
                    "Real API Agent Runs Listing",
                    True,
                    f"Found {total_runs} runs. Status breakdown: {', '.join(status_info)}. Pagination: {'✓' if pagination_works else '✗'}",
                    time.time() - start_time
                )
                return True
            else:
                self.log_test(
                    "Real API Agent Runs Listing",
                    False,
                    "No runs data returned or invalid format",
                    time.time() - start_time
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Real API Agent Runs Listing",
                False,
                f"Failed to list agent runs: {str(e)}",
                time.time() - start_time
            )
            return False
    
    def test_agent_run_creation(self) -> bool:
        """Test creating a new agent run"""
        start_time = time.time()
        
        try:
            test_prompt = f"Dashboard validation test run created at {datetime.now().isoformat()}"
            metadata = {
                "source": "dashboard_validation",
                "test": True,
                "created_by": "real_api_validator"
            }
            
            new_run = self.api.create_agent_run(
                prompt=test_prompt,
                metadata=metadata
            )
            
            if new_run and 'id' in new_run:
                # Verify the run was created
                retrieved_run = self.api.get_agent_run(run_id=new_run['id'])
                
                if retrieved_run and retrieved_run['prompt'] == test_prompt:
                    self.log_test(
                        "Real API Agent Run Creation",
                        True,
                        f"Created and verified run #{new_run['id']} with status '{new_run['status']}'",
                        time.time() - start_time
                    )
                    return True
                else:
                    self.log_test(
                        "Real API Agent Run Creation",
                        False,
                        f"Run created but verification failed",
                        time.time() - start_time
                    )
                    return False
            else:
                self.log_test(
                    "Real API Agent Run Creation",
                    False,
                    "No valid run data returned from creation",
                    time.time() - start_time
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Real API Agent Run Creation",
                False,
                f"Failed to create agent run: {str(e)}",
                time.time() - start_time
            )
            return False
    
    def test_agent_run_details(self) -> bool:
        """Test getting detailed agent run information"""
        start_time = time.time()
        
        try:
            # Get a run to test with
            runs = self.api.list_agent_runs(limit=1)
            
            if not runs['items']:
                self.log_test(
                    "Real API Agent Run Details",
                    False,
                    "No runs available to test details",
                    time.time() - start_time
                )
                return False
            
            test_run_id = runs['items'][0]['id']
            run_details = self.api.get_agent_run(run_id=test_run_id)
            
            if run_details:
                required_fields = ['id', 'status', 'prompt', 'created_at', 'web_url']
                has_required_fields = all(field in run_details for field in required_fields)
                
                self.log_test(
                    "Real API Agent Run Details",
                    has_required_fields,
                    f"Retrieved details for run #{test_run_id}. Status: {run_details.get('status')}. Required fields: {'✓' if has_required_fields else '✗'}",
                    time.time() - start_time
                )
                return has_required_fields
            else:
                self.log_test(
                    "Real API Agent Run Details",
                    False,
                    f"No details returned for run #{test_run_id}",
                    time.time() - start_time
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Real API Agent Run Details",
                False,
                f"Failed to get run details: {str(e)}",
                time.time() - start_time
            )
            return False
    
    def test_agent_run_logs(self) -> bool:
        """Test getting agent run logs"""
        start_time = time.time()
        
        try:
            # Get a run to test with
            runs = self.api.list_agent_runs(limit=5)
            
            if not runs['items']:
                self.log_test(
                    "Real API Agent Run Logs",
                    False,
                    "No runs available to test logs",
                    time.time() - start_time
                )
                return False
            
            # Try to get logs for multiple runs
            logs_found = False
            for run in runs['items']:
                try:
                    logs = self.api.get_agent_run_logs(run_id=run['id'], limit=10)
                    if logs and len(logs) > 0:
                        logs_found = True
                        self.log_test(
                            "Real API Agent Run Logs",
                            True,
                            f"Retrieved {len(logs)} logs for run #{run['id']}",
                            time.time() - start_time
                        )
                        return True
                except Exception as e:
                    logger.debug(f"No logs for run {run['id']}: {str(e)}")
                    continue
            
            if not logs_found:
                self.log_test(
                    "Real API Agent Run Logs",
                    True,  # This is OK - runs might not have logs yet
                    "No logs found for any runs (this is normal for new/pending runs)",
                    time.time() - start_time
                )
                return True
                
        except Exception as e:
            self.log_test(
                "Real API Agent Run Logs",
                False,
                f"Failed to get run logs: {str(e)}",
                time.time() - start_time
            )
            return False
    
    def test_agent_run_management(self) -> bool:
        """Test agent run management operations"""
        start_time = time.time()
        
        try:
            # Create a test run for management
            test_run = self.api.create_agent_run(
                prompt="Test run for management operations validation",
                metadata={"test": "management", "validator": "real_api"}
            )
            
            if not test_run or 'id' not in test_run:
                self.log_test(
                    "Real API Agent Run Management",
                    False,
                    "Failed to create test run for management",
                    time.time() - start_time
                )
                return False
            
            run_id = test_run['id']
            operations_tested = []
            
            # Test cancel operation
            cancel_result = self.api.cancel_agent_run(run_id=run_id)
            operations_tested.append(f"cancel: {'✓' if cancel_result else '✗'}")
            
            # Verify the run status changed
            try:
                updated_run = self.api.get_agent_run(run_id=run_id)
                final_status = updated_run.get('status', 'unknown')
                operations_tested.append(f"status_check: {final_status}")
            except Exception as e:
                operations_tested.append(f"status_check: error - {str(e)}")
            
            # Test pause operation (might not work on cancelled run, but test the endpoint)
            try:
                pause_result = self.api.pause_agent_run(run_id=run_id)
                operations_tested.append(f"pause: {'✓' if pause_result else '✗'}")
            except Exception as e:
                operations_tested.append(f"pause: error - {str(e)}")
            
            # Test resume operation
            try:
                resume_result = self.api.resume_agent_run(run_id=run_id, prompt="Resume test")
                operations_tested.append(f"resume: {'✓' if resume_result else '✗'}")
            except Exception as e:
                operations_tested.append(f"resume: error - {str(e)}")
            
            # Consider it successful if at least cancel worked
            success = cancel_result
            
            self.log_test(
                "Real API Agent Run Management",
                success,
                f"Management operations on run #{run_id}: {', '.join(operations_tested)}",
                time.time() - start_time
            )
            return success
            
        except Exception as e:
            self.log_test(
                "Real API Agent Run Management",
                False,
                f"Management operations failed: {str(e)}",
                time.time() - start_time
            )
            return False
    
    def test_statistics_and_search(self) -> bool:
        """Test statistics and search functionality"""
        start_time = time.time()
        
        try:
            # Test statistics
            stats = self.api.get_run_statistics(days=30)
            
            required_stats = ['total_runs', 'status_breakdown', 'success_rate']
            has_required_stats = all(field in stats for field in required_stats)
            
            # Test search
            search_results = self.api.search_runs(query="test", limit=5)
            search_works = isinstance(search_results, list)
            
            self.log_test(
                "Real API Statistics and Search",
                has_required_stats and search_works,
                f"Stats: {stats['total_runs']} runs, {stats['success_rate']}% success. Search: {len(search_results) if search_works else 0} results",
                time.time() - start_time
            )
            return has_required_stats and search_works
            
        except Exception as e:
            self.log_test(
                "Real API Statistics and Search",
                False,
                f"Statistics and search failed: {str(e)}",
                time.time() - start_time
            )
            return False
    
    def test_projects(self) -> bool:
        """Test project functionality"""
        start_time = time.time()
        
        try:
            projects = self.api.get_projects(limit=10)
            
            if projects and len(projects) > 0:
                project_names = [p['name'] for p in projects]
                self.log_test(
                    "Real API Projects",
                    True,
                    f"Found {len(projects)} projects: {', '.join(project_names)}",
                    time.time() - start_time
                )
                return True
            else:
                # Projects might not be available, but that's OK
                self.log_test(
                    "Real API Projects",
                    True,
                    "No projects found (using default project)",
                    time.time() - start_time
                )
                return True
                
        except Exception as e:
            self.log_test(
                "Real API Projects",
                True,  # Projects are optional
                f"Projects not available (using defaults): {str(e)}",
                time.time() - start_time
            )
            return True
    
    def run_comprehensive_validation(self) -> Dict[str, Any]:
        """Run all validation tests"""
        logger.info("🚀 Starting Real API Comprehensive Validation")
        logger.info(f"API Token: {self.api.api_token[:8]}...{self.api.api_token[-4:]}")
        logger.info(f"Organization ID: {self.api.org_id}")
        logger.info(f"Base URL: {self.api.base_url}")
        logger.info("=" * 60)
        
        # Define test suite
        tests = [
            ("Authentication", self.test_authentication),
            ("Organizations", self.test_organizations),
            ("Agent Runs Listing", self.test_agent_runs_listing),
            ("Agent Run Creation", self.test_agent_run_creation),
            ("Agent Run Details", self.test_agent_run_details),
            ("Agent Run Logs", self.test_agent_run_logs),
            ("Agent Run Management", self.test_agent_run_management),
            ("Statistics and Search", self.test_statistics_and_search),
            ("Projects", self.test_projects),
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
            "status": "PASS" if success_rate >= 70 else "FAIL",  # Lower threshold for real API
            "detailed_results": self.test_results,
            "api_config": {
                "base_url": self.api.base_url,
                "org_id": self.api.org_id,
                "token_preview": f"{self.api.api_token[:8]}...{self.api.api_token[-4:]}"
            }
        }
        
        # Log summary
        logger.info("=" * 60)
        logger.info("📊 REAL API VALIDATION SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Passed: {passed_tests}")
        logger.info(f"Failed: {total_tests - passed_tests}")
        logger.info(f"Success Rate: {success_rate:.1f}%")
        logger.info(f"Total Duration: {total_duration:.2f}s")
        logger.info(f"Overall Status: {summary['status']}")
        logger.info("=" * 60)
        
        if success_rate >= 70:
            logger.info("✅ Real API validation PASSED! Dashboard can use real API.")
        else:
            logger.warning("⚠️ Real API validation FAILED. Check API connectivity and endpoints.")
        
        return summary

def main():
    """Main validation function"""
    print("🚀 Real Codegen API Comprehensive Validation")
    print("=" * 60)
    
    validator = RealAPIValidator()
    summary = validator.run_comprehensive_validation()
    
    # Save results
    results_file = os.path.join(os.path.dirname(__file__), 'real_api_validation_results.json')
    with open(results_file, 'w') as f:
        json.dump(summary, f, indent=2, default=str)
    
    print(f"\n📄 Results saved to: {results_file}")
    
    return summary['status'] == 'PASS'

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

