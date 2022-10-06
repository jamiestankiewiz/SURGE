import random
import time
from pymavlink import mavutil

# Start a connection listening on a UDP port
# cube_orange_connection = mavutil.mavlink_connection('udpin:localhost:5762') # returns mavutil.mavudp object
cube_orange_connection = mavutil.mavlink_connection("/dev/ttyUSB0", baud=921600)

# Wait for the first heartbeat. This sets the system and component ID of remote system for the link.
cube_orange_connection.wait_heartbeat() # shows that the system is responding
print("Connected!")

while True:
    num = round(random.random())
    if num == 1:
            numString = str(numaster.mav.statustext_send(mavutil.mavlink.MAV_SEVERITY_ALERT,numString.encode())
    else:
            numString = str(num)
            master.mav.statustext_send(mavutil.mavlink.MAV_SEVERITY_EMERGENCY,numString.encode())
    time.sleep(1)

cube_orange_connection.close()
