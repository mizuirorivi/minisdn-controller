from typing import Protocol
from src.controller.state.mac_table import MACLearningTable

class ControllerIF(Protocol):
    mac_table: MACLearningTable