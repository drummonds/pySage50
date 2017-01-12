"""Interface to Sage accounting ODBC

This provides an interface to extract data from the accounting system.

It works by extracting the data into a Pandas dataframe and then doing queries from that.

"""
import json
import numpy as np
import pandas as pd
import pyodbc
import os

from dotenv import load_dotenv, find_dotenv

from luca import p


class PySageError(Exception):
    pass


def get_default_connection_string():
    # Make sure environment variables loaded.
    try:
        try:
            # Python 2
            connection_string = os.environ['PYSAGE_CNXN'].decode('utf8')
        except AttributeError:
            # Python 3
            connection_string = os.environ['PYSAGE_CNXN']
    except KeyError:
        raise PySageError('Environment missing PYSAGE_CNXN setting. '
            + 'Check for .env file looked here ??')
    return connection_string


def get_max_transaction_in_sage(cnxn):
    sql = """
SELECT
    max(TRAN_NUMBER)
FROM
    AUDIT_JOURNAL
    """
    df = pd.read_sql(sql, cnxn)
    return int(df.iloc[0,0])

def get_dataframe_sage_odbc_query(sql, name, update_cache=False):
    """This executes a SQL query if it needs to or pulls in a json file from disk.
    The results of the SQL query are returned as a dataframe.  To decide which to do
    the maximum transaction is compared to the json file."""
    connection_string = get_default_connection_string()
    cnxn = pyodbc.connect(connection_string)
    # Get the maximum transaction number
    json_check_file_name = name + '_check.json'
    json_file_name = name + '.json'
    # Read it from file
    try:
        with open(json_check_file_name) as f:
            data = json.load(f)
        max_transaction_stored = data['max_transaction_stored']
    except (FileNotFoundError, ValueError):  # Triggered as open nonexistent file is ok but no data
        max_transaction_stored = 0
    max_transaction_in_sage = get_max_transaction_in_sage(cnxn)
    if max_transaction_stored == 0 or max_transaction_stored != max_transaction_in_sage or update_cache:
        df = pd.read_sql(sage_all_data, cnxn)
        # Read fresh data from sage
        # Update files
        df.to_json(json_file_name)
        data = {'max_transaction_stored': max_transaction_in_sage}
        with open(json_check_file_name, 'w') as f:
            json.dump(data, f)
    else:  # read memoised data
        df = pd.read_json(json_file_name)
        # Need to fix those records that are integer but normally stored as strings.  On memoization theses are
        # converted to integers so now need to be converted back to strings to be compatible
        for fn in ['ACCOUNT_REF', 'INV_REF']:
            df[fn] = df[fn].astype('str')
    return df


sage_all_data = """
SELECT
    aj.TRAN_NUMBER, aj.TYPE, aj.DATE, nl.ACCOUNT_REF, aj.ACCOUNT_REF as ALT_REF, aj.INV_REF, aj.DETAILS, AJ.TAX_CODE,
    aj.AMOUNT, aj.FOREIGN_AMOUNT, aj.BANK_FLAG, ah.DATE_BANK_RECONCILED, aj.EXTRA_REF, aj.PAID_FLAG, ah.OUTSTANDING
FROM
NOMINAL_LEDGER nl, AUDIT_HEADER ah
LEFT OUTER JOIN AUDIT_JOURNAL aj ON nl.ACCOUNT_REF = aj.NOMINAL_CODE
WHERE
aj.HEADER_NUMBER = ah.HEADER_NUMBER AND
aj.DATE > '2000-01-01' AND aj.DELETED_FLAG = 0
"""


class Singleton(type):
    instance = None

    def __call__(cls, *args, **kw):
        if not cls.instance:
            cls.instance = super(Singleton, cls).__call__(*args, **kw)
        return cls.instance


