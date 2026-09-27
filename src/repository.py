import threading
from typing import Set, List, Dict
from src.models import TrainMessage

class TrainRepository:
    def __init__(self):
        self._processed_hashes: Set[str] = set()
        self._valid_messages: List[TrainMessage] = []
        self._track_state: Dict[str, Dict[str, TrainMessage]] = {}
        self._lock = threading.Lock()

    def is_duplicate(self, msg: TrainMessage) -> bool:
        """Evaluates composite key of TrainId, Timestamp, and TrackId."""
        msg_hash = f"{msg.train_id}_{msg.timestamp.isoformat()}_{msg.track_id}"
        with self._lock:
            if msg_hash in self._processed_hashes:
                return True
            self._processed_hashes.add(msg_hash)
            return False

    def store_and_update_state(self, msg: TrainMessage) -> List[TrainMessage]:
        """Atomically stores message, updates train location, and returns other occupants on that track."""
        with self._lock:
            self._valid_messages.append(msg)
            
            if msg.track_id not in self._track_state:
                self._track_state[msg.track_id] = {}
            
            # Remove train from previous tracks
            for track, occupants in self._track_state.items():
                if track != msg.track_id and msg.train_id in occupants:
                    del occupants[msg.train_id]
                    
            # Gather other trains currently sharing this track
            other_occupants = [
                occupant for tid, occupant in self._track_state[msg.track_id].items()
                if tid != msg.train_id
            ]
            
            self._track_state[msg.track_id][msg.train_id] = msg
            return other_occupants

    def get_all_messages(self) -> List[TrainMessage]:
        with self._lock:
            return list(self._valid_messages)