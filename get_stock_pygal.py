"""
Calculate the probability of a chosen stock in the next day from its historical data.
Author: Ngoc Long
"""
import requests, json
from math import factorial, pow
from time import sleep
import pygal

def main():
    symbol = str(input('Enter stock code from a US company:'))
    
    company_name = print_info(symbol)
    
    api_response = draw_binomial(symbol)
    
    while True:
        print('\nWhat action would you like to perform?')
        print('\t1 - Choose another stock company\n\t2 - View', company_name,'history data')
        
        try:
            command = int(input('command = ') )
        except:
            print('\nInvalid input! Please enter a number!')
            sleep(2)
            continue
        
        if command == 1:
            print('\n------------\n')
            main()
        elif command == 2:
            draw_historydata(api_response, company_name)
            print('\n------------\n')
            sleep(2)
        else:
            print('\nInvalid command! Please enter again!')
            sleep(2)
            
def draw_binomial(symbol):
    #outputsize = 'full' to retrieve full data, 'compact' to retrieve maximum 100
    params = {
      'apikey': '62DF5PRP7SCRS7H6',
      'function': 'TIME_SERIES_INTRADAY',
      'interval':'30min',
      'symbol': symbol,
      'adjusted': 'false', 
      'outputsize': 'full'
    }

    api_result = requests.get('https://www.alphavantage.co/query?', params)

    api_response = api_result.json()
    
    test_request(api_result, api_response)
    
    prob_list = get_prob_list(api_response)
    
    prob_up = float(prob_list[0]/prob_list[1])
    
    print('Stock historical data successfully retrieved!')
    print('\tIntervals: 30 mins\n\tFrom: %s\n\tTo: %s\n\tData points: %d\n\tData points skipped: %d\n'
          % (prob_list[4], prob_list[3], prob_list[1], prob_list[2]))
    print('Probability of stock going up is', round(prob_up,4))
    
    #n: the number of next times
    n = 100
    highest_up = draw_binomial_bar(n, prob_up)
    sleep(3)
    
    if highest_up < 45:
        print('Up times = %d/%d has the highest probability.\nTherefore, stock price has a tendency to decrease!'
              % (highest_up, n))
    elif highest_up >55:
        print('Up times = %d/%d has the highest probability.\nTherefore, stock price has a tendency to increase!'
              % (highest_up, n))
    else:
        print('Up times = %d/%d has the highest probability.\nTherefore, stock price is likely to stay the same!'
              % (highest_up, n))
    
    return api_response
    
def get_prob_list(api_response):
    count = 0
    count_up = 0
    skipped = 0
    
    for time_series in api_response['Time Series (30min)']:
        open_value = float(api_response['Time Series (30min)'][time_series]['1. open'])
        close_value = float(api_response['Time Series (30min)'][time_series]['4. close'])
        
        if open_value != close_value:
            count +=1
            if open_value > close_value:
                count_up += 1
        else:
            skipped += 1
    
    response_list = list(api_response['Time Series (30min)'].keys())
    begin = response_list[0]
    end = response_list[-1]
    
    prob_list = []
    prob_list.extend([count_up, count, skipped, begin, end])
 
    return prob_list

def draw_binomial_bar(n, p):    
    labels = [i for i in range(1,n+1)]
    
    height = []
    highest_prob = 0
    highest_up = 0
    
    for i in range (1,n+1):
        binomial_value = binomial_prob(n, i, p)
        if highest_prob < binomial_value:
            highest_prob = binomial_value
            highest_up = i
            
        height.append(binomial_value)
    
    titles = "Probability of increases in the next " + str(n) +" times chart"
    
    chart = pygal.Bar(title=titles,
                      x_title='Increase times',
                      y_title='Probability',
                      width=1280,
                      height=600,
                      show_minor_x_labels=False,
                      x_label_rotation=5,
                      x_labels_major_count=9,
                      legend_at_bottom=True
                      )
    
    chart.value_formatter = lambda x: "%.5f" % x

    chart.add("Increase times", height)
    
    chart.x_labels = labels
    

    chart.render_to_file('binomial_bar.svg')
    
    return highest_up
 
def binomial_prob(n, i, p):
    return nCr(n,i)*pow(p,i)*pow(1-p,n-i)

def nCr(n, r):
    if n < r:
        return 0
    
    f = factorial
    return int(f(n)/(f(r)*f(n-r)))

def print_info(symbol):
    params = {
      'apikey': '62DF5PRP7SCRS7H6',
      'function': 'OVERVIEW',
      'symbol': symbol
    }
    
    api_result = requests.get('https://www.alphavantage.co/query?', params)
    
    api_response = api_result.json()
    
    test_request(api_result, api_response)
    
    print('\nStock from %s successfully retrieved!' % api_response['Name'])
    print('Symbol: "%s"' % api_response['Symbol'])
    print('Country:', api_response['Country'])
    print('Currency:', api_response['Currency'])
    print('Sector:', api_response['Sector'])
    print('Industry:', api_response['Industry'])
    print()
    
    return api_response['Name']

def test_request(api_result, api_response):
    if api_result.status_code != 200:
        print('\nSome errors has occur! Please try again!')
        sleep(2)
        main()
            
    if not bool(api_response):
        print('\nWrong stock code input! Please try again!')
        sleep(2)
        main()

def draw_historydata(api_response, company_name):
    open_value = []
    close_value = []
    labels = []
    
    for time_series in sorted(api_response['Time Series (30min)']):
        open_value.append(float(api_response['Time Series (30min)'][time_series]['1. open']))
        close_value.append(float(api_response['Time Series (30min)'][time_series]['4. close']))
        labels.append(time_series)
        
    titles = company_name + " stock's historical data chart"
    
    chart = pygal.Line(title=titles,
                      x_title='Date',
                      y_title='Price ($)',
                      width=1280,
                      height=600,
                      show_minor_x_labels=False,
                      x_label_rotation=30,
                      x_labels_major_count=5,
                      legend_at_bottom=True
                      )
    
    chart.add("Opening", open_value, dots_size=2)
    chart.add("Closing", close_value, dots_size=2)
    chart.x_labels = labels

    chart.render_to_file('historical_data_chart.svg') 

main()