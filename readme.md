# Multi-Threaded Real-Time Train Monitoring System
 
A thread-safe railway monitoring service built in Python 3.12.
 
The system:
 
- Reads telemetry data from CSV files
- Validates records using Pandas
- Extracts valid entries
- Routes invalid records to dedicated log files
- Processes messages concurrently via a Producer-Consumer pattern
- Detects collision hazards
- Aggregates train speed analytics
- Generates Console, HTML, JSON, and XML reports
 
---
 
# System Architecture
 
```text
[ CSV Telemetry Data ]
│ (Raw read via Pandas)
▼
 
┌────────────────────────────────────────────────────────┐
│ TrainDataParser │
│ │
│ • Field existence checks │
│ • Timestamp ISO formatting checks │
│ • Direction validation │
│ (NORTH, SOUTH, EAST, WEST) │
│ • Speed validation │
│ (numeric & speed >= 0) │
└──────────────┬──────────────────────────┬──────────────┘
│ │
│ Valid Records │ Invalid Records
▼ ▼
 
┌──────────────────────────────┐ ┌─────────────────────┐
│ Threaded MessageProcessor │ │ Invalid Record Logs │
│ │ │ │
│ Producer-Consumer Pattern │ │ output_reports/ │
│ │ │ invalid_records.log │
│ Producer │ └─────────────────────┘
│ │
│ ▼
│ queue.Queue
│ │
│ ├────────┬────────┬────────┐
│ ▼ ▼ ▼ ▼
│ Worker Worker Worker Worker
└────────┬────────┬────────┬────────┘
│ │ │
▼ ▼ ▼
 
┌────────────────────────────────────────────────────────┐
│ Concurrency & State Layer │
│ │
│ ┌─────────────────────────┐ ┌──────────────────────┐ │
│ │ TrainRepository │ │ AnalyticsEngine │ │
│ │ │ │ │ │
│ │ • Thread-safe storage │ │ • Running averages │ │
│ │ • Deduplication cache │ │ • Overspeed alerts │ │
│ │ • Track occupancy │ │ • Collision risks │ │
│ └─────────────────────────┘ └──────────────────────┘ │
└──────────────────────────┬─────────────────────────────┘
│
▼
 
┌────────────────────────────────────────────────────────┐
│ ReportGenerator │
│ │
│ • Console Summary │
│ • Interactive HTML Dashboard │
│ • JSON Report Export │
│ • XML Report Export │
└────────────────────────────────────────────────────────┘
```
 
---
 
# Project Structure
 
```text
railway_project/
│
├── config/
│ └── logger_config.json
│
├── input_data/
│ ├── messages.csv
│ └── test_suite_data.csv
│
├── output_reports/
│ ├── app.log
│ ├── invalid_records.log
│ ├── test_report.html
│ ├── test_results.xml
│ ├── train_summary.html
│ ├── train_summary.json
│ └── train_summary.xml
│
├── src/
│ ├── __init__.py
│ ├── main.py
│ ├── models.py
│ ├── parser.py
│ ├── repository.py
│ ├── engine.py
│ ├── processor.py
│ ├── report.py
│ │
│ └── utils/
│ ├── __init__.py
│ └── logger_util.py
│
├── tests/
│ ├── __init__.py
│ ├── conftest.py
│ ├── test_parser.py
│ ├── test_repository.py
│ ├── test_engine.py
│ ├── test_collision.py
│ ├── test_threaded_processor.py
│ └── test_report.py
│
├── Pipfile
├── Pipfile.lock
├── pytest.ini
└── README.md
```
 
---
 
# Environment Setup
 
## Requirements
 
- Python 3.12+
- Pipenv
 
---
 
## Create Virtual Environment
 
```bash
pipenv --python 3.12
```
 
---
 
## Install Dependencies
 
```bash
pipenv install
```
 
Install development dependencies:
 
```bash
pipenv install --dev
```
 
---
 
# Running the Application
 
```bash
pipenv run python -m src.main
```
 
---
 
# Running Tests
 
All tests operate directly on:
 
```text
input_data/test_suite_data.csv
```
 
No mocks or hard-coded test data are required.
 
---
 
## Run All Tests
 
```bash
pipenv run pytest
```
 
---
 
## Run Tests with Verbose Output
 
```bash
pipenv run pytest -s -v
```
 
