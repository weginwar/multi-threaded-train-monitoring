from src.parser import TrainDataParser

def test_duplicate_handling_from_csv(test_csv_path, repository):
    # Recover only the TRN-DUP records from the CSV file
    dup_messages = [msg for msg in TrainDataParser.parse(test_csv_path) if msg.train_id == "TRN-DUP"]
    assert len(dup_messages) == 2, "Expected exactly 2 TRN-DUP entries in CSV"

    # Message 1: First appearance -> Not a duplicate
    assert repository.is_duplicate(dup_messages[0]) is False
    repository.store_and_update_state(dup_messages[0])

    # Message 2: Identical (TrainId, Timestamp, TrackId) -> Must be flagged as duplicate
    assert repository.is_duplicate(dup_messages[1]) is True

    # Assert repository only stores the unique record
    stored = [m for m in repository.get_all_messages() if m.train_id == "TRN-DUP"]
    assert len(stored) == 1