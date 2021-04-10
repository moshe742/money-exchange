from datetime import datetime as dt

from django.shortcuts import render
from django.views import View
from lxml import etree
import requests
from io import BytesIO

from exchange.forms import ExchangeForm


# Create your views here.
def parse_xml(xml_data):
    bytes_string = bytes(xml_data.strip('ï»¿'), encoding='utf-8')
    bytes_io = BytesIO(bytes_string)
    tree = etree.parse(bytes_io)
    return tree.getroot()


def get_currencies(xml_root):
    result = {}
    for currency in xml_root:
        if currency.tag == 'CURRENCY':
            d = {}
            for item in currency:
                if item.tag in ['RATE', 'UNIT']:
                    d[item.tag.lower()] = float(item.text)
                if item.tag == 'CURRENCYCODE':
                    d['currency_code'] = item.text
            result[d['currency_code']] = d
    return result


def shekel_to_foreign(rate, amount, num_of_units):
    return num_of_units * amount / rate


def foreign_to_shekel(rate, amount, num_of_units):
    return rate * amount / num_of_units


class ExchangeView(View):
    currency_codes = {
        'NIS': '00',
        'USD': '01',
        'GBP': '02',
        'JPY': '31',
        'EUR': '27',
        'AUD': '18',
        'CAD': '06',
        'DKK': '12',
        'NOK': '28',
        'ZAR': '17',
        'SEK': '03',
        'CHF': '05',
        'JOD': '69',
        'LBP': '70',
        'EGP': '79',
    }

    def get(self, request):
        form = ExchangeForm(initial={
            'from_currency': '00',
            'to_currency': '01',
            'date': dt.today().strftime('%d/%m/%Y'),
            'currency_amount': 1,
        })
        return render(request, 'exchange/index.html', context={
            'form': form,
        })

    def post(self, request):
        curr_number_to_code = {v: k for k, v in self.currency_codes.items()}
        form = ExchangeForm(request.POST)
        result = 'There was an error'
        if form.is_valid():
            url = 'http://www.boi.org.il/currency.xml'
            from_currency = curr_number_to_code[form.cleaned_data['from_currency']]
            to_currency = curr_number_to_code[form.cleaned_data['to_currency']]
            currency_amount = float(form.cleaned_data['currency_amount'])

            if from_currency == to_currency:
                return render(request, 'exchange/index.html', context={
                    'form': form,
                    'result': currency_amount
                })

            payload = {
                'rdate': form.cleaned_data['date'].strftime('%Y%m%d')
            }

            res = requests.get(url, params=payload)
            parsed_xml = parse_xml(res.text)
            currencies = get_currencies(parsed_xml)

            from_currency_rate = currencies[from_currency]['rate']
            from_currency_unit = currencies[from_currency]['unit']

            to_currency_rate = currencies[to_currency]['rate']
            to_currency_unit = currencies[to_currency]['unit']

            if from_currency == 'NIS':
                result = shekel_to_foreign(to_currency_rate, currency_amount, to_currency_unit)
            elif to_currency == 'NIS':
                result = foreign_to_shekel(from_currency_rate, currency_amount, from_currency_unit)
            else:
                converted = foreign_to_shekel(from_currency_rate, currency_amount, from_currency_unit)
                result = shekel_to_foreign(to_currency_rate, converted, to_currency_unit)

        return render(request, 'exchange/index.html', context={
            'form': form,
            'result': result
        })
