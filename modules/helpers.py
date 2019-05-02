"""
Helpers for the wallet server

Mainly from bismuth core code
"""


import re
from decimal import Decimal


__version__ = "0.0.2"


def quantize_two(value):
    value = Decimal(value)
    value = value.quantize(Decimal('0.00'))
    return value


def quantize_eight(value):
    value = Decimal(value)
    value = value.quantize(Decimal('0.00000000'))
    return value


def quantize_ten(value):
    value = Decimal(value)
    value = value.quantize(Decimal('0.0000000000'))
    return value


def replace_regex(string, replace):
    replaced_string = re.sub(r'^{}'.format(replace), "", string)
    return replaced_string


def fee_calculate(openfield, operation='', block=0):
    # block var will be removed after HF
    fee = Decimal("0.01") + (Decimal(len(openfield)) / Decimal("100000"))  # 0.01 dust
    if operation == "token:issue":
        fee = Decimal(fee) + Decimal("10")
    if openfield.startswith("alias="):
        fee = Decimal(fee) + Decimal("1")
    return quantize_eight(fee)


# Dup code, not pretty, but would need address module to avoid dup
def address_validate(address):
    return re.match('[abcdef0123456789]{56}', address)
