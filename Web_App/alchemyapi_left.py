"""Query AlchemyAPI to determine number of API calls still available"""
# -*- coding: utf-8 -*-
import json
import requests

def get_api_key():
    # Load API key (40 HEX character key) from local file
    key = open('api_key.txt').readline().strip()
    return key


def alchemy_calls_left(api_key):
    # Typical response from Alchemy:
    #{
    #    "status": "OK",
    #    "consumedDailyTransactions": "1020",
    #    "dailyTransactionLimit": "1000"
    #}
    # This URL tells us how many calls we have left in a day
    URL = "http://access.alchemyapi.com/calls/info/GetAPIKeyInfo?apikey={}&outputMode=json".format(api_key)
    # call AlchemyAPI, ask for JSON response
    response = requests.get(URL)
    calls_left = json.loads(response.content)
    return calls_left


def get_calls_left(api_key):
    """Call AlchemyAPI, report still_calls_left and details"""
    calls_left = alchemy_calls_left(api_key)
    # convert the text number fields to integers
    calls_left['consumedDailyTransactions'] = int(calls_left['consumedDailyTransactions'])
    calls_left['dailyTransactionLimit'] = int(calls_left['dailyTransactionLimit'])
    # add a convenience boolean
    calls_left['still_calls_left'] = calls_left['consumedDailyTransactions'] < calls_left['dailyTransactionLimit']
    return calls_left


if __name__ == "__main__":
    api_key = get_api_key()
    print "Using key:", api_key
    print "Calls left:", get_calls_left(api_key)
