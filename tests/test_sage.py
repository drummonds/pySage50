"""Unit tests for AIS

Aim to exercise both p and remittance docu
"""
from decimal import Decimal
from unittest import TestCase, main

from dotenv import load_dotenv, find_dotenv

from pysage50 import Sage


class SageTestCase(TestCase):

    def setUp(self):
        load_dotenv(find_dotenv())

    def test_sage_number(self):
        # Not a very good test as specific to my installation and database of sage
        sage = Sage()
        self.assertEqual('X322', sage.using_invoice_get(57735, 'Account Ref'))
        self.assertEqual(Decimal('685.70'), sage.using_invoice_get(57735, 'Net Amount'))
        self.assertEqual('X322', sage.using_invoice_get('57735', 'Account Ref'))
        self.assertEqual(Decimal('685.70'), sage.using_invoice_get('57735', 'Net Amount'))
