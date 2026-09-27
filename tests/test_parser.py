import os
from src.parser import TrainDataParser
from src.utils.logger_util import LoggerUtility

def test_read_csv_and_validate_recovered_records(test_csv_path):
    valid_records = list(TrainDataParser.parse(test_csv_path))
    
    assert len(valid_records) == 9

    # Retrieve the unique per-test log file directly from the utility
    log_file = LoggerUtility.get_invalid_log_file()
    assert os.path.exists(log_file)
    with open(log_file, "r", encoding="utf-8") as f:
        log_content = f.read()

    assert "Missing required field: 'TrainId'" in log_content
    assert "Invalid timestamp: 'bad_timestamp_format'" in log_content
    assert "Negative speed not allowed: -25.0" in log_content
    assert "Invalid direction value: 'SIDEWAYS'" in log_content
    assert "Invalid speed value: 'fast_speed'" in log_content