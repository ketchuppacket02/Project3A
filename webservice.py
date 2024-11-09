import requests
import pygal
from datetime import datetime

API_KEY = '5JUJV1WUJIBMM95'

timeSeries = {
        "1" : "TIME_SERIES_INTRADAY",
        "2" : "TIME_SERIES_DAILY",
        "3" : "TIME_SERIES_WEEKLY",
        "4" : "TIME_SERIES_MONTHLY"
    }   
# Function to get chart type

def getChartType():
    user_input = 0
    while(True):
        print("Chart Types\n---------------------")
        print("1. Bar")
        print("2. Line")
        try: 
            user_input = input("Enter the chart type you want (1, 2): ")
            if int(user_input) == 1 or int(user_input) == 2:
                return int(user_input)
        except:
            print("Please enter a valid input - 1, 2")

# Function to get Time series
def getTimeSeriesFunction():
    
    while True:
        print("Select the Time Series of the chart you want to generate")
        print("--------------------------------------------------------")
        print("1. Intraday")
        print("2. Daily")
        print("3. Weekly")
        print("4. Monthly")
        try: 
             user_input = input("Enter time series function (1, 2, 3, 4): ")
             if int(user_input) < 1 or int(user_input) < 5:
                 return timeSeries[user_input]
        except ValueError:
            print("Please enter a valid input - 1, 2, 3, or 4")

       
    
# Function to get stock data
def getStockData(symbol, time_series_function):
    url = f"https://www.alphavantage.co/query?function={time_series_function}&symbol={symbol}&apikey={API_KEY}"
    response = requests.get(url)
    data = response.json()

    if 'Error Message' in data:
        print(f"Error: No data available for the stock symbol '{symbol}'")
        return None
    elif not data:
        print("Error: No data returned by the API.")
        return None
    
    return data

# Function to validate date
def validateDate(prompt):
    while True:
        user_input = input(prompt)
        try:
            return datetime.strptime(user_input, '%Y-%m-%d')
        except:
            print('Invalid date format. Please enter in YYYY-MM-DD format.')

# Function to plot chart
def plot_chart(chart_type, data, title):

    # Create chart type
    if chart_type == 1:
        chart = pygal.Bar()
    elif chart_type == 2:
        chart = pygal.Line()
    else:
        print("Invalid chart type")
        return
    
    # Extract data and set chart values
    dates = []
    values = []
    for date, daily_data in sorted(data.items()):
        dates.append(date)
        values.append(float(daily_data['4. close']))

    chart.title = title
    chart.x_labels = dates
    chart.add('Price', values)

    # Render chart to an svg and open in browser
    chart.render_in_browser()

    # filter for plot
def filtered(stockData, fDate, lDate):
            filData={}
            for date_str, data in stockData.items():
                if fDate <= date_str <=lDate:
                    filData[date_str] = data
        
            return filData

# Main Loop

def main():
    while True:
    
        print("Stock Data Visualizer\n---------------------------")


        # Ask user to select chart type
    
        chart_type = getChartType()

        # Ask user to select time series function

        timeSeriesFunction = getTimeSeriesFunction()


        # Ask user for date range

        begin_date = validateDate("Enter the beginning date (YYYY-MM-DD):")
        end_date = validateDate("Enter the end date (YYYY-MM-DD):")


        # Ensure end date is not before the begin date
        if end_date < begin_date:
            print("End date cannot be earlier than the start date. Please try again.")
            continue

        # Fetch stock data from Alpha Vantage
        Stock = input("Please enter the stock symbol: ").upper()
        stockData= getStockData(Stock, timeSeriesFunction)
        if stockData is None:
            print("Error: No data found")
            continue
        
        if timeSeriesFunction == "TIME_SERIES_INTRADAY":
            timeSeriesKey = "Time Series (15min)"
        elif timeSeriesFunction == "TIME_SERIES_DAILY":
            timeSeriesKey = "Time Series (Daily)"
        elif timeSeriesFunction == "TIME_SERIES_WEEKLY":
            timeSeriesKey = "Weekly Time Series"
        elif timeSeriesFunction == "TIME_SERIES_MONTHLY":
            timeSeriesKey = "Monthly Time Series"
        

        if timeSeriesKey in stockData:
            stockS = stockData[timeSeriesKey]
        else:
            print(f"Error: Can not find time series data for {timeSeriesKey}")
            continue
        
        # Convert dates to strings for comparison
        fDate =begin_date.strftime('%Y-%m-%d')
        lDate = end_date.strftime('%Y-%m-%d')
        

        dataDates = filtered(stockS, fDate, lDate)
        # Plot chart based on user's choice
        plot_chart(chart_type, dataDates, f"Stock Data for {Stock}: {fDate} to {lDate}")

        # Ask if user wants to continue
        userContinue = input("Would you like to continue? (y/n)").lower()
        if userContinue != "y":
            print("Thank you and Goodbye!")
            break

if __name__ == "__main__":
    main()