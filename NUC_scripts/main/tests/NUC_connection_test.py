"""
Auhtor: Andreas Brecl
Date: 01/23/2023

This script will test the functionality of the NUC serial comms script.
This will use the unittest unit testing library to test the functionality
of each definition.

To Run tests navigate to the main folder in your terminal then type:
python -m unittest tests.nuc_connection_test

"""

# Import functions
import unittest

# Import disk_usage_monitor
import lib
from lib.nuc_serial_comms import NUCSerialComms

class TestStringMethods(unittest.TestCase):

    def test_determineMessageForCube(self):
        """
        asdf

        Input:  None

        Output: None
        """

    def test_sendMessageToCube(self):
        """
        asdf

        Input:  None

        Output: None
        """

if __name__ == "__main__":
    unittest.main()
