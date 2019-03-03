### Crypto Currency Trading Bot
Cryptocurrencies have become a global phenomenon in the recent times that has led to the increased trading of these digital currencies. Cryptocurrency trading is highly volatile by nature and hence offers a medium to make profit. As a part of the Statistical Prediction course, we attempted to devise an automated minute-level strategy to trade one or all of the top four cryptocurrencies namely Bitcoin (BTC), Bitcoin Cash (BCH), Litecoin (LTC) and Ethereum (ETH).
### Getting Started
#### Data Description
The data used in this project are minute-wise cryptocurrencies OHLC data along with the volumes. The cryptomarket is open 24 hours a day, seven days a week. We use date of the four major cryptocurrencies, namely BTC (Bitcoin), BCH (Bitcoin cash), ETH (Ethereum) and LTH (Litecoin).
The attributes of the data set are explained below.
1. Time denotes the instance at which the transaction occurred.
2. Open price is the first price of the stock at the beginning of the trading day.
3. Closing price is the price of last transaction of a particular stock completed during a days trading session.
4. High price is the highest intraday price of a stock in the most recent (or current) trading session.
5. Low price is the lowest intraday price of a stock in the most recent (or current) trading session.
6. Volume refers to the amount of stock that was traded during a given period.
### Prerequisites
Python 3.0 is the programming language used.
#### Libraries Required
numpy 1.14.5
pandas 0.23.4
#### Installation
Use the package manager [pip](https://pip.pypa.io/en/stable/) to install all the required libraries.
In command line
```sh
$ pip install 'libraryname' 
```
In ipython notebook
```sh
 !pip install 'libraryname' 
```
### How to run the code
We have two .py files
1. Strategy.py
2. Backtest.py
Run Backtest.py file as Strategy.py file is imported into this file. You will get a graph showing the balance curve for the particular week.
### Author
It is group project and was a part of the course 'Statistical Prediction' in MSc.Bigdata Technology, HKUST. My project group members are 
Reshika, PALANIYAPPAN VELUMANI
Pooja, RAMALINGAM
Li,LU
Yao, ZELI
