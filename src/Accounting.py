from Order import Order
import pandas as pd
import time


# Strategy class will directly manipulate candles and positions itself
class Accounting():
    def __init__(self, equity, comission, leverage) -> None:
        # history informations, update whenever a buy or sell happened
        self.history_positions = {}
        self.history_equities = []

        # current informations
        self.leverage = leverage
        self.comission = comission
        self.positions = {"long": [], "short":[]}   # positions structure would be {
                                                    # "long": [{"symbol": symbol, "units": units, "bought_price": price, "position_type": position_type}...],
                                                    # "short": [{"symbol": symbol, "units": units, "bought_price": price, "position_type": position_type}...]
                                                    # }

        self.ongoing_orders = {} # ongoing_orders structure would be {"order_id": Order}
        self.candles = {} # candles structure would be {timeframe: {symbol:candles, ...}}
        self.euity = equity

    def addOngoingOrder(self, order: Order):
        self.ongoing_orders[Order.order_id] = Order

    def deleteOngoingOrder(self, order_id):
        del self.ongoing_orders[order_id]





