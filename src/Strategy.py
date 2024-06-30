from abc import ABC
import talib

class Strategy(ABC):
    def __init__(self, broker, accounting) -> None:
        self.broker = broker
        self.accounting = accounting
    
    