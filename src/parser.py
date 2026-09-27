import os
import pandas as pd
from typing import Iterator, Dict, Any
from src.models import TrainMessage
from src.utils.logger_util import LoggerUtility

# Fetch invalid records logger configured via JSON[cite: 1, 2]
invalid_logger = LoggerUtility.get_logger("InvalidRecordsLogger", is_invalid_record_logger=True)

class TrainDataParser:
    VALID_DIRECTIONS = {'NORTH', 'SOUTH', 'EAST', 'WEST'}
    REQUIRED_FIELDS = ['TrainId', 'Timestamp', 'TrackId', 'Speed', 'Direction']

    @classmethod
    def parse(cls, filepath: str) -> Iterator[TrainMessage]:
        """
        1. Reads raw file from CSV/JSON[cite: 1, 2].
        2. Recovers rows and checks for missing fields, bad timestamp, speed < 0, bad direction[cite: 1, 2].
        3. Writes invalid records separately via LoggerUtility[cite: 1, 2].
        4. Yields valid TrainMessage domain objects[cite: 1, 2].
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Input file not found: {filepath}")

        if filepath.endswith('.json'):
            df = pd.read_json(filepath, dtype=object)
        else:
            df = pd.read_csv(filepath, dtype=object)

        for index, row in df.iterrows():
            row_num = index + 2
            raw_dict: Dict[str, Any] = row.to_dict()
            
            error = cls._validate_row(raw_dict)
            if error:
                # Log invalid record separately[cite: 1, 2]
                invalid_logger.error(f"Row {row_num} Rejected: {error} | Data: {raw_dict}")
            else:
                yield TrainMessage(
                    train_id=str(raw_dict['TrainId']).strip(),
                    timestamp=pd.to_datetime(raw_dict['Timestamp']).to_pydatetime(),
                    track_id=str(raw_dict['TrackId']).strip(),
                    speed=float(raw_dict['Speed']),
                    direction=str(raw_dict['Direction']).strip().upper()
                )

    @classmethod
    def _validate_row(cls, raw: Dict[str, Any]) -> str | None:
        for field in cls.REQUIRED_FIELDS:
            val = raw.get(field)
            if pd.isna(val) or val is None or str(val).strip() == "":
                return f"Missing required field: '{field}'"

        try:
            pd.to_datetime(raw['Timestamp'], errors='raise')
        except Exception:
            return f"Invalid timestamp: '{raw['Timestamp']}'"

        try:
            speed = float(raw['Speed'])
            if speed < 0:
                return f"Negative speed not allowed: {speed}"
        except (ValueError, TypeError):
            return f"Invalid speed value: '{raw['Speed']}'"

        direction = str(raw['Direction']).strip().upper()
        if direction not in cls.VALID_DIRECTIONS:
            return f"Invalid direction value: '{raw['Direction']}'"

        return None