"""
Author: Andreas Brecl
Date: 10/25/2022

This class deals with sending the serial communication to the cube orange
from the NUC. This will determine if the communication message needs to be
updated saying that the system is writing if it is not writing the data
being collected.
"""

# Import mavutil
from pymavlink import mavutil
from disk_usage_monitor import DiskUsageMonitor

class NUCSerialComms:
    def __init__(self, serialPort, serialSpeed, pathToDisk):
        """
        This initialized the variable names and the object for pymavlink.

        Input:  serialPort <int> - Port that cube orange will connect to
                serialSPeed <int> - Serial rate to write data to cube oranage

        Output: None
        """
        # Define variables
        self.serialPort = serialPort
        self.serialSpeed = serialSpeed
        self.pathToDisk = pathToDisk

        # Create cube orange connection object
        self.cubeOrangeConnection = mavutil.mavlink_connection(self.serialPort, baud=self.serialSpeed)

        # Establish that a connection has occured
        self.cubeOrangeConnection.wait_heartbeat()

        # Create disk usagage object
        self.diskUsage = DiskUsageMonitor()

    def determineMessageForCube(self):
        """
        This function will pull from the disk drive write check function
        and then determine what kind of message needs to be sent to the
        cube orange via MAVLink.

        Input:  None

        Output: None
        """
        # See if disk is writting data
        diskStatus = self.diskUsage.isWritingToDisk(self.pathToDisk)

        # Determine if payload is operating correctly NEEDS UPDATING
        if diskStatus == True:

            # Define messages
            messageType = mavutil.mavlink.MAV_SEVERITY_ALERT
            messageText = 'Disk Writing'

            # Send message to cube
            self.sendMessageToCube(messageType, messageText)

        else:
            # Define messages
            messageType = mavutil.mavlink.MAV_SEVERITY_EMERGENCY
            messageText = 'Disk NOT Writing'

            # Send message to cube
            self.sendMessageToCube(messageType, messageText)

    def sendMessageToCube(self, messageType, messageText):
        """
        This function sends the mavlink message to the cube orange.

        Input:  messageType <object> - mavlink message type
                messageText <string> - string to be sent with mavlink message

        Output: None
        """
        # Send serial communication to NUC
        self.cubeOrangeConnection.mav.statustext_send(messageType, messageText)