"""
Retry Effectiveness Benchmarks

This module benchmarks the effectiveness of the retry mechanisms under various
failure scenarios to optimize retry parameters and strategies.
"""

import time
import random
import statistics
import sys
from typing import List, Dict, Any, Callable, Optional
from dataclasses import dataclass
from unittest.mock import Mock, patch
from concurrent.futures import ThreadPoolExecutor, as_completed

# Import the retry system
sys.path.append('../..')
from codegen_api import (
    retry_with_backoff,
    RateLimitError,
    NetworkError,
    TimeoutError,
    ServerError,
    ClientConfig
)


@dataclass
class RetryScenario:
    """Configuration for a retry test scenario."""
    name: str
    failure_rate: float  # 0.0 to 1.0
    failure_types: List[type]
    max_retries: int
    base_delay: float
    backoff_factor: float
    expected_success_rate: float
    description: str


@dataclass
class RetryResult:
    """Result of a retry test."""
    scenario_name: str
    total_attempts: int
    successful_attempts: int
    failed_attempts: int
    success_rate: float
    average_retries_per_success: float
    average_time_per_success: float
    average_time_per_failure: float
    total_time: float
    retry_distribution: Dict[int, int]  # retry_count -> frequency


class RetrySimulator:
    """Simulates various failure scenarios for retry testing."""
    
    def __init__(self, scenario: RetryScenario):
        self.scenario = scenario
        self.call_count = 0
        self.attempt_times = []
        self.retry_counts = []
    
    def reset(self):
        """Reset simulator state."""
        self.call_count = 0
        self.attempt_times.clear()
        self.retry_counts.clear()
    
    def simulate_operation(self) -> str:
        """Simulate an operation that may fail according to scenario."""
        self.call_count += 1
        
        # Determine if this call should fail
        if random.random() < self.scenario.failure_rate:
            # Choose a random failure type
            failure_type = random.choice(self.scenario.failure_types)
            
            if failure_type == RateLimitError:
                # Simulate rate limit with random retry-after
                retry_after = random.randint(1, 5)
                raise RateLimitError(retry_after)
            elif failure_type == NetworkError:
                raise NetworkError("Simulated network failure")
            elif failure_type == TimeoutError:
                raise TimeoutError("Simulated timeout", 408)
            elif failure_type == ServerError:
                raise ServerError("Simulated server error", 500)
        
        return "success"
    
    def create_retryable_operation(self):
        """Create a retryable version of the operation."""
        @retry_with_backoff(
            max_retries=self.scenario.max_retries,
            base_delay=self.scenario.base_delay,
            backoff_factor=self.scenario.backoff_factor
        )
        def retryable_operation():
            return self.simulate_operation()
        
        return retryable_operation


