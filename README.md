## Stock Binomial
This is a Python program to forecast the probability of stock markets increasing
the next time using binomial distribution.

## Method:
- Step 1: Choose 100 as the number of trials
- Step 2: Get the stock price history data of the US stock market. Limited to latest 2 days.
         Variables: open price, close price, the interval: 30mins.
         Then calculate the probability of getting success in one trial.
- Step 3: Draw the binomial distribution graph. 
         Shows the probability ofthe increases in the next 100 times.
- Step 4: Provide suggestions based onthe result of the graph.

Pygal library might not work on local compiler. Here is an online link that works: 
https://trinket.io/python3/4bc3ac4280
