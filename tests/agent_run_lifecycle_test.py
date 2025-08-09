#!/usr/bin/env python3
"""
Comprehensive Agent Run Lifecycle Test with Real-time State Monitoring

This test validates:
1. Agent run creation with planning task
2. Real-time state monitoring every 1 second
3. Complete log streaming and analysis
4. Proper state management and response retrieval
5. All log types and field population patterns
6. Final answer extraction and validation

Addresses common issues:
- "Running" state not updating to "completed"
- Missing final responses
- Incomplete log retrieval
- State synchronization problems
"""

import os
import time
import json
import sys
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass
import requests
from requests.exceptions import RequestException

# Configuration
CODEGEN_ORG_ID = int(os.getenv("CODEGEN_ORG_ID", "323"))
CODEGEN_API_TOKEN = os.getenv("CODEGEN_API_TOKEN", "sk-ce027fa7-3c8d-4beb-8c86-ed8ae982ac99")
BASE_URL = "https://api.codegen.com/v1"

# Test configuration
POLL_INTERVAL = 1.0  # Poll every 1 second
MAX_WAIT_TIME = 300  # Maximum 5 minutes wait
LOG_BATCH_SIZE = 100  # Maximum logs per request

@dataclass
class LogEntry:
    """Structured log entry matching API specification"""
    agent_run_id: int
    created_at: str
    message_type: str
    thought: Optional[str] = None
    tool_name: Optional[str] = None
    tool_input: Optional[Dict[str, Any]] = None
    tool_output: Optional[Dict[str, Any]] = None
    observation: Optional[Any] = None  # Can be dict, string, or null
    
    def __post_init__(self):
        """Validate log entry according to field population patterns"""
        if self.message_type == "ACTION":
            # ACTION logs should have tool_name, tool_input, tool_output
            if not self.tool_name:
                print(f"⚠️  WARNING: ACTION log missing tool_name: {self}")
        elif self.message_type == "PLAN_EVALUATION":
            # PLAN_EVALUATION logs should always have thought
            if not self.thought:
                print(f"⚠️  WARNING: PLAN_EVALUATION log missing thought: {self}")
        elif self.message_type == "ERROR":
            # ERROR logs should always have observation
            if not self.observation:
                print(f"⚠️  WARNING: ERROR log missing observation: {self}")
        elif self.message_type == "FINAL_ANSWER":
            # FINAL_ANSWER logs should always have observation
            if not self.observation:
                print(f"⚠️  WARNING: FINAL_ANSWER log missing observation: {self}")

@dataclass
class AgentRunState:
    """Complete agent run state"""
    id: int
    organization_id: int
    status: Optional[str]
    created_at: Optional[str]
    web_url: Optional[str]
    result: Optional[str]
    source_type: Optional[str]
    metadata: Optional[Dict[str, Any]]
    total_logs: Optional[int] = None
    logs: List[LogEntry] = None
    
    def __post_init__(self):
        if self.logs is None:
            self.logs = []

class AgentRunLifecycleTest:
    """Comprehensive agent run lifecycle test with real-time monitoring"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {CODEGEN_API_TOKEN}",
            "Content-Type": "application/json",
            "User-Agent": "codegen-lifecycle-test/1.0.0"
        })
        
        # Test state tracking
        self.agent_run_id: Optional[int] = None
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.all_logs: List[LogEntry] = []
        self.seen_log_ids: Set[str] = set()
        self.state_history: List[Dict[str, Any]] = []
        
        # Statistics
        self.stats = {
            "total_polls": 0,
            "total_log_requests": 0,
            "unique_logs_seen": 0,
            "log_types_seen": set(),
            "tools_used": set(),
            "errors_encountered": 0,
            "state_changes": 0,
        }
    
    def log_with_timestamp(self, message: str, level: str = "INFO"):
        """Log message with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        prefix = {
            "INFO": "ℹ️ ",
            "SUCCESS": "✅",
            "WARNING": "⚠️ ",
            "ERROR": "❌",
            "DEBUG": "🔍"
        }.get(level, "📝")
        print(f"[{timestamp}] {prefix} {message}")
    
    def make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make API request with error handling"""
        url = f"{BASE_URL}{endpoint}"
        
        try:
            response = self.session.request(method, url, timeout=30, **kwargs)
            
            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", 60))
                self.log_with_timestamp(f"Rate limited, waiting {retry_after}s", "WARNING")
                time.sleep(retry_after)
                return self.make_request(method, endpoint, **kwargs)
            
            if response.status_code == 401:
                raise Exception("Authentication failed - check API token")
            elif response.status_code == 404:
                raise Exception(f"Resource not found: {endpoint}")
            elif response.status_code >= 400:
                error_data = response.text
                try:
                    error_json = response.json()
                    error_data = json.dumps(error_json, indent=2)
                except:
                    pass
                raise Exception(f"API error {response.status_code}: {error_data}")
            
            return response.json()
            
        except RequestException as e:
            raise Exception(f"Network error: {str(e)}")
    
    def create_planning_agent_run(self) -> int:
        """Create an agent run with a complex planning task"""
        self.log_with_timestamp("Creating agent run with planning task...")
        
        # Complex planning task that should generate multiple steps
        prompt = """Please create a comprehensive project plan for building a Python web scraping tool that:

