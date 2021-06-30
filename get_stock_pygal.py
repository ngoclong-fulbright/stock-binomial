"""
Several functions to deal with stock's probability to change. Data is retrieved from Alpha Vantage API.
Author: Ngoc Long
"""
import requests, json
from math import factorial, pow
from time import sleep
import pygal

def main():
    symbol = str(input('Enter stock code from a US company:'))
    
    company_name = print_info(symbol)
    
    #outputsize = 'full' to retrieve full data, 'compact' to retrieve maximum 100
    params = {
      'apikey': '62DF5PRP7SCRS7H6',
      'function': 'TIME_SERIES_INTRADAY',
      'interval':'30min',
      'symbol': symbol,
      'adjusted': 'false', 
      'outputsize': 'compact'
    }

    api_result = requests.get('https://www.alphavantage.co/query?', params)

    api_response = api_result.json()
    
    while True:
        print('\n------------\n')
        print('What action would you like to perform?')
        print('\t1 - Choose another stock company')
        print('\t2 - View', company_name,'history data')
        print('\t3 - View', company_name,'binomial prediction graph')
        print("\t4 - Get", company_name,"desired stock price's probability")
        
        try:
            command = int(input('command = ') )
        except:
            print('\n------------\n')
            print('\nInvalid input! Please enter a number!')
            sleep(2)
            continue
        
        print('\n------------\n')
        #choose another stock
        if command == 1:
            main()
        #view history info
        elif command == 2:
            draw_historydata(api_response, company_name)
            sleep(2)
        #binomial graph
        elif command == 3:
            draw_binomial(api_response)
            sleep(2)
        #Gambler's ruin
        elif command == 4:
            gambler_stock(symbol)
            sleep(2)
        #wrong input
        else:
            print('\nInvalid command! Please enter again!')
            sleep(2)
            
def test_request(api_result, api_response):
    if api_result.status_code != 200:
        print('\nSome errors has occur! Please try again!')
        print('\n------------\n')
        sleep(2)
        main()
            
    if not bool(api_response):
        print('\nWrong stock code input! Please try again!')
        print('\n------------\n')
        sleep(2)
        main()
         
def print_info(symbol):
    params = {
      'apikey': '62DF5PRP7SCRS7H6',
      'function': 'OVERVIEW',
      'symbol': symbol
    }
    
    api_result = requests.get('https://www.alphavantage.co/query?', params)
    
    api_response = api_result.json()
    
    test_request(api_result, api_response)
    
    print('Stock from %s successfully retrieved!' % api_response['Name'])
    print('Symbol: "%s"' % api_response['Symbol'])
    print('Country:', api_response['Country'])
    print('Currency:', api_response['Currency'])
    print('Sector:', api_response['Sector'])
    print('Industry:', api_response['Industry'])
    
    return api_response['Name']

def draw_binomial(api_response):        
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

def gambler_stock(symbol):
    print('Running...\n')
    gambler_list = get_average_change(symbol)
    
    current = float(gambler_list[5])
    average_change = gambler_list[0]
    prob_up = gambler_list[6]
    
    print("***This function caculates probability for stock's price to reach a certain value based on Gambler's runin formula***")
    print('Latest open price (from %s) is: %s'
          % (gambler_list[4], current))
    print('Probability of stock going up is', round(prob_up,4))
    
    while True:
        try:
            ceil = float(input('\tInput your desired ceiling price: '))
        except:
            print('\tPlease enter a valid real number!\n')
            continue
        
        if current >= ceil:
            print('\tPlease enter a value higher than current price!\n')
            continue
        else:
            break
    
    while True:
        try:
            floor = float(input('\tInput your desired floor price: '))
        except:
            print('\tPlease enter a valid real number!\n')
            continue
        
        if current <= floor:
            print('\tPlease enter a value lower than current price!\n')
            continue
        else:
            break
    # this is the correct formula, but due to math error, we have to change
#     ceil_prob = gambler_prob(current, ceil, average_change, prob_up)
#     floor_prob = gambler_prob(current, floor, average_change, prob_up)
    
    ceil_prob = gambler_prob(current, ceil, 1, prob_up)
    floor_prob = gambler_prob(current, floor, 1, prob_up)
    
 
    print()
    print('\tCaculating completed!')
    print('Probability for stock at %s to increase to %s is: %s percent'
          % (current, ceil, round(ceil_prob,6)*100))
    print('Probability for stock at %s to drop to %s is: %s percent'
          % (current, floor, round(floor_prob,6)*100))
    
def get_average_change(symbol):
    #outputsize = 'full' to retrieve full data, 'compact' to retrieve maximum 100
    params = {
      'apikey': '62DF5PRP7SCRS7H6',
      'function': 'TIME_SERIES_INTRADAY',
      'interval':'1min',
      'symbol': symbol,
      'adjusted': 'false', 
      'outputsize': 'compact'
    }

    api_result = requests.get('https://www.alphavantage.co/query?', params)
    
    api_response = api_result.json()
    
    response_list = list(api_response['Time Series (1min)'].keys())
    total_change = 0
    count = 0
    skipped = 0
    
    for i in range(0, len(response_list)-2):
        open_value = float(api_response['Time Series (1min)'][response_list[i]]['1. open'])
        next_open_value = float(api_response['Time Series (1min)'][response_list[i+1]]['1. open'])
        
        change = abs(open_value - next_open_value)
        
        if change != 0:
            total_change += change
            count += 1
        else:
            skipped += 1
    
    if count != 0:
        average_change = total_change/count
    else:
        average_change = -1
    
    hours = round(len(response_list)/60,0)
    furthest_time = response_list[-1]
    latest_time = response_list[0]
    latest_open = api_response['Time Series (1min)'][latest_time]['1. open']
    prob_up = get_prob_up_1min(api_response)
    
    gambler_list = []
    gambler_list.extend([round(average_change,4), count, skipped,
                        furthest_time, latest_time, latest_open, prob_up])
    
    print('Stock historical data successfully retrieved!')
    print('Average change value from the latest %d hours (%d times) is: %s'
          % (hours, gambler_list[1], gambler_list[0]))
    print()
    
    return gambler_list

def get_prob_up_1min(api_response):
    count = 0
    count_up = 0
    
    for time_series in api_response['Time Series (1min)']:
        open_value = float(api_response['Time Series (1min)'][time_series]['1. open'])
        close_value = float(api_response['Time Series (1min)'][time_series]['4. close'])
        
        if open_value != close_value:
            count +=1
            if open_value > close_value:
                count_up += 1
                
    return count_up/count

def gambler_prob(current, desired, change, prob_up):
    current_units = current/change
    desired_units = desired/change
    
    gap = abs(current_units-desired_units)
    
    if prob_up == 0.5:
        result = current_units/(current_units+gap)
    else:
        if current_units < desired_units:
            p = prob_up
        else:
            p = 1 - prob_up
        
        q = 1-p
        
        try:
            result = (1-pow(q/p,gap))/(1-pow(q/p,gap+gap))
            # this is the correct formula, but due to math error, we have to change
#             result = (1-pow(q/p,current_units))/(1-pow(q/p,current_units+gap))
        except:
            result = 0
            
    return result
