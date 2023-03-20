"""
Author: Andreas Brecl
Date: 10/25/2022

This class deals with monitoring the datawriting on the hard drive of
the NUC. It can pull hard drive data then relay an output if data is
being written to the harddrive.
"""

import os.path
import time

class DiskUsageMonitor:
    def __init__(self, pathToDisk):
        """
        This initialized the variable names and the object for the 
        disk monitoring processes.

        Input:  pathToDisk <string> - Path to harddrive

        Output: None
        """
        self.pathToDisk = pathToDisk

    def isDiskWriting(self):
        """
        This function will pull the disk data then pause momentairly
        before checking if the disk has pulled data again. This will
        allow for the data usage to update and see if it has changed.

        Input:  None

        Output: None
        """
        # Pull disk information
        spaceUsedFirstPull = self.pullDiskData()

        # Sleep for half a second
        time.sleep(0.1)

        # Pull disk information
        spaceUsedSecondPull = self.pullDiskData()

        # Check if data was written
        if spaceUsedSecondPull > spaceUsedFirstPull:
            diskStatus = True
        else:
            diskStatus = False

        # Return status
        return diskStatus


    def pullDiskData(self):
        """
        This function pulls the space used on a harddrive.

        Input:  None

        Output: None
        """
        # Preallocate sizing
        fileSize = 0

        # Pull file path information
        filesInPath = os.scandir(self.pathToDisk)

        # Sort through all files
        for file in filesInPath:
            if file.is_file():
                currentSize = os.path.getsize(file)
                
                # Add to total dir size
                fileSize = fileSize + currentSize

        # Seperate variables
        spaceUsed = fileSize

        # Return space used
        return spaceUsed


