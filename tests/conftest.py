# Ensure 'src' is importable in tests when running from project root
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
SRC_PATH = os.path.join(PROJECT_ROOT, "..", "src")
SRC_ABS = os.path.abspath(SRC_PATH)
if SRC_ABS not in sys.path:
    sys.path.insert(0, SRC_ABS)
