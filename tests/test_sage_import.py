import datetime as dt
import os
from shutil import move
import unittest

from luca import p


from pysage50 import SageImport


class TestSageImport(unittest.TestCase):

    def test_simple_SageImport(self):
        # Todo code test code will fail if run on the end of day so file generated on one day
        # and tested on the next
        try:
            date = dt.datetime.now()
            nominal_code = '4009'
            value = p(2.45)
            si = SageImport()
            filename = si.start_file('TestSage')
            si.write_row('JD', si.default_bank, 'Discount', date,
                         'CN Discount for Ord42', value, 'T9')
            si.write_row('JC', '4009', 'Discount', date,
                         'CN Discount for Ord42', value, 'T9')
            si.close_file()
            assert os.path.isfile(filename)
        finally:
            saved_copy = filename +'.last'
            if os.path.isfile(saved_copy):  # Get rid of old save copy
                os.remove(saved_copy)
            if os.path.isfile(filename):  # Copy the old file so that can inspect after test are run
                move(filename, saved_copy)
