import os
import json
import xml.etree.ElementTree as ET
from src.parser import TrainDataParser
from src.processor import MessageProcessor
from src.report import ReportGenerator


def test_generate_all_reports_from_csv(test_csv_path, repository, engine):
    """
    1. Reads and processes records directly from test_suite_data.csv.
    2. Runs ReportGenerator to generate HTML, JSON, and XML reports.
    3. Verifies file creation and content integrity.
    """
    # Step 1: Process real CSV data through workers
    processor = MessageProcessor(repository, engine, num_workers=2)
    processor.start_consumers()
    processor.produce(TrainDataParser.parse(test_csv_path))
    processor.stop()

    # Step 2: Initialize ReportGenerator
    reporter = ReportGenerator(engine=engine, processor=processor)

    # Define unique test report output targets
    html_target = "output_reports/test_train_summary.html"
    json_target = "output_reports/test_train_summary.json"
    xml_target = "output_reports/test_train_summary.xml"

    # --- Test 1: HTML Report ---
    html_path = reporter.generate_html_report(html_target)
    assert os.path.exists(html_path)
    
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    # Check headers and table records
    assert "Train Analytics Dashboard" in html_content
    assert "TRN-V1" in html_content
    assert "TRK-20" in html_content
    assert "CRITICAL: Head-on collision risk on Track TRK-COLLISION" in html_content

    # --- Test 2: JSON Report ---
    json_path = reporter.generate_json_report(json_target)
    assert os.path.exists(json_path)

    with open(json_path, "r", encoding="utf-8") as f:
        json_data = json.load(f)

    assert "summaries" in json_data
    assert "alerts" in json_data
    assert "TRN-V1" in json_data["summaries"]
    assert json_data["summaries"]["TRN-V1"]["Max Speed"] == 100.0
    assert json_data["summaries"]["TRN-V1"]["Average Speed"] == 50.0
    assert any("TRK-COLLISION" in alert for alert in json_data["alerts"])

    # --- Test 3: XML Report ---
    xml_path = reporter.generate_xml_report(xml_target)
    assert os.path.exists(xml_path)

    tree = ET.parse(xml_path)
    root = tree.getroot()

    assert root.tag == "TrainReport"
    
    # Verify XML structure and element tags
    train_ids = [t.attrib["id"] for t in root.findall(".//Train")]
    assert "TRN-V1" in train_ids
    assert "TRN-V2" in train_ids

    alerts = [a.text for a in root.findall(".//Alert")]
    assert any("TRK-COLLISION" in alert for alert in alerts)