class RetryEffectivenessBenchmark:
    """Benchmark retry mechanism effectiveness."""
    
    def __init__(self):
        self.scenarios = self._create_test_scenarios()
    
    def _create_test_scenarios(self) -> List[RetryScenario]:
        """Create various test scenarios."""
        return [
            RetryScenario(
                name="Low Failure Rate - Network",
                failure_rate=0.1,
                failure_types=[NetworkError],
                max_retries=3,
                base_delay=0.01,  # Short delays for testing
                backoff_factor=2.0,
                expected_success_rate=0.999,
                description="10% network failure rate with standard retry"
            ),
            RetryScenario(
                name="Medium Failure Rate - Mixed",
                failure_rate=0.3,
                failure_types=[NetworkError, TimeoutError, ServerError],
                max_retries=3,
                base_delay=0.01,
                backoff_factor=2.0,
                expected_success_rate=0.97,
                description="30% mixed failure rate with standard retry"
            ),
            RetryScenario(
                name="High Failure Rate - Network",
                failure_rate=0.5,
                failure_types=[NetworkError],
                max_retries=5,
                base_delay=0.01,
                backoff_factor=2.0,
                expected_success_rate=0.97,
                description="50% network failure rate with extended retry"
            ),
            RetryScenario(
                name="Rate Limiting Scenario",
                failure_rate=0.4,
                failure_types=[RateLimitError],
                max_retries=3,
                base_delay=0.01,
                backoff_factor=2.0,
                expected_success_rate=0.95,
                description="40% rate limiting with retry-after handling"
            ),
            RetryScenario(
                name="Server Instability",
                failure_rate=0.6,
                failure_types=[ServerError, TimeoutError],
                max_retries=4,
                base_delay=0.02,
                backoff_factor=1.5,
                expected_success_rate=0.90,
                description="60% server errors with conservative backoff"
            ),
            RetryScenario(
                name="Aggressive Retry",
                failure_rate=0.7,
                failure_types=[NetworkError, TimeoutError],
                max_retries=10,
                base_delay=0.005,
                backoff_factor=1.2,
                expected_success_rate=0.95,
                description="70% failure rate with aggressive retry strategy"
            ),
            RetryScenario(
                name="Conservative Retry",
                failure_rate=0.3,
                failure_types=[NetworkError, ServerError],
                max_retries=2,
                base_delay=0.05,
                backoff_factor=3.0,
                expected_success_rate=0.91,
                description="30% failure rate with conservative retry strategy"
            )
        ]
    
    def run_scenario(self, scenario: RetryScenario, iterations: int = 1000) -> RetryResult:
        """Run a specific retry scenario."""
        simulator = RetrySimulator(scenario)
        
        successful_attempts = 0
        failed_attempts = 0
        success_times = []
        failure_times = []
        retry_counts = []
        retry_distribution = {}
        
        start_time = time.perf_counter()
        
        for _ in range(iterations):
            simulator.reset()
            operation = simulator.create_retryable_operation()
            
            attempt_start = time.perf_counter()
            try:
                result = operation()
                attempt_end = time.perf_counter()
                
                successful_attempts += 1
                success_times.append(attempt_end - attempt_start)
                
                # Count retries (call_count - 1 because first call isn't a retry)
                retries = simulator.call_count - 1
                retry_counts.append(retries)
                retry_distribution[retries] = retry_distribution.get(retries, 0) + 1
                
            except Exception:
                attempt_end = time.perf_counter()
                failed_attempts += 1
                failure_times.append(attempt_end - attempt_start)
                
                # Count retries for failed attempts too
                retries = simulator.call_count - 1
                retry_distribution[retries] = retry_distribution.get(retries, 0) + 1
        
        end_time = time.perf_counter()
        
        success_rate = successful_attempts / iterations
        avg_retries_per_success = statistics.mean(retry_counts) if retry_counts else 0
        avg_time_per_success = statistics.mean(success_times) if success_times else 0
        avg_time_per_failure = statistics.mean(failure_times) if failure_times else 0
        
        return RetryResult(
            scenario_name=scenario.name,
            total_attempts=iterations,
            successful_attempts=successful_attempts,
            failed_attempts=failed_attempts,
            success_rate=success_rate,
            average_retries_per_success=avg_retries_per_success,
            average_time_per_success=avg_time_per_success,
            average_time_per_failure=avg_time_per_failure,
            total_time=end_time - start_time,
            retry_distribution=retry_distribution
        )
    
    def run_all_scenarios(self, iterations: int = 1000) -> List[RetryResult]:
        """Run all retry scenarios."""
        results = []
        
        print(f"Running {len(self.scenarios)} retry effectiveness scenarios with {iterations} iterations each...")
        print("-" * 80)
        
        for scenario in self.scenarios:
            print(f"Running {scenario.name}...", end=" ", flush=True)
            result = self.run_scenario(scenario, iterations)
            results.append(result)
            print(f"Done ({result.success_rate:.1%} success rate)")
        
        return results


