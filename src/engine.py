import threading
from src.models import TrainMessage

class AnalyticsEngine:
    def __init__(self, speed_limit: float = 75.0):
        self.speed_limit = speed_limit
        self.summaries: dict[str, dict] = {}
        self._lock = threading.Lock()

    def process_message(self, msg: TrainMessage):
        """Thread-safe update of aggregations and spatial history."""
        with self._lock:
            if msg.train_id not in self.summaries:
                self.summaries[msg.train_id] = {
                    "total_messages": 0,
                    "max_speed": 0.0,
                    "speed_sum": 0.0,
                    "last_known_track": "",
                    "latest_time": msg.timestamp,
                    "overspeed_violations": 0
                }
                
            summary = self.summaries[msg.train_id]
            summary["total_messages"] += 1
            summary["max_speed"] = max(summary["max_speed"], msg.speed)
            summary["speed_sum"] += msg.speed
            
            if msg.timestamp >= summary["latest_time"]:
                summary["last_known_track"] = msg.track_id
                summary["latest_time"] = msg.timestamp
                
            if msg.speed > self.speed_limit:
                summary["overspeed_violations"] += 1

    def evaluate_collision_risk(self, msg: TrainMessage, other_occupants: list[TrainMessage]) -> list[str]:
        """Evaluates head-on or rear-end risks based on direction and speed differential."""
        alerts = []
        for other in other_occupants:
            if msg.direction != other.direction:
                alerts.append(
                    f"CRITICAL: Head-on collision risk on Track {msg.track_id} "
                    f"between {msg.train_id} ({msg.direction}) and {other.train_id} ({other.direction})."
                )
            elif msg.direction == other.direction and msg.speed > other.speed:
                alerts.append(
                    f"WARNING: Rear-end risk on Track {msg.track_id}. "
                    f"{msg.train_id} ({msg.speed} mph) approaching {other.train_id} ({other.speed} mph)."
                )
        return alerts

    def get_calculated_summaries(self) -> dict[str, dict]:
        with self._lock:
            results = {}
            for tid, data in self.summaries.items():
                avg = data["speed_sum"] / data["total_messages"] if data["total_messages"] > 0 else 0.0
                results[tid] = {
                    "Total Messages": data["total_messages"],
                    "Max Speed": data["max_speed"],
                    "Average Speed": round(avg, 2),
                    "Last Known Track": data["last_known_track"],
                    "Overspeed Violations": data["overspeed_violations"]
                }
            return results