1. Scrapes product data from e-commerce websites
2. Stores data in a database with proper schema design
3. Includes rate limiting and error handling
4. Has a REST API to query the scraped data
5. Includes unit tests and documentation
6. Uses Docker for deployment

Please provide:
- Detailed project structure
- Step-by-step implementation plan
- Technology recommendations
- Timeline estimates
- Risk assessment and mitigation strategies

This should be a thorough analysis with multiple reasoning steps."""
        
        data = {
            "prompt": prompt,
            "metadata": {
                "test_type": "lifecycle_validation",
                "created_by": "agent_run_lifecycle_test",
                "timestamp": datetime.now().isoformat(),
                "expected_complexity": "high",
                "expected_steps": "multiple"
            }
        }
        
        response = self.make_request(
            "POST", 
            f"/organizations/{CODEGEN_ORG_ID}/agent/run",
            json=data
        )
        
        agent_run_id = response["id"]
        self.agent_run_id = agent_run_id
        self.start_time = datetime.now()
        
        self.log_with_timestamp(f"Agent run created: {agent_run_id}", "SUCCESS")
        self.log_with_timestamp(f"Web URL: {response.get('web_url', 'N/A')}")
        self.log_with_timestamp(f"Initial status: {response.get('status', 'N/A')}")
        
        return agent_run_id
    
    def get_agent_run_state(self, agent_run_id: int) -> AgentRunState:
        """Get current agent run state"""
        response = self.make_request(
            "GET",
            f"/organizations/{CODEGEN_ORG_ID}/agent/run/{agent_run_id}"
        )
        
        return AgentRunState(
            id=response["id"],
            organization_id=response["organization_id"],
            status=response.get("status"),
            created_at=response.get("created_at"),
            web_url=response.get("web_url"),
            result=response.get("result"),
            source_type=response.get("source_type"),
            metadata=response.get("metadata")
        )
    
    def get_agent_run_logs(self, agent_run_id: int, skip: int = 0, limit: int = 100) -> Dict[str, Any]:
        """Get agent run logs with pagination"""
        self.stats["total_log_requests"] += 1
        
        response = self.make_request(
            "GET",
            f"/alpha/organizations/{CODEGEN_ORG_ID}/agent/run/{agent_run_id}/logs",
            params={"skip": skip, "limit": limit}
        )
        
        # Validate response structure
        required_fields = ["id", "organization_id", "logs", "total_logs", "page", "size", "pages"]
        for field in required_fields:
            if field not in response:
                self.log_with_timestamp(f"Missing required field in logs response: {field}", "WARNING")
        
        return response
    
    def parse_log_entry(self, log_data: Dict[str, Any]) -> LogEntry:
        """Parse log entry from API response"""
        return LogEntry(
            agent_run_id=log_data.get("agent_run_id", 0),
            created_at=log_data.get("created_at", ""),
            message_type=log_data.get("message_type", ""),
            thought=log_data.get("thought"),
            tool_name=log_data.get("tool_name"),
            tool_input=log_data.get("tool_input"),
            tool_output=log_data.get("tool_output"),
            observation=log_data.get("observation")
        )
    
    def stream_all_logs(self, agent_run_id: int) -> List[LogEntry]:
        """Stream all logs with pagination"""
        all_logs = []
        skip = 0
        
        while True:
            logs_response = self.get_agent_run_logs(agent_run_id, skip=skip, limit=LOG_BATCH_SIZE)
            
            batch_logs = []
            for log_data in logs_response.get("logs", []):
                log_entry = self.parse_log_entry(log_data)
                batch_logs.append(log_entry)
                
                # Track statistics
                log_id = f"{log_entry.created_at}_{log_entry.message_type}_{log_entry.agent_run_id}"
                if log_id not in self.seen_log_ids:
                    self.seen_log_ids.add(log_id)
                    self.stats["unique_logs_seen"] += 1
                    self.stats["log_types_seen"].add(log_entry.message_type)
                    
                    if log_entry.tool_name:
                        self.stats["tools_used"].add(log_entry.tool_name)
                    
                    if log_entry.message_type == "ERROR":
                        self.stats["errors_encountered"] += 1
            
            all_logs.extend(batch_logs)
            
            # Check if we have more logs
            if len(batch_logs) < LOG_BATCH_SIZE:
                break
            
            skip += LOG_BATCH_SIZE
        
        return all_logs
    
    def analyze_logs(self, logs: List[LogEntry]) -> Dict[str, Any]:
        """Analyze logs for patterns and completeness"""
        analysis = {
            "total_logs": len(logs),
            "log_types": {},
            "tools_used": {},
            "has_final_answer": False,
            "has_errors": False,
            "timeline": [],
            "field_population": {
                "ACTION": {"tool_name": 0, "tool_input": 0, "tool_output": 0, "thought": 0},
                "PLAN_EVALUATION": {"thought": 0, "observation": 0},
                "ERROR": {"observation": 0, "tool_name": 0},
                "FINAL_ANSWER": {"observation": 0, "thought": 0}
            }
        }
        
        for log in logs:
            # Count log types
            analysis["log_types"][log.message_type] = analysis["log_types"].get(log.message_type, 0) + 1
            
            # Count tools
            if log.tool_name:
                analysis["tools_used"][log.tool_name] = analysis["tools_used"].get(log.tool_name, 0) + 1
            
            # Check for final answer
            if log.message_type == "FINAL_ANSWER":
                analysis["has_final_answer"] = True
            
            # Check for errors
            if log.message_type == "ERROR":
                analysis["has_errors"] = True
            
            # Timeline
            analysis["timeline"].append({
                "timestamp": log.created_at,
                "type": log.message_type,
                "tool": log.tool_name,
                "has_thought": bool(log.thought),
                "has_observation": bool(log.observation)
            })
            
            # Field population analysis
            if log.message_type in analysis["field_population"]:
                fields = analysis["field_population"][log.message_type]
                if log.tool_name and "tool_name" in fields:
                    fields["tool_name"] += 1
                if log.tool_input and "tool_input" in fields:
                    fields["tool_input"] += 1
                if log.tool_output and "tool_output" in fields:
                    fields["tool_output"] += 1
                if log.thought and "thought" in fields:
                    fields["thought"] += 1
                if log.observation and "observation" in fields:
                    fields["observation"] += 1
        
        return analysis
    
    def print_log_summary(self, logs: List[LogEntry]):
        """Print a summary of logs"""
        if not logs:
            self.log_with_timestamp("No logs found", "WARNING")
            return
        
        self.log_with_timestamp(f"📊 Log Summary ({len(logs)} total logs):")
        
        # Group by type
        by_type = {}
        for log in logs:
            by_type.setdefault(log.message_type, []).append(log)
        
        for log_type, type_logs in by_type.items():
            print(f"  {log_type}: {len(type_logs)} logs")
            
            # Show sample of each type
            for i, log in enumerate(type_logs[:3]):  # Show first 3 of each type
                timestamp = log.created_at.split('T')[1][:12] if 'T' in log.created_at else log.created_at
                
                if log_type == "ACTION":
                    print(f"    [{timestamp}] 🔧 {log.tool_name or 'Unknown tool'}")
                    if log.thought:
                        print(f"      💭 {log.thought[:80]}{'...' if len(log.thought) > 80 else ''}")
                elif log_type == "PLAN_EVALUATION":
                    if log.thought:
                        print(f"    [{timestamp}] 🤔 {log.thought[:80]}{'...' if len(log.thought) > 80 else ''}")
                elif log_type == "FINAL_ANSWER":
                    if log.observation:
                        obs_str = str(log.observation)[:80] if log.observation else "No observation"
                        print(f"    [{timestamp}] 🎯 {obs_str}{'...' if len(obs_str) > 80 else ''}")
                elif log_type == "ERROR":
                    if log.observation:
                        obs_str = str(log.observation)[:80] if log.observation else "No observation"
                        print(f"    [{timestamp}] ❌ {obs_str}{'...' if len(obs_str) > 80 else ''}")
                else:
                    print(f"    [{timestamp}] 📝 {log_type}")
            
            if len(type_logs) > 3:
                print(f"    ... and {len(type_logs) - 3} more {log_type} logs")
    
    def monitor_agent_run(self, agent_run_id: int) -> AgentRunState:
        """Monitor agent run with real-time state and log streaming"""
        self.log_with_timestamp(f"🔄 Starting real-time monitoring of agent run {agent_run_id}")
        self.log_with_timestamp(f"⏱️  Polling every {POLL_INTERVAL}s, max wait time: {MAX_WAIT_TIME}s")
        
        start_time = time.time()
        last_status = None
        last_log_count = 0
        
        while True:
            current_time = time.time()
            elapsed = current_time - start_time
            
            if elapsed > MAX_WAIT_TIME:
                self.log_with_timestamp(f"⏰ Maximum wait time ({MAX_WAIT_TIME}s) exceeded", "WARNING")
                break
            
            self.stats["total_polls"] += 1
            
            try:
                # Get current state
                state = self.get_agent_run_state(agent_run_id)
                
                # Track state changes
                if state.status != last_status:
                    self.stats["state_changes"] += 1
                    self.log_with_timestamp(f"🔄 Status changed: {last_status} → {state.status}")
                    last_status = state.status
                    
                    # Record state change
                    self.state_history.append({
                        "timestamp": datetime.now().isoformat(),
                        "elapsed_seconds": elapsed,
                        "status": state.status,
                        "result_length": len(state.result) if state.result else 0
                    })
                
                # Get latest logs
                current_logs = self.stream_all_logs(agent_run_id)
                
                # Check for new logs
                if len(current_logs) > last_log_count:
                    new_logs = len(current_logs) - last_log_count
                    self.log_with_timestamp(f"📝 Found {new_logs} new logs (total: {len(current_logs)})")
                    last_log_count = len(current_logs)
                    
                    # Show latest logs
                    if new_logs > 0:
                        latest_logs = current_logs[-new_logs:]
                        for log in latest_logs:
                            timestamp = log.created_at.split('T')[1][:12] if 'T' in log.created_at else log.created_at
                            if log.message_type == "ACTION":
                                self.log_with_timestamp(f"  🔧 [{timestamp}] {log.tool_name}: {log.thought[:60] if log.thought else 'No thought'}...")
                            elif log.message_type == "PLAN_EVALUATION":
                                self.log_with_timestamp(f"  🤔 [{timestamp}] Planning: {log.thought[:60] if log.thought else 'No thought'}...")
                            elif log.message_type == "FINAL_ANSWER":
                                self.log_with_timestamp(f"  🎯 [{timestamp}] Final Answer: {str(log.observation)[:60] if log.observation else 'No observation'}...")
                            elif log.message_type == "ERROR":
                                self.log_with_timestamp(f"  ❌ [{timestamp}] Error: {str(log.observation)[:60] if log.observation else 'No observation'}...")
                            else:
                                self.log_with_timestamp(f"  📝 [{timestamp}] {log.message_type}")
                
                # Update state with logs
                state.logs = current_logs
                state.total_logs = len(current_logs)
                
                # Check if completed
                if state.status in ["completed", "failed", "cancelled"]:
                    self.log_with_timestamp(f"🏁 Agent run finished with status: {state.status}", "SUCCESS")
                    self.end_time = datetime.now()
                    return state
                
                # Progress update
                if self.stats["total_polls"] % 10 == 0:  # Every 10 polls
                    self.log_with_timestamp(f"⏳ Still monitoring... Status: {state.status}, Logs: {len(current_logs)}, Elapsed: {elapsed:.1f}s")
                
            except Exception as e:
                self.log_with_timestamp(f"Error during monitoring: {str(e)}", "ERROR")
                time.sleep(POLL_INTERVAL)
                continue
            
            time.sleep(POLL_INTERVAL)
        
        # If we get here, we timed out
        final_state = self.get_agent_run_state(agent_run_id)
        final_logs = self.stream_all_logs(agent_run_id)
        final_state.logs = final_logs
        final_state.total_logs = len(final_logs)
        
        return final_state
    
    def validate_final_state(self, final_state: AgentRunState) -> Dict[str, Any]:
        """Validate the final state and extract results"""
        validation = {
            "status_valid": final_state.status in ["completed", "failed", "cancelled"],
            "has_result": bool(final_state.result),
            "result_length": len(final_state.result) if final_state.result else 0,
            "has_logs": len(final_state.logs) > 0,
            "log_analysis": None,
            "issues": []
        }
        
        # Analyze logs
        if final_state.logs:
            validation["log_analysis"] = self.analyze_logs(final_state.logs)
            
            # Check for common issues
            if not validation["log_analysis"]["has_final_answer"]:
                validation["issues"].append("No FINAL_ANSWER log found")
            
            if validation["log_analysis"]["has_errors"]:
                validation["issues"].append(f"Found {validation['log_analysis']['log_types'].get('ERROR', 0)} error logs")
            
            # Check field population patterns
            field_pop = validation["log_analysis"]["field_population"]
            
            # ACTION logs should have tool fields
            if "ACTION" in validation["log_analysis"]["log_types"]:
                action_count = validation["log_analysis"]["log_types"]["ACTION"]
                if field_pop["ACTION"]["tool_name"] < action_count:
                    validation["issues"].append(f"Some ACTION logs missing tool_name ({field_pop['ACTION']['tool_name']}/{action_count})")
            
            # PLAN_EVALUATION logs should have thought
            if "PLAN_EVALUATION" in validation["log_analysis"]["log_types"]:
                plan_count = validation["log_analysis"]["log_types"]["PLAN_EVALUATION"]
                if field_pop["PLAN_EVALUATION"]["thought"] < plan_count:
                    validation["issues"].append(f"Some PLAN_EVALUATION logs missing thought ({field_pop['PLAN_EVALUATION']['thought']}/{plan_count})")
        
        # Check for state management issues
        if final_state.status == "running" and validation["has_result"]:
            validation["issues"].append("Status shows 'running' but result is present - possible state sync issue")
        
        if final_state.status == "completed" and not validation["has_result"]:
            validation["issues"].append("Status shows 'completed' but no result - possible response retrieval issue")
        
        return validation
    
    def print_final_report(self, final_state: AgentRunState, validation: Dict[str, Any]):
        """Print comprehensive final report"""
        print("\n" + "="*80)
        print("🎯 AGENT RUN LIFECYCLE TEST - FINAL REPORT")
        print("="*80)
        
        # Basic info
        duration = (self.end_time - self.start_time).total_seconds() if self.end_time and self.start_time else 0
        print(f"📊 Agent Run ID: {final_state.id}")
        print(f"⏱️  Total Duration: {duration:.1f} seconds")
        print(f"🔄 Final Status: {final_state.status}")
        print(f"🌐 Web URL: {final_state.web_url}")
        
        # Result info
        if final_state.result:
            print(f"📝 Result Length: {len(final_state.result)} characters")
            print(f"📄 Result Preview: {final_state.result[:200]}{'...' if len(final_state.result) > 200 else ''}")
        else:
            print("❌ No result found")
        
        # Statistics
        print(f"\n📈 MONITORING STATISTICS:")
        print(f"  Total Polls: {self.stats['total_polls']}")
        print(f"  Log Requests: {self.stats['total_log_requests']}")
        print(f"  Unique Logs: {self.stats['unique_logs_seen']}")
        print(f"  State Changes: {self.stats['state_changes']}")
        print(f"  Log Types Seen: {', '.join(sorted(self.stats['log_types_seen']))}")
        print(f"  Tools Used: {', '.join(sorted(self.stats['tools_used']))}")
        print(f"  Errors: {self.stats['errors_encountered']}")
        
        # Log analysis
        if validation["log_analysis"]:
            analysis = validation["log_analysis"]
            print(f"\n📋 LOG ANALYSIS:")
            print(f"  Total Logs: {analysis['total_logs']}")
            print(f"  Log Types: {dict(analysis['log_types'])}")
            print(f"  Tools Used: {dict(analysis['tools_used'])}")
            print(f"  Has Final Answer: {'✅' if analysis['has_final_answer'] else '❌'}")
            print(f"  Has Errors: {'⚠️ ' if analysis['has_errors'] else '✅'}")
        
        # State history
        if self.state_history:
            print(f"\n🔄 STATE CHANGE HISTORY:")
            for i, state_change in enumerate(self.state_history):
                print(f"  {i+1}. [{state_change['elapsed_seconds']:.1f}s] {state_change['status']} (result: {state_change['result_length']} chars)")
        
        # Validation results
        print(f"\n✅ VALIDATION RESULTS:")
        print(f"  Status Valid: {'✅' if validation['status_valid'] else '❌'}")
        print(f"  Has Result: {'✅' if validation['has_result'] else '❌'}")
        print(f"  Has Logs: {'✅' if validation['has_logs'] else '❌'}")
        
        # Issues
        if validation["issues"]:
            print(f"\n⚠️  ISSUES FOUND:")
            for i, issue in enumerate(validation["issues"], 1):
                print(f"  {i}. {issue}")
        else:
            print(f"\n🎉 NO ISSUES FOUND - ALL VALIDATIONS PASSED!")
        
        # Log summary
        if final_state.logs:
            print(f"\n📝 DETAILED LOG SUMMARY:")
            self.print_log_summary(final_state.logs)
        
        print("="*80)
    
    def run_test(self) -> bool:
        """Run the complete lifecycle test"""
        try:
            self.log_with_timestamp("🚀 Starting Agent Run Lifecycle Test", "SUCCESS")
            self.log_with_timestamp(f"🔧 Configuration: ORG_ID={CODEGEN_ORG_ID}, POLL_INTERVAL={POLL_INTERVAL}s")
            
            # Step 1: Create agent run
            agent_run_id = self.create_planning_agent_run()
            
            # Step 2: Monitor with real-time state and log streaming
            final_state = self.monitor_agent_run(agent_run_id)
            
            # Step 3: Validate final state
            validation = self.validate_final_state(final_state)
            
            # Step 4: Print comprehensive report
            self.print_final_report(final_state, validation)
            
            # Determine success
            success = (
                validation["status_valid"] and
                validation["has_result"] and
                validation["has_logs"] and
                len(validation["issues"]) == 0
            )
            
            if success:
                self.log_with_timestamp("🎉 TEST PASSED - All validations successful!", "SUCCESS")
            else:
                self.log_with_timestamp(f"❌ TEST FAILED - Found {len(validation['issues'])} issues", "ERROR")
            
            return success
            
        except Exception as e:
            self.log_with_timestamp(f"💥 TEST CRASHED: {str(e)}", "ERROR")
            import traceback
            traceback.print_exc()
            return False

def main():
    """Main test execution"""
    print("🧪 Agent Run Lifecycle Test with Real-time State Monitoring")
    print("=" * 80)
    
    # Validate configuration
    if not CODEGEN_API_TOKEN:
        print("❌ CODEGEN_API_TOKEN environment variable not set")
        sys.exit(1)
    
    if not CODEGEN_ORG_ID:
        print("❌ CODEGEN_ORG_ID environment variable not set")
        sys.exit(1)
    
    # Run test
    test = AgentRunLifecycleTest()
    success = test.run_test()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
