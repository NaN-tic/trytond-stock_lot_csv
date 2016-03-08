# This file is part of stock_lot_csv module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.tests.test_tryton import ModuleTestCase
from trytond.tests.test_tryton import suite as test_suite
import unittest


class StockLotCsvTestCase(ModuleTestCase):
    'Test Stock Lot Csv module'
    module = 'stock_lot_csv'


def suite():
    suite = test_suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
            StockLotCsvTestCase))
    return suite
