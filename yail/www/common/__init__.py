import os
import sys

__abs_file__ = os.path.abspath(__file__)
com_dir = os.path.dirname(__abs_file__)
www_dir = os.path.dirname(com_dir)
code_dir = os.path.dirname(www_dir)
sys.path.append(code_dir)
