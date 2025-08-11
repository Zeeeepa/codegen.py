"""
Allow codegenapi to be executed as a module: python -m codegenapi
"""

import sys
from .cli import main

if __name__ == "__main__":
    sys.exit(main())

