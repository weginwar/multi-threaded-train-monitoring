import os
import json
import xml.etree.ElementTree as ET
from typing import Optional

from src.engine import AnalyticsEngine
from src.processor import MessageProcessor


class ReportGenerator:
    def __init__(
        self,
        engine: AnalyticsEngine,
        processor: Optional[MessageProcessor] = None
    ):
        self.engine = engine
        self.processor = processor

    def generate_console_summary(self):
        """Print formatted analytics to console."""

        summaries = self.engine.get_calculated_summaries()

        print("\n================== TRAIN SUMMARY REPORT ==================")

        for train_id, data in summaries.items():
            print(f"\nTrain ID: {train_id}")

            for key, value in data.items():
                print(f"  {key:22}: {value}")

        print("\n==================== COLLISION ALERTS ====================")

        alerts = self.processor.alerts if self.processor else []

        if alerts:
            for alert in alerts:
                print(f"  [ALERT] {alert}")
        else:
            print("  No collision hazards detected.")

        print("==========================================================\n")

    def generate_html_report(
        self,
        output_path: str = "output_reports/train_summary.html"
    ) -> str:
        """
        Generates a styled HTML dashboard containing train
        analytics and collision alerts.
        """

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        summaries = self.engine.get_calculated_summaries()
        alerts = self.processor.alerts if self.processor else []

        total_trains = len(summaries)

        total_violations = sum(
            item["Overspeed Violations"]
            for item in summaries.values()
        )

        table_rows = []

        for train_id, data in summaries.items():

            table_rows.append(
                f"""
                <tr>
                    <td>{train_id}</td>
                    <td>{data["Total Messages"]}</td>
                    <td>{data["Max Speed"]}</td>
                    <td>{data["Average Speed"]}</td>
                    <td>{data["Last Known Track"]}</td>
                    <td>{data["Overspeed Violations"]}</td>
                </tr>
                """
            )

        alert_html = ""

        if alerts:
            for alert in alerts:
                alert_html += f"""
                <div class="alert">
                    {alert}
                </div>
                """
        else:
            alert_html = """
            <div class="success">
                No collision hazards detected.
            </div>
            """

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Train Analytics Dashboard</title>

            <style>

                body {{
                    font-family: Arial, sans-serif;
                    margin: 30px;
                    background-color: #f5f7fa;
                }}

                h1 {{
                    color: #2c3e50;
                }}

                .cards {{
                    display: flex;
                    gap: 20px;
                    margin-bottom: 30px;
                }}

                .card {{
                    background-color: white;
                    padding: 20px;
                    border-radius: 10px;
                    min-width: 200px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                }}

                .card h3 {{
                    margin: 0;
                    color: #555;
                }}

                .card h2 {{
                    color: #3498db;
                    margin-top: 10px;
                }}

                table {{
                    width: 100%;
                    border-collapse: collapse;
                    background: white;
                }}

                th {{
                    background-color: #34495e;
                    color: white;
                    padding: 12px;
                }}

                td {{
                    padding: 10px;
                    text-align: center;
                    border-bottom: 1px solid #ddd;
                }}

                tr:hover {{
                    background-color: #f4f4f4;
                }}

                .alert {{
                    background-color: #ffe5e5;
                    padding: 12px;
                    border-left: 6px solid red;
                    margin-bottom: 10px;
                }}

                .success {{
                    background-color: #eafbea;
                    padding: 12px;
                    border-left: 6px solid green;
                }}

            </style>
        </head>

        <body>

            <h1>🚆 Train Analytics Dashboard</h1>

            <div class="cards">

                <div class="card">
                    <h3>Total Trains</h3>
                    <h2>{total_trains}</h2>
                </div>

                <div class="card">
                    <h3>Total Alerts</h3>
                    <h2>{len(alerts)}</h2>
                </div>

                <div class="card">
                    <h3>Overspeed Violations</h3>
                    <h2>{total_violations}</h2>
                </div>

            </div>

            <h2>Train Summary</h2>

            <table>

                <tr>
                    <th>Train ID</th>
                    <th>Total Messages</th>
                    <th>Max Speed</th>
                    <th>Average Speed</th>
                    <th>Last Known Track</th>
                    <th>Overspeed Violations</th>
                </tr>

                {''.join(table_rows)}

            </table>

            <h2>Collision Alerts</h2>

            {alert_html}

        </body>
        </html>
        """

        with open(output_path, "w", encoding="utf-8") as file:
            file.write(html_content)

        return output_path

    def generate_json_report(
        self,
        output_path: str = "output_reports/train_summary.json"
    ) -> str:

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        report = {
            "summaries": self.engine.get_calculated_summaries(),
            "alerts": self.processor.alerts if self.processor else []
        }

        with open(output_path, "w", encoding="utf-8") as file:
            json.dump(report, file, indent=4)

        return output_path

    def generate_xml_report(
        self,
        output_path: str = "output_reports/train_summary.xml"
    ) -> str:

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        root = ET.Element("TrainReport")

        summaries_elem = ET.SubElement(root, "Summaries")

        for train_id, data in self.engine.get_calculated_summaries().items():

            train_elem = ET.SubElement(
                summaries_elem,
                "Train",
                id=train_id
            )

            for key, value in data.items():
                metric = ET.SubElement(
                    train_elem,
                    key.replace(" ", "_")
                )
                metric.text = str(value)

        alerts_elem = ET.SubElement(root, "Alerts")

        if self.processor:
            for alert in self.processor.alerts:
                alert_elem = ET.SubElement(alerts_elem, "Alert")
                alert_elem.text = alert

        tree = ET.ElementTree(root)

        tree.write(
            output_path,
            encoding="utf-8",
            xml_declaration=True
        )

        return output_path