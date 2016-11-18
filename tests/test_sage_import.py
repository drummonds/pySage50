import datetime as dt
import os
from shutil import move
import unittest

from luca import p


from pysage50 import SageImport


class TestSageImport(unittest.TestCase):

    def cleanup(self, filename, filename_end):
        rootDir = '.'
        for dirName, subdirList, fileList in os.walk(rootDir):
            if dirName[:6].lower() != r".\.git":
                print('Found directory: %s' % dirName)
                for fname in fileList:
                    if fname[:len(filename_end)].lower() == filename_end:
                        os.remove(fname)
                        print('\t%s' % fname)
        saved_copy = filename + '.last'
        if os.path.isfile(saved_copy):  # Get rid of all old save copy
            os.remove(saved_copy)
        if os.path.isfile(filename):  # Copy the old file so that can inspect after test are run
            move(filename, saved_copy)

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
            self.cleanup(filename, 'TestSage Import.csv.last')

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
            self.cleanup(filename, 'TestSage2 Import.csv.last')

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
            self.cleanup(filename, 'TestSage2 Import.csv.last')
