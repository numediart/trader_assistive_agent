import yfinance as yf
import os

def download_market(ticker, period, interval, output=None, dir=os.path.join("FOMO", "data")):
    stock = yf.Ticker(ticker)
    history = stock.history(period=period, interval=interval)
    if output == None:
        output = "{}_{}_{}.csv".format(ticker, period, interval)
    history.to_csv(os.path.join(dir, output))
