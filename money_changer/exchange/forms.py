from django import forms
from django.utils.translation import gettext as _


class ExchangeForm(forms.Form):
    CURRENCIES = (
        ('00', _('New Israeli Shekel')),
        ('01', _('US Dollar')),
        ('02', _('Great Britain Pound')),
        ('31', _('Yen')),
        ('27', _('Euro')),
        ('18', _('Australian Dollar')),
        ('06', _('Canadian Dollar')),
        ('12', _('Denmark Krone')),
        ('28', _('Norwegian Krone')),
        ('17', _('South African Rand')),
        ('03', _('Swidish Krona')),
        ('05', _('Switzerland Franc')),
        ('69', _('Jordanian Dinar')),
        ('70', _('Lebanonian Pound')),
        ('79', _('Egyptian Pound'))
    )
    from_currency = forms.ChoiceField(choices=CURRENCIES)
    to_currency = forms.ChoiceField(choices=CURRENCIES)
    date = forms.DateField(input_formats=['%d/%m/%Y'])
    currency_amount = forms.FloatField(min_value=0)
