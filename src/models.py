from dataclasses import dataclass
from datetime import datetime
from enum import Enum



@dataclass(frozen=True)
class TrainMessage:
    train_id:str
    track_id:str
    timestamp:datetime
    speed:float
    direction:str


