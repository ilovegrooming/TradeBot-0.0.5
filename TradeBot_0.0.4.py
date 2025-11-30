# Imports
import yfinance as yf
from datetime import datetime, timedelta
import json
import tkinter as tk

# Debug

with open("tickers.json", "r") as f:
    raw = f.read()
    print("RAW FILE CONTENTS >>>")
    print(repr(raw))
    print("<<< END RAW FILE CONTENTS")
    f.seek(0)


# Basic Functions

def import_tickers():
    with open("tickers.json", "r") as f:
        data = json.load(f)
        return data

# Classes

class MarketDataFetcher:
    def __init__(self):
        pass

    def get_data(self, ticker: str, interval: str, data_type: str, start: str, end: str):
        try:
            data = yf.download(
                ticker,
                start=start,
                end=end,
                interval=interval,
                progress=False,
                auto_adjust=False
            )

            if data.empty or data_type not in data.columns:
                print(f"{ticker} - no {data_type} data in this range.")
                return None

            return data[data_type]  # pandas Series
        except:
            print(f"{ticker} Has Failed To Download This Will Be Fixed In Later Versions")
            return None


class Bot:
    def __init__(
        self,
        ticker: str,
        close_prices,
        printer=None,
        trade_range: int = 3,
        trade_take_profit: int = 3,
        trade_stop_loss: int = 1,
        indicator_period: int = 5
    ):
        self.ticker = ticker
        self.close_prices = close_prices
        self.printer = printer
        self.trade_range = trade_range
        self.take_profit = trade_take_profit
        self.stop_loss = trade_stop_loss
        self.indicator_period = indicator_period

    def log(self, text, color):
        if self.printer is not None:
            # Send both text and color to the GUI
            self.printer.print_line(text, color)
        else:
            print(text)


    def run(self):
        # Latest price
        self.latest_price = self.close_prices.iloc[-1]

        self.sma_list = self.close_prices.rolling(window=self.indicator_period).mean()
        self.latest_sma = self.sma_list.iloc[-1]

        item_latest_sma = self.latest_sma.item()
        item_latest_price = self.latest_price.item()

        # print(f"Latest Price: {item_latest_price} | Latest SMA: {item_latest_sma}") # Add back for debug

        RED = "\033[91m"
        GREEN = "\033[92m"
        WHITE = "\033[97m"
        RESET = "\033[0m"


        if item_latest_price > item_latest_sma:
            signal = "BUY"
            self.log(f"BUY | {self.ticker}", "GREEN")
        elif item_latest_price < item_latest_sma:
            signal = "SELL"
            self.log(f"SELL | {self.ticker}", "RED")
        else:
            self.log(f"An Error Occured or Price And Indicators Are The Same.", "WHITE")
            if item_latest_price == item_latest_sma:
                signal = "HOLD"
            else:
                signal = "ERROR"

        return signal



class Scanner:
    def __init__(self, tickers_list_json, days_requested, number_tickers_chosen, printer=None):
        self.tickers_list_json = tickers_list_json
        self.days_requested = days_requested
        self.number_tickers_chosen = number_tickers_chosen
        self.printer = printer

    def find_dates(self, days_ago: int):
        today_datetime = datetime.today()
        past_datetime = today_datetime - timedelta(days=days_ago)

        today = today_datetime.strftime("%Y-%m-%d")
        past = past_datetime.strftime("%Y-%m-%d")

        return today, past


    def run(self):
        selected = self.tickers_list_json[:self.number_tickers_chosen]

        # get dates
        today, past_today = self.find_dates(self.days_requested)

        # Init classes
        market_fetcher = MarketDataFetcher()

        for ticker_current in selected:
            closing_data = market_fetcher.get_data(
                ticker_current,
                "5m",
                "Close",
                past_today,
                today
            )

            if closing_data is None or closing_data.empty:
                print(f"Skipping {ticker_current} (no usable data)\n")
                continue

            bot = Bot(
                ticker=ticker_current,
                close_prices=closing_data,
                indicator_period=5,
                printer=self.printer
            )

            bot.run()

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("TradeBot MVP 0.0.4")
        self.configure(bg="#1e1e1e")

        # Title label
        label = tk.Label(self, text="TradeBot MVP", font=("Arial", 20))
        label.grid(row=0, column=0, columnspan=2, pady=20)

        # Days input
        tk.Label(self, text="Days Ago:").grid(row=1, column=0, sticky="e", pady=5)
        self.days_entry = tk.Entry(self, width=20)
        self.days_entry.grid(row=1, column=1, sticky="w", pady=5)

        # Tickers input
        tk.Label(self, text="# of Tickers:").grid(row=2, column=0, sticky="e", pady=5)
        self.tickers_entry = tk.Entry(self, width=20)
        self.tickers_entry.grid(row=2, column=1, sticky="w", pady=5)

        # Scan button
        scan_button = tk.Button(self, text="Scan Stocks", command=self.run_scan)
        scan_button.grid(row=3, column=0, columnspan=2, pady=20)

        # Console
        self.console = tk.Text(self, bg="black", fg="white")
        self.console.grid(row=4, column=0, columnspan=2, pady=20)

        # Colors
        self.console.tag_config("GREEN", foreground="lime")
        self.console.tag_config("RED", foreground="red")
        self.console.tag_config("WHITE", foreground="white")

        self.update_idletasks()

        min_w = self.winfo_width()
        min_h = self.winfo_height()
        self.minsize(min_w, min_h)

    def run_scan(self):
        days_chosen = int(self.days_entry.get())
        tickers_chosen = int(self.tickers_entry.get())

        # Use your Scanner
        market_scanner = Scanner(ALL_TICKERS, days_chosen, tickers_chosen, printer=self)
        market_scanner.run()

    def print_line(self, text, color="WHITE"):
        self.console.insert(tk.END, text + "\n", color)
        self.console.see(tk.END)




# actual script

# JSON stuff
data = import_tickers()
ALL_TICKERS = data["default_list"]

# class imports

window = MainWindow()

# Run stuff

window.mainloop()