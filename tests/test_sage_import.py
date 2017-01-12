import datetime as dt
import os
from shutil import move
import unittest

from luca import p

from file_utils import remove_old_sage_import_files
from pysage50 import SageImport


class TestSageImport(unittest.TestCase):

    def test_simple_SageImport(self):
        # Todo code test code will fail if run on the end of day so file generated on one day
        # and tested on the next
        filename = ''
        try:
            date = dt.datetime.now()
            nominal_code = '4009'
            value = p(2.45)
            si = SageImport()
            try:
                filename = si.start_file('TestSage')
                # Hopefully writing nonsense so won't fail
                si.write_row('JD', si.default_bank, 'Discount', date,
                                   'CN Discount for Ord42', value, 'T9')
                si.write_row('JC', '0021', 'Discount', date,
                                   'CN Discount for Ord42', value, 'T9')
            finally:
                si.close_file()
            assert os.path.isfile(filename)
        finally:
            remove_old_sage_import_files(filename, 'TestSage Import.csv.last')

    def test_check_SageImportSuccess(self):
        filename = ''
        try:
            date = dt.datetime.now()
            nominal_code = '4009'
            value = p(2.45)
            si = SageImport()
            try:
                filename = si.start_file('TestSage2')
                # Hopefully writing nonsense so won't fail
                si.check_write_row('JD', si.default_bank, 'Discount', date,
                                   'CN Discount for Ord42', value, 'T9')
                si.check_write_row('JC', '0021', 'Discount', date,
                                   'CN Discount for Ord42', value, 'T9')
            finally:
                si.close_file()
            assert os.path.isfile(filename)
        finally:
            remove_old_sage_import_files(filename, 'TestSage2 Import.csv.last')

    def test_check_SageImportFail(self):
        # TODO
        filename = ''
        try:
            date = dt.datetime.now()
            nominal_code = '4009'
            value = p(2.45)
            si = SageImport()
            try:
                filename = si.start_file('TestSage2')
                # Hopefully writing nonsense so won't fail
                si.check_write_row('JD', si.default_bank, 'Discount', date,
                                   'CN Discount for Ord42', value, 'T9')
                si.check_write_row('JC', '0021', 'Discount', date,
                                   'CN Discount for Ord42', value, 'T9')
            finally:
                si.close_file()
            assert os.path.isfile(filename)
        finally:
            remove_old_sage_import_files(filename, 'TestSage2 Import.csv.last')
