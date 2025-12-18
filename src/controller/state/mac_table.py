from dataclasses import dataclass
from typing import Optional
import time


@dataclass
class MACEntry:
    mac: str
    port: int
    learned_at: float


class MACLearningTable:
    def __init__(self, timeout_seconds: int = 300):
        """
        Initialize the table.
        Implementation will enforce timeout on entries.
        """
        self.timeout_seconds = timeout_seconds
        self._entries: dict[str, MACEntry] = {}


    def learn(self, mac: str, port: int, now: Optional[float] = None):
        """Record a source MAC on an ingress port"""
        if now is None:
            now = time.time()
        self._entries[mac] = MACEntry(mac, port, now)
    def lookup(self, mac: str, now: Optional[float] = None) -> Optional[int]:
        """Lookup destination MAC and return port if present"""
        if now is None:
            now = time.time()
        entry = self._entries.get(mac)
        if entry is None:
            return None
        if now - entry.learned_at > self.timeout_seconds:
            del self._entries[mac]
            return None
        return entry.port

    def age_out(self, now: Optional[float] = None):
        """Expire stale entries"""
        if now is None:
            now = time.time()
        for mac, entry in list(self._entries.items()):
            if now - entry.learned_at > self.timeout_seconds:
                del self._entries[mac]

    def clear(self):
        """Clear all entries"""
        self._entries.clear()
