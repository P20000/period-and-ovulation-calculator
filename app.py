#!/usr/bin/env python3
"""
Application alias entry point.
Invokes main.py with platform auto-detection and modern modular architecture.
"""

import sys
from main import main

if __name__ == "__main__":
    sys.exit(main())
