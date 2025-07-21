#!/usr/bin/env python3
"""
Simple test runner for the speech sentiment analysis system.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from test_pipeline import PipelineTester

async def main():
    """Run all tests."""
    logging.basicConfig(level=logging.INFO)
    
    tester = PipelineTester()
    success = await tester.run_all_tests()
    
    if success:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print("\n❌ Some tests failed!")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)