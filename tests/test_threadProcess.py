from src.parser import TrainDataParser
from src.processor import MessageProcessor

def test_threaded_pipeline_execution_from_csv(test_csv_path, repository, engine):
    processor = MessageProcessor(repository, engine, num_workers=4)
    processor.start_consumers()

    # Producer streams records recovered from CSV into the queue
    stream = TrainDataParser.parse(test_csv_path)
    processor.produce(stream)
    processor.stop()

    summaries = engine.get_calculated_summaries()

    # Rejected records from CSV must never appear in final analytics
    assert "TRN-ERR-TIME" not in summaries
    assert "TRN-ERR-SPD" not in summaries
    assert "TRN-ERR-DIR" not in summaries

    # TRN-DUP appeared twice in CSV, but summary Total Messages must be 1 due to deduplication
    assert summaries["TRN-DUP"]["Total Messages"] == 1

    # Verify head-on collision was captured concurrently across worker threads
    assert any("CRITICAL: Head-on collision risk on Track TRK-COLLISION" in a for a in processor.alerts)