import matplotlib.pyplot as plt
import numpy as np
import requests
import random


def get_currencies(currency_list):
    URL = 'https://www.cbr-xml-daily.ru/daily_json.js'
    response = requests.get(URL).json()
    currencies = response['Valute']
    table = [currencies[i] for i in currency_list]
    result = [[i["Nominal"], i["Value"]] for i in table]
    return result


def make_chart(currency_list):
    response = get_currencies(currency_list)

    currs = [i[1] for i in response]
    currency_names = [
        f'{response[k][0]} {v}' for k, v in enumerate(currency_list)
        ]

    N = len(currs)
    ind = np.arange(N)
    width = 0.35

    colors = tuple(
        [tuple([random.uniform(0, 1) for i in range(3)]) for i in currs]
        )
    p1 = plt.bar(ind, currs, width, color=colors)
    plt.ylabel('RUB')
    plt.title('Currency list')
    plt.xticks(ind, currency_names)
    plt.yticks(np.arange(0, max(currs), (max(currs) // 10)))

    plt.savefig('result.jpg')
    return 'result.jpg'