class Sage(metaclass=Singleton):
    """Interface to SAGE line 50 account system.
    """
    def  __init__(self, connection_string=''):
        """ If update_cache then make sure you keep updating from the database"""
        load_dotenv(find_dotenv())
        if connection_string == '':
            connection_string = get_default_connection_string()
        self.sqldata = get_dataframe_sage_odbc_query(sage_all_data, 'SageODBC')
        if self.sqldata['DATE'].dtype == np.object:
            self.sqldata['DATE'] = self.sqldata['DATE'].astype('datetime64')

    def update_cache(self):
        self.sqldata = get_dataframe_sage_odbc_query(sage_all_data, 'SageODBC', update_cache=True)
        if self.sqldata['DATE'].dtype == np.object:
            self.sqldata['DATE'] = self.sqldata['DATE'].astype('datetime64')


    def using_reference_get(self, i, field, numchars=30, record_type = ['SI']):
        """
                Using the invoice number we can look up the field.  The accounting database contains line entries.
                So this aggregates the line entries and returns the sum of the field if numeric.
        """
        df = self.sqldata[(self.sqldata['TYPE'].isin(record_type))
                          & (self.sqldata['ACCOUNT_REF'] == '1100')
                          & (self.sqldata['INV_REF'] == str(i))
                          ]
        if len(df) == 0:  # It is an error to look up data where there is none
            raise PySageError('No data found in Audit Header to match invoice {}'.format(i))
        elif field in ['TRAN_NUMBER']:
            return list(df[:1][field])[0]
        elif field in ['DATE', 'TYPE', 'ACCOUNT_REF', 'ALT_REF', 'INV_REF', 'TAX_CODE',
                       'BANK_FLAG', 'DATE_BANK_RECONCILED']:
            return list(df[field])[0]
        elif field in ['OUTSTANDING']:
            return p(list(df[field])[0])
        elif field in ['AMOUNT', 'FOREIGN_AMOUNT']:
            return p(df[field].sum())
        elif field == 'GROSS_AMOUNT':
            return p(df['AMOUNT'].sum())
        elif field in ['NET_AMOUNT']:
            df2 = self.sqldata[(self.sqldata['TYPE'].isin(record_type))
                              & (self.sqldata['ACCOUNT_REF'] == '2200') # Get VAT control account
                              & (self.sqldata['INV_REF']== str(i))
                              ]
            return p(df['AMOUNT'].sum() + df2['AMOUNT'].sum())
        elif field in ['TAX_AMOUNT']:
            df2 = self.sqldata[(self.sqldata['TYPE'].isin(record_type))
                               & (self.sqldata['ACCOUNT_REF'] == '2200')  # Get VAT control account
                               & (self.sqldata['INV_REF']== str(i))
                               ]
            return p(- df2['AMOUNT'].sum())
        elif field in ['TAX_RATE']:
            df2 = self.sqldata[(self.sqldata['TYPE'].isin(record_type))
                               & (self.sqldata['ACCOUNT_REF'] == '4000')  # Get net Sales amount
                               & (self.sqldata['INV_REF']== str(i))
                               ]
            return 100 * ((float(df['AMOUNT'].sum()) / float(- df2['AMOUNT'].sum())) - 1.0)
        elif field in ['DETAILS', 'EXTRA_REF']:
            return df[field].str.cat()[:numchars]
        else:
            raise PySageError('Unmatched get field {} for using_invoice_get '.format(field))

    def get_field(self, row, field):
        """ For use in a lambda
         lambda row: self.get_field(row,'This Field')
        """
        result = None
        if row['Member Code'] not in ('4552', '4424'):  # TODO Ignore enrichment for AIS discount and AIS invoices
            if row['Document Type'] in ('Invoice',):
                result = self.using_reference_get(row['Your Ref'], field, record_type=['SI'])
            if row['Document Type'] in ('Credit Note',):
                result = self.using_reference_get(row['Your Ref'], field, record_type=['SC'])
        return result

    def enrich_remittance_doc(self, remittance_doc):
        """Enrich a raw remittance document with data from Sage
        It uses getField which uses 3 predefined columns:
            'Your Ref'  is our invoice number
            'Member Code' is an AIS specfic membership code and defines some exceptions
            'Document Type' defines the type of document.  We are only enriching 'Invoice' and 'Credit Note'
        """
        def get_series(field):
            return remittance_doc.df.apply(lambda row: self.get_field(row, field), axis=1)

        remittance_doc.df['Account_Ref'] = get_series('ALT_REF')
        remittance_doc.df['Sage_Net_Amount'] = get_series('NET_AMOUNT')
        remittance_doc.df['Sage_Gross_Amount'] = get_series('GROSS_AMOUNT')
        remittance_doc.df['Sage_VAT_Amount'] = get_series('TAX_AMOUNT')
        remittance_doc.df['Sage_Tax_Rate'] = get_series('TAX_RATE') / 100
        net = remittance_doc.df['Sage_Net_Amount'].sum()
        vat = remittance_doc.df['Sage_VAT_Amount'].sum()
        gross = remittance_doc.df['Sage_Gross_Amount'].sum()
        # Check sage calculations - shouldn't be a problem.  if this is passed can then rely on two of the
        # three values to set the third.  Note due to rounding you can't calculate them except approximately unless
        # you have access to the line items.
        if ( p(net + vat) != p(gross) ):
            remittance_doc.checked = False
            raise PySageError("Internal calcs of sum in Sage don't add up. net + vat != gross,  {} + {} != {}".format(
                net, vat, gross
            ))
        # Check that gross AIS doc values match Sage gross values  TODO remove specific for local installation
        gross_sum_ex_discount = remittance_doc.df[remittance_doc.df['Member Code'] != '4552']['Sage_Gross_Amount'].sum()
        if (gross != gross_sum_ex_discount):
            remittance_doc.checked = False
            raise PySageError("Adding up total AIS invoices doesn't equal Sage sum,  {} != {}, types {}, {}".format(
                gross_sum_ex_discount, gross, type(gross_sum_ex_discount), type(gross)
            ))
        # The internal sum has already been done.  It is not until the next stage that we calculate discounts

    def check_for_transactions_in_the_month(self, journal_type, account, date):
        # c = 'Type of date {} account = {}  Type of account {} journal type = {}'.format(type(date), account,
        #     type(account), journal_type)
        # return (True, 0, c)
        # d2 = pd.to_datetime(date, format='%d/%m/%Y')
        # d2 = dt.datetime(2014,12,15)
        en = date +  pd.offsets.MonthEnd(0)
        st = en -  pd.offsets.MonthBegin(1)
        test2 = self.sqldata[self.sqldata['ACCOUNT_REF'] == int(account)]
        test1 = test2[self.sqldata['DATE'] >= st]
        test = test1[self.sqldata['DATE'] <= en]
        l = len(test)
        if l == 0:
            comment = 'Found no transactions from {} upto {} (type of start = {}).'.format(
                st.strftime('%Y-%m-%d'), en.strftime('%Y-%m-%d'), type(st), )
            return (False, 0, comment)
        else:
            tn = test[:1]
            # TODO make next a function and reuse below
            comment = 'Found {} transactions from {} upto {}. First was on {}: details {}: for {}.'.format(
                l, st.strftime('%Y-%m-%d'), en.strftime('%Y-%m-%d'),
                list(tn['DATE'])[0].strftime('%Y-%m-%d'),
                list(tn['DETAILS'])[0],
                p(list(tn['AMOUNT'])[0]),)
            return (True, 0, comment)

    def detailed_check_for_transactions_in_the_month(self, journal_type, account, date, details):
        en = date +  pd.offsets.MonthEnd(0)
        st = en -  pd.offsets.MonthBegin(1)
        test1 = self.sqldata[self.sqldata['ACCOUNT_REF'] == int(account)]
        test2 = test1[self.sqldata['DATE'] >= st]
        test3 = test2[self.sqldata['DATE'] <= en]
        test = test3[self.sqldata['DETAILS'] == details] # Exact match is ok since looking for machine duplicates
        l = len(test)
        if l == 0:
            comment = 'Found no transactions from {} upto {} (type of start = {}).'.format(
                st.strftime('%Y-%m-%d'), en.strftime('%Y-%m-%d'), type(st), )
            return (False, 0, comment)
        else:
            tn = test[:1]
            comment = 'Found {} transactions from {} upto {}. First was on {}: details {}: for {}.'.format(
                l, st.strftime('%Y-%m-%d'), en.strftime('%Y-%m-%d'),
                list(tn['DATE'])[0].strftime('%Y-%m-%d'),
                list(tn['DETAILS'])[0],
                p(list(tn['AMOUNT'])[0]),)
            return (True, 0, comment)

    def check_for_transactions_on_this_day(self, tran_type, account, tran_date):
        sqldata = self.sqldata
        test3 = sqldata[sqldata['TYPE'] == tran_type]
        test2 = test3[test3['ALT_REF'] == account]
        test = test2[test2['DATE'] == tran_date]
        l = len(test)
        if l == 0:
            comment = 'Found no transactions on {} .'.format(
                tran_date.strftime('%Y-%m-%d'), )
            return (False, 0, comment)
        else:
            tn = test[:1]
            comment = 'Found {} transactions on {}. First was on {}: details {}: for {}.'.format(
                l, tran_date.strftime('%Y-%m-%d'),
                list(tn['DATE'])[0].strftime('%Y-%m-%d'),
                list(tn['DETAILS'])[0],
                list(tn['AMOUNT'])[0],)
            return (True, 0, comment)

    def list_of_accounts_with_unmatched_receipts(self):
        """This is a list of all the account codes that have invoices paid but not matched off in Sage"""
        df = self.sqldata
        accounts_list = list(set(list(df[(df['PAID_FLAG'] == 'N') & (df['TYPE'].isin(['SA']))]['ALT_REF'])))
        accounts_list.sort()
        return accounts_list