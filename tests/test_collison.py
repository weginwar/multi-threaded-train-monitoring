from src.parser import TrainDataParser

def test_collision_hazard_detection_from_csv(test_csv_path, repository, engine):
    collision_alerts = []

    # Process messages sequentially as they are recovered from the CSV
    for msg in TrainDataParser.parse(test_csv_path):
        # Update occupancy and get other trains on the same track
        other_occupants = repository.store_and_update_state(msg)
        
        # Check collision risk against current occupants
        alerts = engine.evaluate_collision_risk(msg, other_occupants)
        if alerts:
            collision_alerts.extend(alerts)

    # In test_suite_data.csv: TRN-HA (EAST) and TRN-HB (WEST) meet on TRK-COLLISION
    assert len(collision_alerts) >= 1
    head_on_alert = any(
        "CRITICAL: Head-on collision risk on Track TRK-COLLISION" in alert and
        "TRN-HA" in alert and "TRN-HB" in alert
        for alert in collision_alerts
    )
    assert head_on_alert is True, "Expected head-on collision alert between TRN-HA and TRN-HB"