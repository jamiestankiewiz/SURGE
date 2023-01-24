"""
Auhtor: Andreas Brecl
Date: 01/23/2023

This script will test the functionality of the disk monitoring script.
This will use the pytest unit testing library to test the functionality
of each definition.

To Run tests navigate to the main folder in your terminal then type:
python -m unittest tests.disk_usage_monitor_test

"""

# Import functions
import unittest

# Import disk_usage_monitor
import lib
from lib.disk_usage_monitor import DiskUsageMonitor

class TestStringMethods(unittest.TestCase):

    def test_isDiskWriting_one(self):
        """
        This funciton will test if the disk writing function accurate checks
        if the data is being written to a harddrive. This will verify writing has
        occured.

        Input:  None

        Output: None
        """
        

    def test_isDiskWriting_two(self):
        """
        This funciton will test if the disk writing function accurate checks
        if the data is being written to a harddrive. This will verify no writing
        has occured

        Input:  None

        Output: None
        """

    def test_pullDiskData_one(self):
        """
        This function tests to see if the disk data is being pulled as an integer.
        This is currently just checks the computers C drive to see if it is avaliable.

        Input:  None

        Output: None
        """
        # Define path and create object
        pathToDisk = "C:"
        diskUsage = DiskUsageMonitor(pathToDisk)

        # Check if output is integer
        self.assertIsInstance(diskUsage.pullDiskData(), int)

if __name__ == "__main__":
    unittest.main()
