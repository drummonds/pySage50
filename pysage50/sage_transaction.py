"""This is a slightly higher level of abstraction than SageImport.  It represents the various types of transactions
that can be in Sage.  It then allows them to be checked to see if present or written out using SageImport."""
import datetime as dt


class SageTransactionError(Exception):
    pass


class SageTransaction:
    # This should represent both the body of the invoice and enough information so that it can be
    # checked if present in Sage

    def __init__(self):
        self.tran_type = 'xx'
        self.account = 'aaa000'
        self.nominal = '0000'
        self.date = dt.datetime.now()
        self.reference = ''
        self.extra_ref = ''
        self.details = ''
        self.net_amount = 0.0
        self.tax_code = 'T999'
        self.tax_amount = 0.0
        self.exchange_rate = 1.0
        self.user_name = 'PySage50'
        self.comment = ''
        self.sage_sign = 1
        self.transaction_number = -1  # assume not in sage to start

    def write_row(self, sage_import):
        sage_import.write_row(
            self.tran_type, self.nominal, self.reference,
            self.date, self.details, self.net_amount,
            self.tax_code, self.account, self.tax_amount,
            self.exchange_rate, self.extra_ref, self.user_name,
            self.comment)

    @property
    def sage_net_amount(self):  # This may be negative or positive depending on the type of transaction.
        return self.net_amount * self.sage_sign

    def compare_field(self, sage, local, msg):
        if sage != local:
            print('CheckAuditHeader: ' + msg + ' no match, in sage {}, here {} TN({})'
                  .format(sage, local, self.transaction_number))

    def update_transaction_number(self, transaction_number):
        if hasattr(self, 'transaction_number'):
            if self.transaction_number != transaction_number:
                raise SageTransactionError('Transaction nos not equal, in Sage {}, here {}'.format(
                    transaction_number, self.transaction_number))
        else:
            self.transaction_number = transaction_number

    def check_audit_header(self, ah):
        result = False
        # Try first a simple match
        rec = ah[(ah['INV_REF'] == self.reference)
                 & (ah['DATE'] == self.date)]
        if len(rec) == 1:
            r = rec.iloc[0]
            self.update_transaction_number(r.TRAN_NUMBER)
            self.compare_field(r['ACCOUNT_REF'], self.account, 'Account ref')
            self.compare_field(r['TYPE'], self.tran_type, 'Transaction type')
            self.compare_field(r['NET_AMOUNT'], self.sage_net_amount, 'Net amount')
            result = True
        elif len(rec) == 0:
            # Try a more exact match
            rec = ah[(ah['DATE'] == self.date) &
                     (ah['ACCOUNT_REF'] == self.account) &
                     (ah['TYPE'] == self.tran_type) &
                     (ah['NET_AMOUNT'] == self.net_amount)]
            if len(rec) == 1:
                r = rec.iloc[0]
                self.update_transaction_number(r.TRAN_NUMBER)
                self.compare_field(r['INV_REF'], self.reference, 'Reference')
                result = True
            elif len(rec) == 0:
                result = False  # There is no entry in Sage
        else:
            raise SageTransactionError('CheckAuditHeader Should be 1 record in audit header but there are {}'.format(
                len(rec)))
        return result


class SageTransactionPurchaseInvoice(SageTransaction):
    # This differentiates the generic SageTransaction as a purchase invoice

    def __init__(self):
        super(SageTransactionPurchaseInvoice, self).__init__()
        self.tran_type = 'PI'
        self.sage_sign = -1


class SageTransactionPurchaseAdvance(SageTransaction):
    # This differentiates the generic SageTransaction as a purchase advance - ie the invoice has been paid

    def __init__(self):
        super(SageTransactionPurchaseAdvance, self).__init__()
        self.tran_type = 'PA'


class SagePurchaseInvoice(SageTransaction):
    # This should represent both the invoice and the payment.
    # Normally there would be a payment associate with a purchase invoice, but if this is not wanted it can
    # be set to null.

    def __init__(self):
        # TODO get rid of duplication between self.invoice and base object
        self.invoice = SageTransactionPurchaseInvoice()
        self.payment = SageTransactionPurchaseAdvance()
        # must be before inheritance as this net_amount is used in initation
        super(SagePurchaseInvoice, self).__init__()

    def check_audit_header(self, ah):
        invoice_result = self.invoice.check_audit_header(ah)
        try:
            if invoice_result:
                if not self.payment.check_audit_header(ah):
                    print('SagePurchaseInvoice: Invoice {} is ok but no payment as yet.'.format(self.invoice.reference))
                else:
                    print('SagePurchaseInvoice: Invoice {} is ok and paid.'.format(self.invoice.reference))
            else:
                print('SagePurchaseInvoice: No Invoice in Sage Audit Header')
        except AttributeError:
            # If no payment then then need to pass and just use the invoice.
            pass
        return invoice_result

    def write_row(self, sage_import):
        self.invoice.write_row(sage_import)
        try:
            self.payment.write_row(sage_import)
        except AttributeError:
            # If None then need to pass
            pass

    # TODO full set of properties so that using the main object is like the two purchase invoice and advance.
    @property
    def net_amount(self):
        try:
            if self.invoice.net_amount == self.payment.net_amount:
                return self.invoice.net_amount
            else:  # Invoice amount != payment amount so
                SageTransactionError('Invoice amount {} does not equal Paymount amount {}'.format(
                    self.invoice.net_amount, self.payment.net_amount))
        except AttributeError:
            # If Payment = None then
            return self.invoice.net_amount

    @net_amount.setter
    def net_amount(self, value):
        self.invoice.net_amount = value
        try:
            self.payment.net_amount = value
        except AttributeError:
            # If Payment = None then
            pass
