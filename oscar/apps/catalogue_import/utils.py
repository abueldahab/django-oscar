import os
import csv
import sys
from decimal import Decimal as D

from oscar.core.loading import import_module

import_module('catalogue_import.exceptions', ['CatalogueImportException'], locals())
import_module('product.models', ['ItemClass', 'Item'], locals())
import_module('partner.models', ['Partner', 'StockRecord'], locals())


class Importer(object):
    u"""A catalogue importer object"""
    
    _flush = False
    
    def __init__(self, logger, delimiter=",", flush=False):
        self.logger = logger
        self._delimiter = delimiter
        self._flush = flush
        if flush:
            self.logger.info(" - Flushing product data before import")
    
    def handle(self, file_path=None):
        u"""Handles the actual import process"""
        if not file_path:
            raise CatalogueImportException("No file path supplied")
        
        if self._flush is True:
            self._flush_product_data()
        Validator().validate(file_path)
        self._import(file_path)
        
    def _flush_product_data(self):
        u"""Flush out product and stock models"""
        ItemClass.objects.all().delete()
        Item.objects.all().delete()
        Partner.objects.all().delete()
        StockRecord.objects.all().delete()

    def _import(self, file_path):
        u"""Imports given file"""
        stats = {'new_items': 0,
                 'updated_items': 0
                 }
        row_number = 0
        for row in csv.reader(open(file_path,'rb'), delimiter=self._delimiter, quotechar='"', escapechar='\\'):
            row_number += 1
            self._import_row(row_number, row, stats)
        msg = "\tNew items: %d\n\tUpdated items: %d" % (stats['new_items'], stats['updated_items'])
        self.logger.info(msg)
    
    def _import_row(self, row_number, row, stats):
        if len(row) != 4 and len(row) != 8:
            self.logger.error("Row number %d has an invalid number of fields, skipping..." % row_number)
            return
        item = self._create_item(*row[:4], stats=stats)
        if len(row) == 8:
            # With stock data
            self._create_stockrecord(item, *row[4:8], stats=stats)
            
    def _create_item(self, upc, title, description, item_class, stats):
        # Ignore any entries that are NULL
        if description == 'NULL':
            description = ''
        
        # Create item class and item
        item_class,_ = ItemClass.objects.get_or_create(name=item_class)
        try:
            item = Item.objects.get(upc=upc)
            stats['updated_items'] += 1
        except Item.DoesNotExist:
            item = Item()
            stats['new_items'] += 1
        item.upc = upc
        item.title = title
        item.description = description
        item.item_class = item_class
        item.save()
        return item
        
    def _create_stockrecord(self, item, partner_name, partner_sku, price_excl_tax, num_in_stock, stats):            
        # Create partner and stock record
        partner, _ = Partner.objects.get_or_create(name=partner_name)
        try:
            stock = StockRecord.objects.get(partner_sku=partner_sku)
        except StockRecord.DoesNotExist:
            stock = StockRecord()
        
        stock.product = item
        stock.partner = partner
        stock.partner_sku = partner_sku
        stock.price_excl_tax = D(price_excl_tax)
        stock.num_in_stock = num_in_stock
        stock.save()
        
        
class Validator(object):
    u"""A catalogue importer file object"""
    
    def validate(self, file_path):
        self._exists(file_path)
        self._is_file(file_path)
        self._is_readable(file_path)
    
    def _exists(self, file_path):
        u"""Check whether a file exists"""
        if not os.path.exists(file_path):
            raise CatalogueImportException("%s does not exist" % (file_path))
        
    def _is_file(self, file_path):
        u"""Check whether file is actually a file type"""
        if not os.path.isfile(file_path):
            raise CatalogueImportException("%s is not a file" % (file_path))
        
    def _is_readable(self, file_path):
        u"""Check file is readable"""
        try:
            f = open(file_path, 'r')
            f.close()
        except:
            raise CatalogueImportException("%s is not readable" % (file_path))
        
