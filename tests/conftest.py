import sys
from pathlib import Path

import pytest


@pytest.fixture(scope="function")
def sys_path_input():
    """
    Add the input directory to sys.path
    """
    test_dir = str(Path(__file__).parent / "input")
    sys.path.append(test_dir)
    yield
    sys.path.remove(test_dir)
