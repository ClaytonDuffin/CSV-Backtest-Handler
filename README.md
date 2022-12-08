# CSV-Backtest-Handler

Module for processing and visualizing the performance of one or more backtests stored in CSV format.

Useful for quickly dealing with variable-length data, which is an inevitable part of the backtesting process. Also streamlines visualization, since the tool can be used to cycle through and quickly visualize any number of backtests stored in CSV format.

Assumes that returns have already been computed only for the CSV file containing the backtest data. The CSV file containing the underlying data is intended to be left alone in OHLCV format, and must include dates to run properly. There are two sample files posted in the repository so that you can see how the data should be fed into the program. There are also two output charts posted that show the end result(s).
