#!/usr/bin/env python3
"""
Simple CLI interface for the Python Open SWE agent.
"""

import sys
import json
from src.enhanced_graph import run_enhanced_agent
from visuals import print_welcome_message


def main():
    """Main CLI interface."""
    if len(sys.argv) < 2:
        print("Usage: python cli.py 'Your coding request here'")
        print("Example: python cli.py 'Create a Python function to calculate fibonacci numbers'")
        sys.exit(1)
    
    request = " ".join(sys.argv[1:])
    print(f"🤖 Processing request: {request}")
    print("=" * 60)
    
    # Run the agent
    result = run_enhanced_agent(request)
    
    # Display results
    print(f"\n📊 Status: {result['status']}")
    
    if result.get('error_message'):
        print(f"❌ Error: {result['error_message']}")
    
    if result.get('plan'):
        print(f"\n📋 Plan:")
        print("-" * 40)
        print(result['plan'])
    
    if result.get('code_changes'):
        print(f"\n💻 Code Implementation:")
        print("-" * 40)
        for i, code in enumerate(result['code_changes'], 1):
            print(f"\n--- Implementation {i} ---")
            print(code)
    
    print(f"\n🔄 Total iterations: {result.get('iteration_count', 0)}")
    print("=" * 60)
    print("✅ Complete!")


if __name__ == "__main__":
    print_welcome_message()

    main()