from Order import Order
import pandas as pd



# Strategy class will directly manipulate candles and positions itself
class Accounting():
    def __init__(self, equity, comission, candles_limit=10000) -> None:
        # history informations, update whenever a buy or sell happened
        self.history_positions = {}
        self.history_equities = []

        # current informations
        self.positions = []
        self.ongoing_orders = {}
        self.candles = {}
        self.euity = equity
        self.comission = comission

    def setFund(self, value):
        self.equity = value

    def addComodity(self, comodity_name:str, candle:pd.DataFrame):
        self.candles[comodity_name] = candle

    def deleteComodity(self, comodity_name:str):
        del self.candles[comodity_name]      

    def addOngoingOrder(self, order: Order):
        self.ongoing_orders.append(order)
        return len(self.ongoing_orders) - 1 # return the order id 

    def deleteOngoingOrder(self, order_id):
        del self.ongoing_orders

    def updateCandles(self):
        pass



