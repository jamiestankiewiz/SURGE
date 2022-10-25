"""
add comments

"""

# Import mavutil
import time
from pymavlink import mavutil

class NUCSerialComms:
    def __init__(self, serialPort, serialSpeed):
        """
        
        """
    
        self.serialPort = serialPort
        self.serialSpeed = serialSpeed

    def sendMessageToCube(self):
        """
        
        """
        # Establish a connection between the NUC and Cubeorange
        self.initialize(self)

        # Determine if payload is operating correctly
        


    def initialize(self):
        """
        
        """
        # Create cube orange connection object
        cube_orange_connection = mavutil.mavlink_connection(self.serialPort, baud=self.serialSpeed)

        # Establish that a connection has occured
        cube_orange_connection.wait_heartbeat()