---
 
## Run a Single Test File
 
```bash
pipenv run pytest tests/test_parser.py
```
 
---
 
# Test Artifacts Generated
 
| Artifact | Description |
|-----------|------------|
| test_report.html | Pytest execution report |
| test_results.xml | JUnit XML report |
| invalid_records.log | Invalid telemetry records |
| train_summary.html | Business analytics dashboard |
| train_summary.json | JSON export |
| train_summary.xml | XML export |
 
---
 
# Test Suite Coverage
 
## test_parser.py
 
### test_read_csv_and_validate_recovered_records
 
Validates:
 
- CSV parsing
- Missing fields
- Invalid timestamps
- Negative speeds
- Invalid directions
 
Confirms:
 
- Invalid records are logged
- Valid records become TrainMessage objects
 
---
 
## test_repository.py
 
### test_duplicate_handling_from_csv
 
Validates:
 
- Composite key deduplication
 
Based on:
 
```text
(TrainId, Timestamp, TrackId)
```
 
Confirms repeated messages are ignored.
 
---
 
## test_engine.py
 
### test_speed_calculations_and_overspeed_from_csv
 
Validates:
 
- Running averages
- Maximum speed detection
- Overspeed threshold (>75 mph)
 
---
 
## test_collision.py
 
### test_collision_hazard_detection_from_csv
 
Validates:
 
- Head-on collision detection
- Same-track occupancy conflicts
 
---
 
## test_threaded_processor.py
 
### test_threaded_pipeline_execution_from_csv
 
Validates:
 
- Multi-threaded queue processing
- Worker coordination
- Thread safety
- Lost-update prevention
 
---
 
## test_report.py
 
### test_generate_all_reports_from_csv
 
Validates generation of:
 
- HTML Dashboard
- JSON Export
- XML Export
 
---
 
# Concurrency Risks Addressed
 
## Deduplication Race Condition
 
### Risk
 
Two workers process the same message simultaneously.
 
### Resolution
 
```python
TrainRepository._lock
```
 
ensures atomic check-and-insert behavior.
 
---
 
## Spatial Occupancy Desynchronization
 
### Risk
 
Track occupancy becomes inconsistent during concurrent updates.
 
### Resolution
 
```python
store_and_update_state()
```
 
performs atomic occupancy transitions.
 
---
 
## Analytics Lost Updates
 
### Risk
 
Operations such as:
 
```python
speed_sum += msg.speed
total_messages += 1
```
 
lose updates under concurrent execution.
 
### Resolution
 
```python
AnalyticsEngine._lock
```
 
protects all aggregation operations.
 
---
 
## Test Log Cross Contamination
 
### Risk
 
Multiple tests write to the same log file.
 
### Resolution
 
```python
LoggerUtility.set_invalid_log_file()
```
 
creates isolated log targets per test.
 
---
 
# Known Limitations
 
## In-Memory Volatility
 
All runtime state exists in RAM.
 
A restart clears:
 
- Deduplication cache
- Track occupancy
- Analytics state
 
---
 
## Global Lock Contention
 
Heavy worker counts can increase contention on shared locks.
 
---
 
## Large Dataset Loading
 
Current implementation loads complete CSV files into memory.
 
---
 
# Scaling to 10M+ Messages
 
## Chunked CSV Processing
 
Use Pandas chunking:
 
```python
pd.read_csv(filepath, chunksize=50000)
```
 
to avoid loading multi-GB files into memory.
 
---
 
## Distributed Messaging
 
Replace:
 
```python
queue.Queue
```
 
with:
 
- Apache Kafka
- RabbitMQ
 
Partition by:
 
```text
track_id
```
 
to scale horizontally.
 
---
 
## Probabilistic Deduplication
 
Replace:
 
```python
set()
```
 
with:
 
- Bloom Filters
- Redis Bloom Filters
 
for memory-efficient duplicate tracking.
 
---
 
## External State Storage
 
Move occupancy and train state to:
 
- Redis
- Valkey
 
to support distributed worker nodes.
 
---
 
# Outputs Generated
 
The system produces:
 
- Console Report
- HTML Dashboard
- JSON Export
- XML Export
- Invalid Record Logs
- Pytest HTML Reports
- JUnit XML Reports
 
making it suitable for analytics, monitoring, auditing, and integration workflows.