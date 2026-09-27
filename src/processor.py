import threading
import queue
from typing import List, Iterable
from src.models import TrainMessage
from src.repository import TrainRepository
from src.engine import AnalyticsEngine

class MessageProcessor:
    def __init__(self, repository: TrainRepository, engine: AnalyticsEngine, num_workers: int = 4):
        self.repository = repository
        self.engine = engine
        self.message_queue: queue.Queue = queue.Queue()
        self.workers: List[threading.Thread] = []
        self.num_workers = num_workers
        self.alerts: List[str] = []
        self._alert_lock = threading.Lock()
        self._stop_event = threading.Event()

    def start_consumers(self):
        self._stop_event.clear()
        for i in range(self.num_workers):
            t = threading.Thread(target=self._worker_loop, name=f"ConsumerWorker-{i}", daemon=True)
            t.start()
            self.workers.append(t)

    def produce(self, messages: Iterable[TrainMessage]):
        for msg in messages:
            self.message_queue.put(msg)
        self.message_queue.join()

    def stop(self):
        self._stop_event.set()

    def _worker_loop(self):
        while not self._stop_event.is_set() or not self.message_queue.empty():
            try:
                msg: TrainMessage = self.message_queue.get(timeout=0.1)
                if not self.repository.is_duplicate(msg):
                    other_occupants = self.repository.store_and_update_state(msg)
                    self.engine.process_message(msg)
                    
                    new_alerts = self.engine.evaluate_collision_risk(msg, other_occupants)
                    if new_alerts:
                        with self._alert_lock:
                            self.alerts.extend(new_alerts)
                self.message_queue.task_done()
            except queue.Empty:
                continue