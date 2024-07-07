from Accounting import Accounting
from Broker import Broker
import time
import asyncio

class Order():
    def __init__(self, order_id, symbol, base, quote_amount, units, direction, comodity_type) -> None:
        self.symbol = symbol
        self.order_id = order_id
        self.base = base
        self.quote_amount = quote_amount
        self.units = units
        self.direction = direction # long or short
        self.comodity_type = comodity_type

class LimitOrder(Order):
    def __init__(self, order_id, symbol, base, quote_amount, units, direction, comodity_type, limit_price) -> None:
        super().__init__(order_id, symbol, base, quote_amount, units, direction, comodity_type)
        self.limit_price = limit_price

class MarketOrder(Order):
    def __init__(self, order_id, symbol, base, quote_amount, units, direction, comodity_type) -> None:
        super().__init__(order_id, symbol, base, quote_amount, units, direction, comodity_type)





