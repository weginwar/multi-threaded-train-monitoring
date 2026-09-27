import os
from src.parser import TrainDataParser
from src.repository import TrainRepository
from src.engine import AnalyticsEngine
from src.processor import MessageProcessor
from src.report import ReportGenerator
from src.utils.logger_util import LoggerUtility

def main():
    LoggerUtility.load_config("config/logger_config.json")
    os.makedirs('output_reports', exist_ok=True)
    os.makedirs('input_data', exist_ok=True)

    repository = TrainRepository()
    engine = AnalyticsEngine(speed_limit=75.0)
    processor = MessageProcessor(repository, engine, num_workers=4)
    reporter = ReportGenerator(engine, processor)

    print("Starting multi-threaded consumer workers...")
    processor.start_consumers()

    csv_path = "input_data/messages.csv"
    print(f"Producer reading stream from: {csv_path}")
    valid_stream = TrainDataParser.parse(csv_path)
    
    processor.produce(valid_stream)
    processor.stop()

    reporter.generate_console_summary()
    # Generate persistent reports in output_reports/
    html_file = reporter.generate_html_report("output_reports/train_summary.html")
    json_file = reporter.generate_json_report("output_reports/train_summary.json")
    xml_file = reporter.generate_xml_report("output_reports/train_summary.xml")

    print(f"\nReports successfully generated:")
    print(f" - HTML Dashboard : {html_file}")
    print(f" - JSON Report    : {json_file}")
    print(f" - XML Report     : {xml_file}")

if __name__ == "__main__":
    main()