class ConcurrentRetryBenchmark:
    """Benchmark retry behavior under concurrent load."""
    
    def __init__(self):
        self.failure_rate = 0.3
        self.max_workers = 10
    
    def simulate_concurrent_operation(self, operation_id: int) -> Dict[str, Any]:
        """Simulate a single concurrent operation."""
        @retry_with_backoff(max_retries=3, base_delay=0.01, backoff_factor=2.0)
        def operation():
            if random.random() < self.failure_rate:
                raise NetworkError(f"Failure in operation {operation_id}")
            return f"Success from operation {operation_id}"
        
        start_time = time.perf_counter()
        try:
            result = operation()
            end_time = time.perf_counter()
            return {
                'operation_id': operation_id,
                'success': True,
                'result': result,
                'duration': end_time - start_time
            }
        except Exception as e:
            end_time = time.perf_counter()
            return {
                'operation_id': operation_id,
                'success': False,
                'error': str(e),
                'duration': end_time - start_time
            }
    
    def run_concurrent_benchmark(self, total_operations: int = 100) -> Dict[str, Any]:
        """Run concurrent retry benchmark."""
        start_time = time.perf_counter()
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all operations
            futures = [
                executor.submit(self.simulate_concurrent_operation, i)
                for i in range(total_operations)
            ]
            
            # Collect results
            results = []
            for future in as_completed(futures):
                results.append(future.result())
        
        end_time = time.perf_counter()
        
        # Analyze results
        successful_ops = [r for r in results if r['success']]
        failed_ops = [r for r in results if not r['success']]
        
        success_rate = len(successful_ops) / total_operations
        avg_success_duration = statistics.mean([r['duration'] for r in successful_ops]) if successful_ops else 0
        avg_failure_duration = statistics.mean([r['duration'] for r in failed_ops]) if failed_ops else 0
        
        return {
            'total_operations': total_operations,
            'successful_operations': len(successful_ops),
            'failed_operations': len(failed_ops),
            'success_rate': success_rate,
            'total_duration': end_time - start_time,
            'average_success_duration': avg_success_duration,
            'average_failure_duration': avg_failure_duration,
            'max_workers': self.max_workers,
            'operations_per_second': total_operations / (end_time - start_time)
        }


class RetryParameterOptimizer:
    """Optimize retry parameters for different scenarios."""
    
    def __init__(self):
        self.base_scenario = RetryScenario(
            name="Optimization Test",
            failure_rate=0.4,
            failure_types=[NetworkError, TimeoutError],
            max_retries=3,
            base_delay=0.01,
            backoff_factor=2.0,
            expected_success_rate=0.95,
            description="Base scenario for parameter optimization"
        )
    
    def test_max_retries_optimization(self, iterations: int = 500) -> List[Dict[str, Any]]:
        """Test different max_retries values."""
        results = []
        
        for max_retries in [1, 2, 3, 4, 5, 7, 10]:
            scenario = RetryScenario(
                name=f"MaxRetries-{max_retries}",
                failure_rate=self.base_scenario.failure_rate,
                failure_types=self.base_scenario.failure_types,
                max_retries=max_retries,
                base_delay=self.base_scenario.base_delay,
                backoff_factor=self.base_scenario.backoff_factor,
                expected_success_rate=self.base_scenario.expected_success_rate,
                description=f"Testing max_retries={max_retries}"
            )
            
            benchmark = RetryEffectivenessBenchmark()
            result = benchmark.run_scenario(scenario, iterations)
            
            results.append({
                'max_retries': max_retries,
                'success_rate': result.success_rate,
                'avg_time_per_success': result.average_time_per_success,
                'avg_retries_per_success': result.average_retries_per_success
            })
        
        return results
    
    def test_backoff_factor_optimization(self, iterations: int = 500) -> List[Dict[str, Any]]:
        """Test different backoff_factor values."""
        results = []
        
        for backoff_factor in [1.0, 1.2, 1.5, 2.0, 2.5, 3.0]:
            scenario = RetryScenario(
                name=f"BackoffFactor-{backoff_factor}",
                failure_rate=self.base_scenario.failure_rate,
                failure_types=self.base_scenario.failure_types,
                max_retries=self.base_scenario.max_retries,
                base_delay=self.base_scenario.base_delay,
                backoff_factor=backoff_factor,
                expected_success_rate=self.base_scenario.expected_success_rate,
                description=f"Testing backoff_factor={backoff_factor}"
            )
            
            benchmark = RetryEffectivenessBenchmark()
            result = benchmark.run_scenario(scenario, iterations)
            
            results.append({
                'backoff_factor': backoff_factor,
                'success_rate': result.success_rate,
                'avg_time_per_success': result.average_time_per_success,
                'avg_retries_per_success': result.average_retries_per_success
            })
        
        return results
    
    def find_optimal_parameters(self, target_success_rate: float = 0.95) -> Dict[str, Any]:
        """Find optimal retry parameters for target success rate."""
        print(f"Optimizing retry parameters for {target_success_rate:.1%} success rate...")
        
        # Test max_retries optimization
        print("Testing max_retries values...", end=" ", flush=True)
        max_retries_results = self.test_max_retries_optimization()
        print("Done")
        
        # Test backoff_factor optimization
        print("Testing backoff_factor values...", end=" ", flush=True)
        backoff_results = self.test_backoff_factor_optimization()
        print("Done")
        
        # Find best max_retries
        best_max_retries = None
        best_max_retries_score = float('inf')
        
        for result in max_retries_results:
            if result['success_rate'] >= target_success_rate:
                # Score based on time and retries (lower is better)
                score = result['avg_time_per_success'] + result['avg_retries_per_success'] * 0.1
                if score < best_max_retries_score:
                    best_max_retries_score = score
                    best_max_retries = result['max_retries']
        
        # Find best backoff_factor
        best_backoff_factor = None
        best_backoff_score = float('inf')
        
        for result in backoff_results:
            if result['success_rate'] >= target_success_rate:
                score = result['avg_time_per_success'] + result['avg_retries_per_success'] * 0.1
                if score < best_backoff_score:
                    best_backoff_score = score
                    best_backoff_factor = result['backoff_factor']
        
        return {
            'target_success_rate': target_success_rate,
            'optimal_max_retries': best_max_retries,
            'optimal_backoff_factor': best_backoff_factor,
            'max_retries_results': max_retries_results,
            'backoff_factor_results': backoff_results
        }


