import os
import unittest

from dotenv import load_dotenv, find_dotenv


from pysage50 import SageImport


class TestEnv(unittest.TestCase):

    def test_env(self):
        # Check that a local .env has been set or that their is a production variable.
        env = find_dotenv()
        print(env)
        load_dotenv(env)
        try:
            # Python 2
            connection_string = os.environ['PYSAGE_CNXN'].decode('utf8')
        except AttributeError:
            # Python 3
            connection_string = os.environ['PYSAGE_CNXN']
        print(connection_string)
        assert(len(connection_string+' ') > 1)
