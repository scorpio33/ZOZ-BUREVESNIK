#!/usr/bin/env python3
import pytest
import sys
from pathlib import Path

def main():
    root_dir = Path(__file__).parent.parent
    test_dir = str(root_dir / 'tests')
    
    args = [
        test_dir,
        "-v",
        "--tb=short",
        "--disable-warnings",
        "--no-header",
        "--show-capture=no",
        "--asyncio-mode=strict",
        "--asyncio-default-fixture-loop-scope=session",
        "-p", "no:warnings",
    ]
    
    sys.exit(pytest.main(args))

if __name__ == '__main__':
    main()