def print_retry_results(results: List[RetryResult]):
    """Print formatted retry effectiveness results."""
    print("\n" + "=" * 80)
    print("RETRY EFFECTIVENESS RESULTS")
    print("=" * 80)
    
    for result in results:
        print(f"\n{result.scenario_name}:")
        print(f"  Success Rate: {result.success_rate:.1%} ({result.successful_attempts}/{result.total_attempts})")
        print(f"  Avg Retries per Success: {result.average_retries_per_success:.2f}")
        print(f"  Avg Time per Success: {result.average_time_per_success*1000:.2f} ms")
        print(f"  Avg Time per Failure: {result.average_time_per_failure*1000:.2f} ms")
        print(f"  Total Time: {result.total_time:.2f} seconds")
        
        # Show retry distribution
        if result.retry_distribution:
            print("  Retry Distribution:")
            for retries, count in sorted(result.retry_distribution.items()):
                percentage = (count / result.total_attempts) * 100
                print(f"    {retries} retries: {count} attempts ({percentage:.1f}%)")


def print_concurrent_results(result: Dict[str, Any]):
    """Print concurrent retry benchmark results."""
    print("\n" + "=" * 80)
    print("CONCURRENT RETRY RESULTS")
    print("=" * 80)
    
    print(f"Total Operations: {result['total_operations']}")
    print(f"Successful Operations: {result['successful_operations']}")
    print(f"Failed Operations: {result['failed_operations']}")
    print(f"Success Rate: {result['success_rate']:.1%}")
    print(f"Total Duration: {result['total_duration']:.2f} seconds")
    print(f"Operations per Second: {result['operations_per_second']:.1f}")
    print(f"Max Workers: {result['max_workers']}")
    print(f"Avg Success Duration: {result['average_success_duration']*1000:.2f} ms")
    print(f"Avg Failure Duration: {result['average_failure_duration']*1000:.2f} ms")


