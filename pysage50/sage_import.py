import datetime as dt
import os
from unipath import Path

class SageImportError(Exception):
    pass

from .sage import Sage

class SageImport:

    @staticmethod
    def today_as_string():
        now = dt.datetime.now()
        return dt.datetime.strftime(now, '%Y-%m-%d')

    def __init__(self, home_directory='', user='Auto', default_bank = '1200'):
        """this is windows based"""
        self.home_directory = home_directory
        self.user = user
        self.default_bank = default_bank
        self.date = SageImport.today_as_string()

    def check_for_transactions_on_this_day(self, tran_type, account, tran_date):
        if not hasattr(self, 'sage'):
            self.sage = Sage()
        sqldata = self.sage.sqldata
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

    # Row functions

    def write_row(self, tran_type, nominal, reference,
                  date, details, net_amount,
                  tax_code, account='', tax_amount=0.0,
                  exchange_rate=1, extra_ref='', user_name = 'PySage50', comment = ''):
        if user_name == '':
            user_name = self.user
        # Don't be tempted to put spaces after comma's. SAGE WILL REJECT IT.
        self.f.write(tran_type + ',')
        self.f.write(account + ',')
        self.f.write(nominal + ',')
        self.f.write(dt.datetime.strftime(date, '%d/%m/%Y')+',')
        self.f.write(reference + ',')
        self.f.write(details + ',')
        self.f.write('{0:.2f}'.format(net_amount) + ',')
        self.f.write(tax_code + ',')
        self.f.write('{0:.2f}'.format(tax_amount)+',') # Tax amount
        self.f.write('{0:.2f}'.format(exchange_rate)+',')
        self.f.write(extra_ref+',')
        self.f.write(user_name)
        if comment != '':
            self.f.write(','+comment)
        self.f.write('\n')

    def check_write_row(self, tran_type, nominal,reference,
                  date, details, net_amount,
                  tax_code, account='', tax_amount=0.0,
                  exchange_rate=1, extra_ref='', user_name = 'Computer', comment = ''):
        r = self.check_for_transactions_on_this_day(tran_type, nominal, date)
        if r[0]:
            #Error There are transactions when there should be none
            self.ran_ok = False
            tran_type = 'xx'+tran_type
            comment = comment + ' ' + r[2]
        else:
            comment = comment + ' :Checked '+ r[2]
        self.write_row(tran_type, nominal,reference,
                  date, details, net_amount,
                  tax_code, account=account, tax_amount=tax_amount,
                  exchange_rate=exchange_rate, extra_ref=extra_ref, user_name = user_name, comment = comment)

    def detailed_check_write_row(self, tran_type, nominal,reference,
                  date, details, net_amount,
                  tax_code, account='', tax_amount=0.0,
                  exchange_rate=1, extra_ref='', user_name = 'H3', comment = ''):
        # Detailed check where check for the exact reference and account.  This will prevent duplication
        r = self.detailed_check_for_transactions_in_the_month(tran_type, nominal, date, details)
        if r[0]:
            #Error There are transactions when there should be none
            self.ran_ok = False
            tran_type = 'xx'+tran_type
            comment = comment + ' ' + r[2]
        else:
            comment = comment + ' :Checked '+ r[2]
        self.write_row(tran_type, nominal,reference,
                  date, details, net_amount,
                  tax_code, account=account, tax_amount=tax_amount,
                  exchange_rate=exchange_rate, extra_ref=extra_ref, user_name = user_name, comment = comment)

    def start_file(self, name):
        self.filename = Path(self.home_directory).child(SageImport.today_as_string() + ' ' + name + ' Import.csv')
        if os.path.isfile(self.filename):
            raise SageImportError('File already exists.  Should probably delete and try again.  File is {}.'.
                                  format(self.filename))
        self.f = open(self.filename, 'w')
        #Write header row
        self.f.write('Type,Account Reference,Nominal A/C Ref,'
                     + 'Date,Reference,Details,'
                     + 'Net Amount,Tax Code,Tax Amount,'
                     + 'Exchange Rate,Extra Reference,User Name')
        self.f.write('\n')
        return self.filename

    def close_file(self):
        self.f.close() # you can omit in most cases as the destructor will call if


