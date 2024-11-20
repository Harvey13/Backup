from dataclasses import dataclass
from typing import Optional

@dataclass
class Progress:
    current: int = 0
    total: int = 0
    status: str = 'pending'  # pending, syncing, completed, error

@dataclass
class FolderPair:
    source: str
    destination: str
    progress: Optional[Progress] = None