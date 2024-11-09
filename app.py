from flask import Flask, render_template, request
import requests
import pygal
import csv
from datetime import datetime

app = Flask(__name__)

API_KEY = '5JUJV1WUJIBMM95'  # Replace with your actual Alpha Vantage API key

timeSeries = {
    "Intraday": "TIME_SERIES_INTRADAY",
    "Daily": "TIME_SERIES_DAILY",
    "Weekly": "TIME_SERIES_WEEKLY",
    "Monthly": "TIME_SERIES_MONTHLY"
}

def load_symbols():
    """Load stock symbols from CSV, extracting only the Symbol column."""
    symbols = []
    try:
        with open("stocks.csv", "r") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                symbols.append(row['Symbol'])  # Only add the symbol to the list
    except Exception as e:
        print(f"Error loading symbols from CSV: {e}")
    return symbols

@app.route("/", methods=["GET", "POST"])
def index():
    chart_svg = None
    symbols = load_symbols()  # Load symbols from CSV for dropdown

    if request.method == "POST":
        try:
            # Retrieve form data
            symbol = request.form.get("symbol")
            chart_type = request.form.get("chartType")
            time_series_function = timeSeries[request.form.get("timeSeries")]
            start_date = request.form.get("startDate")
            end_date = request.form.get("endDate")

            # Validate dates
            fDate = datetime.strptime(start_date, '%Y-%m-%d')
            lDate = datetime.strptime(end_date, '%Y-%m-%d')
            if fDate > lDate:
                return "Start date must be before end date."

            # Fetch stock data from Alpha Vantage API
            stock_data = get_stock_data(symbol, time_series_function)
            if not stock_data:
                return f"No data available for the symbol '{symbol}'."

            # Filter data by date range
            filtered_data = filter_data_by_date(stock_data, fDate, lDate)

            # Generate chart
            chart_svg = generate_chart(filtered_data, chart_type, symbol, start_date, end_date)
        
        except Exception as e:
            print(f"Error occurred: {e}")
            return "An error occurred while processing your request."

    return render_template("index.html", symbols=symbols, chartTypes=["Bar", "Line"], timeSeriesKeys=timeSeries.keys(), chart_svg=chart_svg)


def get_stock_data(symbol, time_series_function):
    """Fetch stock data from the Alpha Vantage API."""
    url = f"https://www.alphavantage.co/query?function={time_series_function}&symbol={symbol}&apikey={API_KEY}"
    response = requests.get(url)
    data = response.json()

    # Print the raw response for debugging
    print("API Response:", data)  

    # Check for errors in the response
    if "Error Message" in data:
        print(f"Error: {data['Error Message']}")
        return None
    elif not data or "Note" in data:
        print("Error: API rate limit exceeded or no data available.")
        return None

    # Parse and return the relevant data key based on the time series function
    time_series_key = {
        "TIME_SERIES_INTRADAY": "Time Series (15min)",
        "TIME_SERIES_DAILY": "Time Series (Daily)",
        "TIME_SERIES_WEEKLY": "Weekly Time Series",
        "TIME_SERIES_MONTHLY": "Monthly Time Series"
    }.get(time_series_function)

    return data.get(time_series_key, {})


def filter_data_by_date(data, start_date, end_date):
    """Filter data by date range."""
    filtered_data = {}
    for date_str, values in data.items():
        date = datetime.strptime(date_str, '%Y-%m-%d')
        if start_date <= date <= end_date:
            filtered_data[date_str] = values
    return filtered_data


def generate_chart(data, chart_type, symbol, start_date, end_date):
    """Generate a chart with Pygal."""
    if chart_type == "Bar":
        chart = pygal.Bar()
    else:
        chart = pygal.Line()
    
    dates = sorted(data.keys())
    closing_prices = [float(data[date]['4. close']) for date in dates]
    
    chart.title = f"{symbol} Stock Price ({start_date} to {end_date})"
    chart.x_labels = dates
    chart.add('Close Price', closing_prices)

    chart_file = "static/chart.svg"
    chart.render_to_file(chart_file)
    return chart_file


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
