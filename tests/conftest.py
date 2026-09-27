import os
import pytest
from src.engine import AnalyticsEngine
from src.repository import TrainRepository
from src.utils.logger_util import LoggerUtility

@pytest.fixture
def test_csv_path(request):
    """
    Initializes a unique log file per test execution and returns the CSV path.
    """
    test_name = request.node.name
    log_dir = "output_reports"
    os.makedirs(log_dir, exist_ok=True)
    
    unique_log_file = os.path.join(log_dir, f"{test_name}_invalid.log")
    
    if os.path.exists(unique_log_file):
        os.remove(unique_log_file)

    LoggerUtility.set_invalid_log_file(unique_log_file)

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(base_dir, "input_data", "test_suite_data.csv")
    assert os.path.exists(file_path), f"CSV sheet not found at {file_path}"
    return file_path

@pytest.fixture
def engine():
    return AnalyticsEngine(speed_limit=75.0)

@pytest.fixture
def repository():
    return TrainRepository()