from abc import ABC, abstractmethod
from Order import Order
from ccxt import binance

class Broker(ABC): # implement the details on the restful api of each exchange
    def __init__(self, endpoint) -> None:
        self.endpoint = endpoint

    @abstractmethod
    def fetch_open_orders(self, symbol):
        pass

    @abstractmethod
    def place_order(self, symbol, amount, order_type, side, Price=None)->int:
        pass

    @abstractmethod
    def place_futures_order(self, symbol, amount, order_type, side, price=None)->int:
        pass

    @abstractmethod
    def fetch_ohlcv(self, symbol:str, timeframe:str, since:int)->list:
        pass

    @abstractmethod
    def fetch_last_price(self, symbol):
        pass

class BinanceBroker(Broker):
    def __init__(self, endpoint) -> None:
        super().__init__(endpoint)

    def fetch_open_orders(self, symbol):
        order_list = self.endpoint.fetch_open_orders(symbol=symbol)
        return order_list

    def place_order(self, symbol, amount, order_type, side, price=None)->int:
        if price != None:
            order = self.endpoint.create_order(symbol, order_type, side, amount, price)
        else:
            order = self.endpoint.create_order(symbol, order_type, side, amount)
        order_id = order["id"]
        return order_id


    def place_futures_order(self, symbol, amount, order_type, side, price=None)->int:
        if side == "sell":
            order = self.endpoint.create_orders([{"symbol":symbol, "type": order_type, "side": side, "amount": amount}])
        else:
            if price != None:
                order = self.endpoint.create_orders([{"symbol":symbol, "type": order_type, "side": side, "amount": amount, "price": price}])
            else:
                order = self.endpoint.create_orders([{"symbol":symbol, "type": order_type, "side": side, "amount": amount}])

        order_id = order["id"]
        return order_id

    def fetch_ohlcv(self, symbol, timeframe, since:int)->list:
        candles = self.endpoint.fetch_ohlcv(symbol="BTC/USDT", timeframe="1h", since=since)
        return candles

    def fetch_last_price(self, symbol):
        result = self.endpoint.fetch_last_prices([symbol])
        current_price = result["info"]["price"]
        return current_price

class IncubationBroker(Broker):
    def __init__(self, endpoint) -> None:
        super().__init__(endpoint)
