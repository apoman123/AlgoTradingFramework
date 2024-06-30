from Accounting import Accounting
from Broker import Broker

class Order():
    def __init__(self, order_id, base, quote_amount, units, direction, accounting: Accounting, broker:Broker) -> None:
        self.order_id = order_id
        self.base = base
        self.quote_amount = quote_amount
        self.units = units
        self.direction = direction # long or short
        self.accounting = accounting
        self.broker = broker

    def checkIfFilled(self):
        pass

    def orderFilled(self):
        self.accounting.deleteOngoingOrder(self.order_id)

class LimitOrder(Order):
    def __init__(self, order_id, base, quote_amount, units, direction, limit_price, accounting: Accounting, broker:Broker) -> None:
        super().__init__(order_id, base, quote_amount, units, direction, accounting, broker)
        self.limit_price = limit_price

class MarketOrder(Order):
    def __init__(self, order_id, base, quote_amount, units, direction) -> None:
        super().__init__(order_id, base, quote_amount, units, direction)
        

