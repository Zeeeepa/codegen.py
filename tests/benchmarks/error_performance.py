"""
Performance Benchmarks for Error Handling System

This module benchmarks the performance of the error handling system to ensure
that error processing doesn't significantly impact CLI performance.
"""

import time
import statistics
import sys
from typing import List, Dict, Any
from contextlib import contextmanager
from unittest.mock import Mock, patch

# Import the error handling system
sys.path.append('../..')
from cli.core.errors import (
    CLIError,
    ConfigurationError,
    AuthenticationCLIError,
    ValidationCLIError,
    NetworkCLIError,
    translate_sdk_error,
    handle_cli_error,
    ErrorHandler
)

from codegen_api import (
    AuthenticationError,
    ValidationError,
    RateLimitError,
    NetworkError,
    TimeoutError,
    ServerError,
    retry_with_backoff
)


class PerformanceBenchmark:
    """Base class for performance benchmarks."""
    
    def __init__(self, name: str):
        self.name = name
        self.results: List[float] = []
    
    @contextmanager
    def measure_time(self):
        """Context manager to measure execution time."""
        start_time = time.perf_counter()
        yield
        end_time = time.perf_counter()
        self.results.append(end_time - start_time)
    
    def run_benchmark(self, iterations: int = 1000) -> Dict[str, Any]:
        """Run the benchmark for specified iterations."""
        self.results.clear()
        
        for _ in range(iterations):
            with self.measure_time():
                self.benchmark_operation()
        
        return self.calculate_statistics()
    
    def benchmark_operation(self):
        """Override this method with the operation to benchmark."""
        raise NotImplementedError
    
    def calculate_statistics(self) -> Dict[str, Any]:
        """Calculate performance statistics."""
        if not self.results:
            return {}
        
        return {
            'name': self.name,
            'iterations': len(self.results),
            'mean': statistics.mean(self.results),
            'median': statistics.median(self.results),
            'min': min(self.results),
            'max': max(self.results),
            'std_dev': statistics.stdev(self.results) if len(self.results) > 1 else 0,
            'total_time': sum(self.results)
        }


class ErrorCreationBenchmark(PerformanceBenchmark):
    """Benchmark error object creation."""
    
    def __init__(self):
        super().__init__("Error Creation")
    
    def benchmark_operation(self):
        """Create various error objects."""
        CLIError("Test error", exit_code=1, suggestions=["Fix it"])
        ConfigurationError("Config error")
        AuthenticationCLIError("Auth error")
        ValidationCLIError("Validation error", field_errors={"field": ["error"]})
        NetworkCLIError("Network error")


class ErrorTranslationBenchmark(PerformanceBenchmark):
    """Benchmark SDK error translation."""
    
    def __init__(self):
        super().__init__("Error Translation")
        self.sdk_errors = [
            AuthenticationError("Auth failed", 401),
            ValidationError("Validation failed", 400),
            RateLimitError(60),
            NetworkError("Network failed"),
            TimeoutError("Timeout", 408),
            ServerError("Server error", 500)
        ]
    
    def benchmark_operation(self):
        """Translate SDK errors to CLI errors."""
        for sdk_error in self.sdk_errors:
            translate_sdk_error(sdk_error)


class ErrorDisplayBenchmark(PerformanceBenchmark):
    """Benchmark error display formatting."""
    
    def __init__(self):
        super().__init__("Error Display")
        self.cli_errors = [
            CLIError("Simple error"),
            ConfigurationError("Config error with suggestions"),
            ValidationCLIError("Validation error", field_errors={
                "field1": ["Error 1", "Error 2"],
                "field2": ["Error 3"]
            }),
            NetworkCLIError("Network error with details", 
                          suggestions=["Check connection", "Try again"])
        ]
    
    def benchmark_operation(self):
        """Format errors for display."""
        with patch('cli.core.errors.Console') as mock_console_class:
            mock_console = Mock()
            mock_console_class.return_value = mock_console
            
            for error in self.cli_errors:
                handle_cli_error(error)


class ErrorHandlerBenchmark(PerformanceBenchmark):
    """Benchmark ErrorHandler context manager."""
    
    def __init__(self):
        super().__init__("Error Handler Context Manager")
    
    def benchmark_operation(self):
        """Test ErrorHandler context manager overhead."""
        with ErrorHandler(verbose=False):
            # Simulate successful operation
            pass


class ErrorHandlerWithExceptionBenchmark(PerformanceBenchmark):
    """Benchmark ErrorHandler with exception handling."""
    
    def __init__(self):
        super().__init__("Error Handler with Exception")
    
    def benchmark_operation(self):
        """Test ErrorHandler with exception processing."""
        with patch('sys.exit'), patch('cli.core.errors.handle_cli_error'):
            try:
                with ErrorHandler(verbose=False):
                    raise CLIError("Test error")
            except SystemExit:
                pass


