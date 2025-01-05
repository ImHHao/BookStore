import dao
from app import app
import math

def stats_cart(cart):
    total_amount, total_quantity = 0, 0

    if cart != None:
        for c in cart.values():
            total_quantity += c['quantity']
            total_amount += c['quantity'] * c['price']

    return {
        "total_amount": total_amount,
        "total_quantity": total_quantity
    }


def total_price(detailOrder):
    total = 0

    for do in detailOrder:
        total += do['quantity'] * do['price']

    return total
