import time
from abc import ABC

import talib
import pandas as pd

from Order import Order, LimitOrder, MarketOrder
from Broker import Broker
from Accounting import Accounting
TIMEFRAME_TO_SECONDS = {"1m": 60, "3m": 180, "5m": 300, "15m": 900, "30m": 1800,
                        "1h": 3600, "2h": 7200, "4h": 14400, "6h": 21600, "8h": 28800, "12h": 43200,
                        "1d": 86400, "3d": 259200, "1w": 604800, "1mo": 2592000}

class Strategy(ABC):
    def __init__(self, broker:Broker, startup_period:int, symbols:list,
                 timeframes:list, equity:float, commission:float,
                 leverage:float, order_type:str, trading_mode:str) -> None:
        self.broker = broker
        self.accounting = Accounting(equity, commission, leverage)
        self.next_timestamp = {}
        self.order_type = order_type
        self.trading_mode = trading_mode

        # data initialization, timestamps all in ms
        # initialize timeframes of candles
        for timeframe in timeframe:
            self.accounting.candles[timeframe] = {}

        for timeframe in timeframe:
            self.next_timestamp[timeframe] = None

        # initialize ohlcv data
        current_time = time.time() * 1000 # current timestamp in ms
        for symbol in symbols:
            for timeframe in timeframes:
                dataframe = pd.DataFrame(self.broker.fetch_ohlcv(symbol, timeframe, current_time - startup_period * TIMEFRAME_TO_SECONDS[timeframe]),
                                         columns=["timestamp", "open", "high", "low", "close", "volume"])
                self.accounting.candles[timeframe][symbol] = dataframe

        # find next timestamp
        for timeframe in timeframes:
            last_timestamp = self.accounting[timeframe][symbol[0]]["timestamp"].iloc[-1]
            next_timestamp = last_timestamp + TIMEFRAME_TO_SECONDS[timeframe] * 1000
            self.next_timestamp[timeframe] = next_timestamp

    def routine(self):
        while True:
            # check if the ongoing orders are filled(if there are ongoing orders)
            if self.accounting.ongoing_orders["long"] or self.accounting.ongoing_orders["short"]:
                for order_id, order in self.accounting.ongoing_orders.items():
                    self.check_if_filled(order)

            # check if we need to update new data
            current_time = time.time() * 1000
            for timeframe, timestamp in self.next_timestamp.items():
                if current_time >= timestamp:
                    # update new next timestamp
                    timestamp += TIMEFRAME_TO_SECONDS[timeframe] * 1000

                    # update candle sticks
                    for symbol, candles in self.accounting.candles[timeframe].items():
                        new_candles = pd.DataFrame(self.broker.fetch_ohlcv(symbol, timestamp),
                                                   columns=["timestamp", "open", "high", "low", "close", "volume"])
                        candles = pd.concat([candles, new_candles])

                        # generate new indicators and entry/exit signal
                        self.generate_indicators()
                        self.generate_entry()
                        self.generate_exit()

                        # check current signals and place orders if needed
                        if self.trading_mode == "futures":
                            if candles["entry_long"] == True:
                                # place long order
                                self.place_futures_order(symbol, "long")

                            if candles["entry_short"] == True:
                                # place short order
                                self.place_futures_order(symbol, "short")

                            if candles["exit_long"] == True:
                                # close long position
                                self.close_position_symbol(symbol, "long")

                            if candles["exit_short"] == True:
                                # close short position
                                self.close_position_symbol(symbol, "short")

                        elif self.trading_mode == "spot":

                            if candles["entry_long"] == True:
                                # place long order
                                self.place_order(symbol, "long")

                            if candles["entry_short"] == True:
                                # place short order
                                self.place_order(symbol, "short")

                            if candles["exit_long"] == True:
                                # close long position
                                self.close_position_symbol(symbol, "long")

                            if candles["exit_short"] == True:
                                # close short position
                                self.close_position_symbol(symbol, "short")

            # check stop loss/profit of all positions
            for position in self.accounting.positions["long"]:
                if self.get_stop_loss(position):
                    self.close_position(position, "long")

                if self.get_stop_profit(position):
                    self.close_position(position, "long")

            for position in self.accounting.positions["short"]:
                if self.get_stop_loss(position):
                    self.close_position(position, "short")

                if self.get_stop_profit(position):
                    self.close_position(position, "short")

            # each routine sleep 5 seconds
            time.sleep(5)





    def check_if_filled(self, order: Order):
        opened_order_list = self.broker.fetch_open_orders(symbol=order.symbol)
        for order_info in opened_order_list:
            if not order.order_id == order_info["info"]["orderId"]:
                self.order_filled(order)
                break

    def order_filled(self, order:Order):
            position = {"symbol": order.symbol, "units": order.units, "bought_price": order.quote_amount, "position_type": order.comodity_type}
            self.accounting.positions["long"].append(position)
            self.accounting.deleteOngoingOrder(order.order_id)

    def close_position_symbol(self, symbol, direction):
        for position in self.accounting.positions[direction]:
            if position["symbol"] == symbol:
                if position["symbol"]["position_type"] == "spot":
                    self.broker.place_order(symbol, position["units"], order_type="market", side="sell")
                if position["symbol"]["position_type"] == "futures":
                    self.broker.place_futures_order(symbol, position["units"], order_type="market", side="sell")
                self.accounting.positions.remove(position)


    def close_position(self, position, direction):
        symbol = position["symbol"]
        units = position["units"]
        if direction == "long":
            if position["position_type"] == "spot":
                self.broker.place_order(symbol, units, "market", "sell")
            elif position["positino_type"] == "futures":
                self.broker.place_futures_order(symbol, units, "long", "market", "sell")
            self.accounting.positions["long"].remove(position)

        elif direction == "short":
            if position["position_type"] == "spot":
                self.broker.place_order(symbol, units, "market", "sell")
            elif position["positino_type"] == "futures":
                self.broker.place_futures_order(symbol, units, "short", "market", "sell")
            self.accounting.positions["short"].remove(position)

    def close_all(self):
        # close all  of the positions
        for position in self.accounting.positions["long"]:
            if position["symbol"]["position_type"] == "spot":
                self.broker.place_order(position["symbol"], position["units"], order_type="market", side="sell")
                self.accounting.positions.remove(position)
            if position["symbol"]["position_type"] == "futures":
                self.broker.place_futures_order(position["symbol"], position["units"], order_type="market", side="sell")
                self.accounting.positions.remove(position)

        for position in self.accounting.positions["short"]:
            if position["symbol"]["position_type"] == "spot":
                self.broker.place_order(position["symbol"], position["units"], order_type="market", side="sell")
                self.accounting.positions.remove(position)
            if position["symbol"]["position_type"] == "futures":
                self.broker.place_futures_order(position["symbol"], position["units"], order_type="market", side="sell")
                self.accounting.positions.remove(position)

    def place_order(self, symbol, direction):
        # place order of this one
        quote_amount = self.get_position_size() # calculate the amount that the strategy will place in usd(or any coin you want)

        if self.order_type == "limit":
            order_id = self.broker.place_order(symbol, quote_amount, self.order_type, "buy", self.broker.fetch_last_price(symbol))
        elif self.order_type == "market":
            order_id = self.broker.place_order(symbol, quote_amount, self.order_type, "buy")

        base = symbol.split("/")[0]
        units = quote_amount / self.broker.fetch_last_price(symbol)

        if self.order_type == "market":
            order = MarketOrder(order_id, symbol, base, quote_amount, units, direction, comodity_type=self.trading_mode)
        else:
            order = LimitOrder(order_id, symbol, base, quote_amount, units, direction, comodity_type=self.trading_mode)

        self.accounting.addOngoingOrder(order)
        self.accounting.euity -= quote_amount

    def place_futures_order(self, symbol, direction):
        # place order of this one
        quote_amount = self.get_position_size() # calculate the amount that the strategy will place in usd(or any coin you want)

        if self.order_type == "limit":
            order_id = self.broker.place_futures_order(symbol, quote_amount, self.order_type, "buy", self.broker.fetch_last_price(symbol))
        elif self.order_type == "market":
            order_id = self.broker.place_futures_order(symbol, quote_amount, self.order_type, "buy")

        base = symbol.split("/")[0]
        units = quote_amount / self.broker.fetch_last_price(symbol)
        if self.order_type == "market":
            order = MarketOrder(order_id, symbol, base, quote_amount, units, direction, comodity_type=self.trading_mode)
        else:
            order = LimitOrder(order_id, symbol, base, quote_amount, units, direction, comodity_type=self.trading_mode)
        self.accounting.addOngoingOrder(order)
        self.accounting.equity -= quote_amount

    def generate_entry(self):
        # your custom entry, two columns: entry_long, entry_short
        pass

    def generate_exit(self):
        # your custom exit, two columns: exit_long, exit_short
        pass

    def generate_indicators(self):
        # your custom indicators
        pass

    def get_position_size(self):
        # your custom position sizing method
        pass

    def get_stop_loss(self, position)->bool:
        # your custom stop loss
        pass

    def get_stop_profit(self, position)->bool:
        # your custom stop profit
        pass