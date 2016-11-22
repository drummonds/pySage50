import unittest


from .file_utils import remove_old_sage_import_files
from luca import p
from pysage50 import SageImport, SageTransaction, SageTransactionPurchaseInvoice, SageTransactionPurchaseAdvance
from pysage50 import SagePurchaseInvoice


class TestSageTransaction(unittest.TestCase):

    def test_simple_SageTransaction(self):
        try:
            st = SageTransaction()
            si = SageImport()
            try:
                filename = si.start_file('TestSageTransaction')
                st.net_amount = 43  # If zero then not date will be output
                st.write_row(si)
            finally:
                si.close_file()
            #assert os.path.isfile(filename)
        finally:
            remove_old_sage_import_files(filename, 'TestSageTransaction Import.csv.last')


    def test_other_SageTransactions(self):
        try:
            stpi = SageTransactionPurchaseInvoice()
            stpa = SageTransactionPurchaseAdvance()
            spi = SagePurchaseInvoice()
            si = SageImport()
            try:
                filename = si.start_file('TestOtherSageTransaction')
                stpi.net_amount = 43  # If zero then not date will be output
                stpi.write_row(si)
                stpa.net_amount = 42  # If zero then not date will be output
                stpa.write_row(si)
                spi.net_amount = 41  # If zero then not date will be output
                spi.write_row(si)
            finally:
                si.close_file()
            #assert os.path.isfile(filename)
        finally:
            remove_old_sage_import_files(filename, 'TestOtherSageTransaction Import.csv.last')


    def test_SagePurchaseInvoice(self):
        spi = SagePurchaseInvoice()
        self.assertEqual(spi.net_amount, p(0), 'Default is zero')
        spi.net_amount = 42
        self.assertEqual(spi.net_amount, p(42), 'By default assign to both')
        spi.payment = None
        self.assertEqual(spi.net_amount, p(42), 'If no payment then invoice should still work')
        spi.net_amount = 43
        self.assertEqual(spi.net_amount, p(43), 'Can assign to invoice even when no payment')


