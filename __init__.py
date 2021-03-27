# This file is part of stock_lot_csv module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool
from . import stock


def register():
    Pool.register(
        stock.ImportCSVStart,
        module='stock_lot_csv', type_='model')
    Pool.register(
        stock.ImportCSV,
        module='stock_lot_csv', type_='wizard')
