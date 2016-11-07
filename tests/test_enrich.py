"""Unit tests for AIS

Aim to exercise both p and remittance docu
"""
from decimal import Decimal
from os import remove, path
import pandas as pd
from unittest import TestCase, main

from dotenv import load_dotenv, find_dotenv

from pysage50 import Sage

class TestRemittanceDoc():

    def __init__(self):
        self.df = pd.DataFrame( [
            [57735, '1234', 'Invoice'],
            [999, '4552', 'Invoice'],  # AIS invoice should be ignored
            [57735, '1234', 'SomethingElse'],  # Not invoice or credit note should be ignored
            ],
            columns= ['Your Ref', 'Member Code', 'Document Type']
        )


class SageTestCase(TestCase):

    def setUp(self):
        load_dotenv(find_dotenv())

    # TODO this should invert and be a method of Remittancedoc with sage as a parameter
    def test_sage_number(self):
        # Not a very good test as specific to my installation and database of sage
        sage = Sage()
        trd = TestRemittanceDoc();
        sage.enrich_remittance_doc(trd)
        assert(trd.df['Sage_Gross_Amount'][0] ==  (trd.df['Sage_VAT_Amount'][0]
                                                   + trd.df['Sage_Net_Amount'][0]))
        assert(trd.df['Sage_Gross_Amount'][0] ==  (trd.df['Sage_VAT_Amount'][0]
                                                   + trd.df['Sage_Net_Amount'][0]))
        self.assertIsNone(trd.df['Sage_Gross_Amount'][1], 'AIS own member code so ignored')
        self.assertIsNone(trd.df['Sage_Gross_Amount'][2], 'Not an invoice so ignored')
        print(trd.df)