class RetryMechanismBenchmark(PerformanceBenchmark):
    """Benchmark retry mechanism performance."""
    
    def __init__(self):
        super().__init__("Retry Mechanism")
        self.call_count = 0
    
    def benchmark_operation(self):
        """Test retry mechanism with successful operation."""
        self.call_count = 0
        
        @retry_with_backoff(max_retries=3, base_delay=0.001)  # Very short delay for benchmarking
        def successful_operation():
            self.call_count += 1
            return "success"
        
        result = successful_operation()
        assert result == "success"
        assert self.call_count == 1


class RetryWithFailureBenchmark(PerformanceBenchmark):
    """Benchmark retry mechanism with failures."""
    
    def __init__(self):
        super().__init__("Retry with Failures")
        self.call_count = 0
    
    def benchmark_operation(self):
        """Test retry mechanism with eventual success."""
        self.call_count = 0
        
        @retry_with_backoff(max_retries=2, base_delay=0.001)
        def eventually_successful():
            self.call_count += 1
            if self.call_count < 2:
                raise NetworkError("Temporary failure")
            return "success"
        
        result = eventually_successful()
        assert result == "success"
        assert self.call_count == 2


class ComplexErrorScenarioBenchmark(PerformanceBenchmark):
    """Benchmark complex error handling scenarios."""
    
    def __init__(self):
        super().__init__("Complex Error Scenario")
    
    def benchmark_operation(self):
        """Test complex error handling flow."""
        with patch('sys.exit'), patch('cli.core.errors.handle_cli_error'):
            try:
                with ErrorHandler(verbose=True):
                    # Simulate SDK error that needs translation
                    sdk_error = ValidationError("Complex validation error", 400)
                    sdk_error.field_errors = {
                        "field1": ["Error 1", "Error 2"],
                        "field2": ["Error 3"],
                        "field3": ["Error 4", "Error 5", "Error 6"]
                    }
                    raise sdk_error
            except SystemExit:
                pass


