"""Unit tests for AIS

Aim to exercise both p and remittance docu
"""
from decimal import Decimal
from os import remove, path
from unittest import TestCase, main

from dotenv import load_dotenv, find_dotenv

from pysage50 import Sage, PySageError


class SageTestCase(TestCase):

    def setUp(self):
        load_dotenv(find_dotenv())

    def clean_up(self):
        for fn2 in ['SageODBC_check.json', 'SageODBC.json']:
            for fn in [fn2, '../' + fn2]:
                try:
                    remove(fn)
                except FileNotFoundError:
                    pass

    def invoice_assertions(self, sage):
        # Test invoices
        for fn in ['ACCOUNT_REF', 'INV_REF']:
            self.assertTrue(isinstance(sage.sqldata[fn][0], str),
                            'Type of {} should be string is {}'.format(fn,
                                                                       type(sage.sqldata[fn][0])))
        self.assertEqual('X322', sage.using_reference_get(57735, 'ALT_REF', record_type=['SI']))
        self.assertEqual(Decimal('822.84'), sage.using_reference_get(57735, 'AMOUNT', record_type=['SI']))
        self.assertEqual('X322', sage.using_reference_get('57735', 'ALT_REF', record_type=['SI']))
        self.assertEqual(Decimal('822.84'), sage.using_reference_get('57735', 'AMOUNT', record_type=['SI']))
        self.assertRaises(PySageError, sage.using_reference_get, '57735', 'AMOUNT', record_type=['SC'])
        # Test credit notes
        self.assertEqual('X1324', sage.using_reference_get(4082, 'ALT_REF', record_type=['SC']))
        self.assertEqual(Decimal('-9.90'), sage.using_reference_get('4082', 'AMOUNT', record_type=['SC']))
        self.assertRaises(PySageError, sage.using_reference_get, '4082', 'AMOUNT', record_type=['SI'])

    def test_sage_number(self):
        # Not a very good test as specific to my installation and database of sage
        self.clean_up()
        sage = Sage()
        self.invoice_assertions(sage)
        # TODO test for NET_AMOUNT or remove
        # This should work with memoized files and so should the assertions
        sage2 = Sage()
        self.invoice_assertions(sage2)
