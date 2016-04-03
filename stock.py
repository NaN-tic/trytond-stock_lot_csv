# This file is part of stock_lot_csv module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from io import StringIO
from csv import reader
from logging import getLogger
from trytond.pool import Pool
from trytond.tools import cursor_dict
from trytond.model import fields, ModelView
from trytond.transaction import Transaction
from trytond.wizard import Button, StateTransition, StateView, Wizard


__all__ = ['ImportCSVStart', 'ImportCSV']
logger = getLogger(__name__)


class ImportCSVStart(ModelView):
    'Import CSV start'
    __name__ = 'import.csv.start'
    archive = fields.Binary('Archive', required=True,
        help='First column: product code. Second column: number lot')
    character_encoding = fields.Selection([
            ('utf-8', 'UTF-8'),
            ('latin-1', 'Latin-1'),
            ], 'Character Encoding')
    header = fields.Boolean('Headers',
        help='Set this check box to true if CSV file has headers.')
    separator = fields.Selection([
            (',', 'Comma'),
            (';', 'Semicolon'),
            ('tab', 'Tabulator'),
            ('|', '|'),
            ], 'CSV Separator', help="Archive CSV Separator",
        required=True)
    quote = fields.Char('Quote',
        help='Character to use as quote')

    @classmethod
    def default_character_encoding(cls):
        return 'utf-8'

    @staticmethod
    def default_header():
        return True

    @staticmethod
    def default_separator():
        return ","

    @staticmethod
    def default_quote():
        return '"'


class ImportCSV(Wizard):
    'Import CSV'
    __name__ = 'import.csv'
    start = StateView('import.csv.start', 'stock_lot_csv.import_csv_start', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Import File', 'archive', 'tryton-ok', default=True),
            ])
    archive = StateTransition()

    def read_csv_file(self, archive):
        '''Read CSV data'''
        separator = self.start.separator
        if separator == "tab":
            separator = '\t'
        quote = self.start.quote

        data = StringIO(archive)
        if quote:
            rows = reader(data, delimiter=str(separator), quotechar=str(quote))
        else:
            rows = reader(data, delimiter=str(separator))
        return rows

    def transition_archive(self):
        pool = Pool()
        StockLot = pool.get('stock.lot')
        Lot = pool.get('stock.lot')
        Product = pool.get('product.product')
        cursor = Transaction().cursor

        has_header = self.start.header
        archive = self.start.archive
        data = self.read_csv_file(archive)

        lot = Lot.__table__()
        product = Product.__table__()
        cursor.execute(*lot
            .join(product, 'LEFT', condition=(lot.product == product.id))
            .select(
                product.code.as_('code'),
                lot.number.as_('lot'),
                )
            )
        lots = [(p['code'], p['lot']) for p in cursor_dict(cursor)]
        products = {p.code: p for p in Product.search([])}

        if has_header:
            next(data, None)
        to_create = []
        for row in list(data):
            if not row:
                continue
            if (row[0], row[1]) in lots:
                continue
            if row[0] in products:
                lot = StockLot()
                lot.product = products[row[0]]
                lot.number = row[1]
                to_create.append(lot)

        if to_create:
            StockLot.save(to_create)
            logger.info('Imported %s lots: %s.'
                % (len(to_create), str([l.number for l in to_create])))

        return 'end'
