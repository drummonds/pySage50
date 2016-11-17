import datetime as dt
import os
from unipath import Path

from luca import p

from .sage import Sage

class SageImportError(Exception):
    pass

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

    # Row functions
    def write_row(self, tran_type, nominal, reference,
                  date, details, net_amount,
                  tax_code, account='', tax_amount=0.0,
                  exchange_rate=1, extra_ref='', user_name = 'PySage50', comment = ''):
        if p(net_amount) == p(0) and p(tax_amount) == p(0):
            pass  # don't write out anything for zero value as not needed
        else:
            if user_name == '':
                user_name = self.user
            # Don't be tempted to put spaces after comma's. SAGE LINE 50 WILL REJECT IT.
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
        if not hasattr(self, 'sage'):
            self.sage = Sage()
        r = self.sage.check_for_transactions_on_this_day(tran_type, nominal, date)
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
        if not hasattr(self, 'sage'):
            self.sage = Sage()
        # Detailed check where check for the exact reference and account.  This will prevent duplication
        r = self.sage.detailed_check_for_transactions_in_the_month(tran_type, nominal, date, details)
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

    def write_error_row(self, message):
        """This allows error message to written out so that the user can work out how to correct the file.
        The error message means that the file is no long correct.  So none of the entries will be imported"""
        self.f.write(message)

    def start_file(self, name, check_exists=True):
        self.filename = Path(self.home_directory).child(SageImport.today_as_string() + ' ' + name + ' Import.csv')
        if os.path.isfile(self.filename):
            if check_exists:
                raise SageImportError('File already exists.  Should probably delete and try again.  File is {}.'.
                                      format(self.filename))
            else:
                os.remove(self.filename)
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