def print_optimization_results(optimization_result: Dict[str, Any]):
    """Print parameter optimization results."""
    print("\n" + "=" * 80)
    print("RETRY PARAMETER OPTIMIZATION RESULTS")
    print("=" * 80)
    
    print(f"Target Success Rate: {optimization_result['target_success_rate']:.1%}")
    print(f"Optimal Max Retries: {optimization_result['optimal_max_retries']}")
    print(f"Optimal Backoff Factor: {optimization_result['optimal_backoff_factor']}")
    
    print("\nMax Retries Analysis:")
    for result in optimization_result['max_retries_results']:
        print(f"  {result['max_retries']} retries: {result['success_rate']:.1%} success, "
              f"{result['avg_time_per_success']*1000:.1f}ms avg time")
    
    print("\nBackoff Factor Analysis:")
    for result in optimization_result['backoff_factor_results']:
        print(f"  {result['backoff_factor']}x backoff: {result['success_rate']:.1%} success, "
              f"{result['avg_time_per_success']*1000:.1f}ms avg time")


def main():
    """Main benchmark runner."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run retry effectiveness benchmarks")
    parser.add_argument("--iterations", type=int, default=1000,
                       help="Number of iterations per scenario")
    parser.add_argument("--concurrent", action="store_true",
                       help="Run concurrent retry benchmark")
    parser.add_argument("--optimize", action="store_true",
                       help="Run parameter optimization")
    parser.add_argument("--output", type=str, help="Output file for results (JSON)")
    
    args = parser.parse_args()
    
    all_results = {}
    
    # Run effectiveness benchmarks
    benchmark = RetryEffectivenessBenchmark()
    effectiveness_results = benchmark.run_all_scenarios(args.iterations)
    print_retry_results(effectiveness_results)
    all_results['effectiveness'] = [
        {
            'scenario_name': r.scenario_name,
            'success_rate': r.success_rate,
            'average_retries_per_success': r.average_retries_per_success,
            'average_time_per_success': r.average_time_per_success,
            'retry_distribution': r.retry_distribution
        }
        for r in effectiveness_results
    ]
    
    # Run concurrent benchmark if requested
    if args.concurrent:
        concurrent_benchmark = ConcurrentRetryBenchmark()
        concurrent_result = concurrent_benchmark.run_concurrent_benchmark()
        print_concurrent_results(concurrent_result)
        all_results['concurrent'] = concurrent_result
    
    # Run optimization if requested
    if args.optimize:
        optimizer = RetryParameterOptimizer()
        optimization_result = optimizer.find_optimal_parameters()
        print_optimization_results(optimization_result)
        all_results['optimization'] = optimization_result
    
    # Save results if requested
    if args.output:
        import json
        with open(args.output, 'w') as f:
            json.dump(all_results, f, indent=2)
        print(f"\nResults saved to {args.output}")
    
    # Provide recommendations
    print("\n" + "=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)
    
    # Analyze effectiveness results
    high_success_scenarios = [r for r in effectiveness_results if r.success_rate >= 0.95]
    low_success_scenarios = [r for r in effectiveness_results if r.success_rate < 0.90]
    
    if high_success_scenarios:
        print("\n✅ High Success Rate Scenarios (≥95%):")
        for result in high_success_scenarios:
            print(f"  {result.scenario_name}: {result.success_rate:.1%}")
    
    if low_success_scenarios:
        print("\n⚠️  Low Success Rate Scenarios (<90%):")
        for result in low_success_scenarios:
            print(f"  {result.scenario_name}: {result.success_rate:.1%}")
        print("  Consider increasing max_retries or adjusting failure handling")
    
    # General recommendations
    print("\n📋 General Recommendations:")
    print("  • For network errors: Use max_retries=3-5 with backoff_factor=2.0")
    print("  • For rate limiting: Respect retry-after headers and use longer delays")
    print("  • For server errors: Use conservative backoff to avoid overwhelming servers")
    print("  • For high failure rates: Consider circuit breaker patterns")
    print("  • Monitor retry patterns in production to optimize parameters")


if __name__ == "__main__":
    main()

