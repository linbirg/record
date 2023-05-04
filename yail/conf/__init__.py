import os
import sys

__abs_file__ = os.path.abspath(__file__)
conf_dir = os.path.dirname(__abs_file__)
code_dir = os.path.dirname(conf_dir)
sys.path.append(code_dir)