from src.parser import TrainDataParser

def test_speed_calculations_and_overspeed_from_csv(test_csv_path, engine):
    # Stream valid records from CSV into the analytics engine
    for msg in TrainDataParser.parse(test_csv_path):
        engine.process_message(msg)

    summaries = engine.get_calculated_summaries()

    # --- 1. Validate Calculations for TRN-V1 (Speeds: 50.0, 100.0, 0.0) ---
    assert "TRN-V1" in summaries
    v1 = summaries["TRN-V1"]
    assert v1["Total Messages"] == 3
    assert v1["Max Speed"] == 100.0
    assert v1["Average Speed"] == 50.0  # (50 + 100 + 0) / 3
    assert v1["Last Known Track"] == "TRK-20"
    assert v1["Overspeed Violations"] == 1  # 100.0 > 75.0

    # --- 2. Validate Boundary Conditions for Overspeed (Limit = 75.0) ---
    # TRN-V2 speed is exactly 75.0 -> Must NOT trigger an overspeed violation
    assert "TRN-V2" in summaries
    assert summaries["TRN-V2"]["Max Speed"] == 75.0
    assert summaries["TRN-V2"]["Overspeed Violations"] == 0

    # TRN-V3 speed is 76.0 -> Must trigger exactly 1 overspeed violation
    assert "TRN-V3" in summaries
    assert summaries["TRN-V3"]["Max Speed"] == 76.0
    assert summaries["TRN-V3"]["Overspeed Violations"] == 1