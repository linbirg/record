import os
import sys


__abs_file__ = os.path.abspath(__file__)
lib_dir = os.path.dirname(__abs_file__)
test_dir = os.path.dirname(lib_dir)
code_dir = os.path.dirname(test_dir)
sys.path.append(code_dir)


from lib import logger

logger.LOG_DEBUG("hello")