class MemoryUsageBenchmark:
    """Benchmark memory usage of error handling."""
    
    def __init__(self):
        self.name = "Memory Usage"
    
    def run_benchmark(self, iterations: int = 1000) -> Dict[str, Any]:
        """Measure memory usage of error operations."""
        import tracemalloc
        
        # Start memory tracing
        tracemalloc.start()
        
        # Baseline memory
        baseline = tracemalloc.take_snapshot()
        
        # Create many errors
        errors = []
        for i in range(iterations):
            error = CLIError(f"Error {i}", suggestions=[f"Fix {i}", f"Try {i}"])
            errors.append(error)
        
        # Measure memory after error creation
        after_creation = tracemalloc.take_snapshot()
        
        # Translate errors
        translated_errors = []
        for i in range(iterations // 10):  # Fewer translations to avoid overwhelming
            sdk_error = AuthenticationError(f"SDK Error {i}", 401)
            cli_error = translate_sdk_error(sdk_error)
            translated_errors.append(cli_error)
        
        # Final memory measurement
        final_snapshot = tracemalloc.take_snapshot()
        
        # Calculate memory differences
        creation_diff = after_creation.compare_to(baseline, 'lineno')
        translation_diff = final_snapshot.compare_to(after_creation, 'lineno')
        
        tracemalloc.stop()
        
        return {
            'name': self.name,
            'iterations': iterations,
            'creation_memory_mb': sum(stat.size_diff for stat in creation_diff[:10]) / 1024 / 1024,
            'translation_memory_mb': sum(stat.size_diff for stat in translation_diff[:10]) / 1024 / 1024,
            'total_errors_created': len(errors),
            'total_errors_translated': len(translated_errors)
        }


def run_all_benchmarks(iterations: int = 1000) -> List[Dict[str, Any]]:
    """Run all performance benchmarks."""
    benchmarks = [
        ErrorCreationBenchmark(),
        ErrorTranslationBenchmark(),
        ErrorDisplayBenchmark(),
        ErrorHandlerBenchmark(),
        ErrorHandlerWithExceptionBenchmark(),
        RetryMechanismBenchmark(),
        RetryWithFailureBenchmark(),
        ComplexErrorScenarioBenchmark(),
    ]
    
    results = []
    
    print(f"Running {len(benchmarks)} performance benchmarks with {iterations} iterations each...")
    print("-" * 80)
    
    for benchmark in benchmarks:
        print(f"Running {benchmark.name}...", end=" ", flush=True)
        result = benchmark.run_benchmark(iterations)
        results.append(result)
        print(f"Done ({result['mean']*1000:.3f}ms avg)")
    
    # Run memory benchmark separately
    print("Running Memory Usage benchmark...", end=" ", flush=True)
    memory_benchmark = MemoryUsageBenchmark()
    memory_result = memory_benchmark.run_benchmark(iterations)
    results.append(memory_result)
    print("Done")
    
    return results


def print_benchmark_results(results: List[Dict[str, Any]]):
    """Print formatted benchmark results."""
    print("\n" + "=" * 80)
    print("PERFORMANCE BENCHMARK RESULTS")
    print("=" * 80)
    
    for result in results:
        if result['name'] == "Memory Usage":
            print(f"\n{result['name']}:")
            print(f"  Iterations: {result['iterations']}")
            print(f"  Creation Memory: {result['creation_memory_mb']:.3f} MB")
            print(f"  Translation Memory: {result['translation_memory_mb']:.3f} MB")
            print(f"  Errors Created: {result['total_errors_created']}")
            print(f"  Errors Translated: {result['total_errors_translated']}")
        else:
            print(f"\n{result['name']}:")
            print(f"  Iterations: {result['iterations']}")
            print(f"  Mean: {result['mean']*1000:.3f} ms")
            print(f"  Median: {result['median']*1000:.3f} ms")
            print(f"  Min: {result['min']*1000:.3f} ms")
            print(f"  Max: {result['max']*1000:.3f} ms")
            print(f"  Std Dev: {result['std_dev']*1000:.3f} ms")
            print(f"  Total Time: {result['total_time']*1000:.3f} ms")


def analyze_performance_regression(current_results: List[Dict[str, Any]], 
                                 baseline_results: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Analyze performance regression compared to baseline."""
    if not baseline_results:
        return {"status": "no_baseline", "message": "No baseline results for comparison"}
    
    regressions = []
    improvements = []
    
    # Create lookup for baseline results
    baseline_lookup = {result['name']: result for result in baseline_results}
    
    for current in current_results:
        name = current['name']
        if name in baseline_lookup and 'mean' in current:
            baseline = baseline_lookup[name]
            
            current_mean = current['mean']
            baseline_mean = baseline['mean']
            
            # Calculate percentage change
            change_percent = ((current_mean - baseline_mean) / baseline_mean) * 100
            
            if change_percent > 10:  # More than 10% slower
                regressions.append({
                    'name': name,
                    'change_percent': change_percent,
                    'current_mean': current_mean * 1000,
                    'baseline_mean': baseline_mean * 1000
                })
            elif change_percent < -10:  # More than 10% faster
                improvements.append({
                    'name': name,
                    'change_percent': abs(change_percent),
                    'current_mean': current_mean * 1000,
                    'baseline_mean': baseline_mean * 1000
                })
    
    return {
        'status': 'analyzed',
        'regressions': regressions,
        'improvements': improvements,
        'total_benchmarks': len(current_results)
    }


def main():
    """Main benchmark runner."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run error handling performance benchmarks")
    parser.add_argument("--iterations", type=int, default=1000, 
                       help="Number of iterations per benchmark")
    parser.add_argument("--output", type=str, help="Output file for results (JSON)")
    parser.add_argument("--baseline", type=str, help="Baseline results file for comparison")
    
    args = parser.parse_args()
    
    # Run benchmarks
    results = run_all_benchmarks(args.iterations)
    
    # Print results
    print_benchmark_results(results)
    
    # Save results if requested
    if args.output:
        import json
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to {args.output}")
    
    # Compare with baseline if provided
    if args.baseline:
        try:
            import json
            with open(args.baseline, 'r') as f:
                baseline_results = json.load(f)
            
            analysis = analyze_performance_regression(results, baseline_results)
            
            print("\n" + "=" * 80)
            print("PERFORMANCE REGRESSION ANALYSIS")
            print("=" * 80)
            
            if analysis['status'] == 'analyzed':
                if analysis['regressions']:
                    print("\n⚠️  PERFORMANCE REGRESSIONS DETECTED:")
                    for reg in analysis['regressions']:
                        print(f"  {reg['name']}: {reg['change_percent']:.1f}% slower "
                              f"({reg['current_mean']:.3f}ms vs {reg['baseline_mean']:.3f}ms)")
                
                if analysis['improvements']:
                    print("\n✅ PERFORMANCE IMPROVEMENTS:")
                    for imp in analysis['improvements']:
                        print(f"  {imp['name']}: {imp['change_percent']:.1f}% faster "
                              f"({imp['current_mean']:.3f}ms vs {imp['baseline_mean']:.3f}ms)")
                
                if not analysis['regressions'] and not analysis['improvements']:
                    print("\n✅ No significant performance changes detected")
            
        except Exception as e:
            print(f"\n❌ Error comparing with baseline: {e}")
    
    # Performance thresholds
    print("\n" + "=" * 80)
    print("PERFORMANCE ANALYSIS")
    print("=" * 80)
    
    warnings = []
    for result in results:
        if 'mean' in result:
            mean_ms = result['mean'] * 1000
            if mean_ms > 10:  # More than 10ms average
                warnings.append(f"{result['name']}: {mean_ms:.3f}ms (threshold: 10ms)")
    
    if warnings:
        print("\n⚠️  PERFORMANCE WARNINGS:")
        for warning in warnings:
            print(f"  {warning}")
    else:
        print("\n✅ All benchmarks within acceptable performance thresholds")


if __name__ == "__main__":
    main()

