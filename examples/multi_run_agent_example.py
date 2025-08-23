#!/usr/bin/env python3
"""
Example script demonstrating the MultiRunAgent functionality.

This script shows how to use the MultiRunAgent to run multiple agent instances
concurrently and synthesize their outputs for better results.
"""

import os
import json
import argparse
from typing import Optional

from codegen_client import CodegenClient


def main():
    """
    Run the MultiRunAgent example.
    """
    parser = argparse.ArgumentParser(description="MultiRunAgent Example")
    parser.add_argument("org_id", type=int, help="Organization ID")
    parser.add_argument("prompt", type=str, help="Prompt for the agent")
    parser.add_argument("--concurrency", "-c", type=int, default=3, help="Number of concurrent agent runs (1-20)")
    parser.add_argument("--repo-id", "-r", type=int, help="Repository ID (optional)")
    parser.add_argument("--model", "-m", type=str, help="Model to use (optional)")
    parser.add_argument("--temperature", "-t", type=float, default=0.7, help="Temperature for generation (0.0-1.0)")
    parser.add_argument("--synthesis-temperature", "-st", type=float, default=0.2, help="Temperature for synthesis (0.0-1.0)")
    parser.add_argument("--timeout", type=float, default=600.0, help="Maximum seconds to wait for completion")
    parser.add_argument("--output", "-o", type=str, help="Output file for results (JSON)")
    args = parser.parse_args()

    # Get API key from environment
    api_key = os.environ.get("CODEGEN_API_KEY")
    if not api_key:
        print("Error: CODEGEN_API_KEY environment variable is not set")
        return 1

    # Initialize client
    client = CodegenClient(api_key=api_key)

    # Validate concurrency
    if not 1 <= args.concurrency <= 20:
        print("Error: Concurrency must be between 1 and 20")
        return 1

    print(f"Running {args.concurrency} agent instances concurrently...")
    
    try:
        # Create multi-run agent
        result = client.multi_run_agent.create_multi_run(
            org_id=args.org_id,
            prompt=args.prompt,
            concurrency=args.concurrency,
            repo_id=args.repo_id,
            model=args.model,
            temperature=args.temperature,
            synthesis_temperature=args.synthesis_temperature,
            timeout=args.timeout,
        )
        
        print(f"\nSuccess! Completed multi-run agent with {len(result['candidates'])} successful runs")
        
        # Display the final synthesized output
        print("\nFinal Synthesized Output:")
        print("=" * 80)
        print(result["final"])
        print("=" * 80)
        
        # Save results to file if requested
        if args.output:
            with open(args.output, "w") as f:
                json.dump(result, f, indent=2)
            print(f"\nResults saved to {args.output}")
            
        return 0
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1


if __name__ == "__main__":
    exit(main())

