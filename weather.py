from flask import Flask
import csv
import codecs
import urllib.request
import urllib.error
import sys


app = Flask(__name__)


@app.route('/')
def get_weather():
    BaseURL = 'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/'

    ApiKey = 'YGT9KE6TRPFYAQM7YSGNW6A2T'
    UnitGroup = 'us'
    Location = 'kyiv'
    StartDate = '2020-01-01'
    EndDate = '2020-01-01'
    ContentType = "csv"
    Include = "days"
    ApiQuery = BaseURL + Location
    if (len(StartDate)):
        ApiQuery += "/" + StartDate
        if (len(EndDate)):
            ApiQuery += "/" + EndDate
    ApiQuery += "?"
    if (len(UnitGroup)):
        ApiQuery += "&unitGroup=" + UnitGroup

    if (len(ContentType)):
        ApiQuery += "&contentType=" + ContentType

    if (len(Include)):
        ApiQuery += "&include=" + Include

    ApiQuery += "&key=" + ApiKey
    print(' - Running query URL: ', ApiQuery)
    print()

    try:
        CSVBytes = urllib.request.urlopen(ApiQuery)
    except urllib.error.HTTPError as e:
        ErrorInfo = e.read().decode()
        print('Error code: ', e.code, ErrorInfo)
        sys.exit()
    except  urllib.error.URLError as e:
        ErrorInfo = e.read().decode()
        print('Error code: ', e.code, ErrorInfo)
        sys.exit()

    CSVText = csv.reader(codecs.iterdecode(CSVBytes, 'utf-8'))



    RowIndex = 0
    for Row in CSVText:
        if RowIndex == 0:
            FirstRow = Row
        else:
            print('Weather in ', Row[0], ' on ', Row[1])

            ColIndex = 0
            for Col in Row:
                if ColIndex >= 4:
                    print('   ', FirstRow[ColIndex], ' = ', Row[ColIndex])
                ColIndex += 1
        RowIndex += 1

    return CSVText


if __name__ == '__main__':
    app.run()
