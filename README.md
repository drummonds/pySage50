# pySage50
Python interface Sage Line 50 Accountancy

This is a collection of tools that I have used for helping my day to day work with Sage 50.  The
first group is a collection of tools to make it easier to generate Sage Import files.
It is currently Windows Only as there is a link to an ODBC connection.

There are two parts:
- A wrapper to create import files
- A wrapper for connection to the ODBC files.

# Sage Import files

Look in the test code to see an example.  Sage line 50 has an import system that
allows you to import a certain number of transactions.  This is an alternative to
storing data in say the saved journal entries.

## Warnings and notes
### Foreign Currencies
This does not cope with foreign currency transactions.  Some of these will be accepted
but then you will have a mess.
### Nominal codes
These are effectively string so a low nominal code is treated like this with leading
zeros:
`si.write_row('JC', '0021', 'Discount', date,'CN Discount for Ord42', value, 'T9')`


### Installing a module locally
An aide memoire for me You need a command line like this:
'pip install git+file://C:/it/majorprojects/pySage50'

# Local Setup
You need to do a couple of things to get this to work:
- Install a 32bit version of Python to work with the 32bit version of Sage ODBC
- Setup the SAGE ODBC connection as a System DSN - see below.
- Create a .env file or put in the environment your settings for the ODBC string - see .env_template as a template.

### Setting up Sage ODBC

Create a System DSN 'Slumberfleece2015' which points to \\\\SFL-SERVER-LON\2014\DataRestores\Company.001\ACCDATA

`Control Panel\Aministrative Tools\ODBC Data Sources(32bit)`

The driver should be installed SageLine50V2

###### Check

Run Sage and open Slumberfleece current.

# Roadmap

- Always use the cached data version here and split off the actual DB
component to a seperate project PySage50DB which will include the
specific version of python needed to talk to the ODBC connection.



