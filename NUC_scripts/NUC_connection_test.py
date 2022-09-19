from dronekit import connect
from pymavlink import mavutil

ip = '/dev/ttyUSB0'
# through dronekit.connect
cube_orange = connect(ip=ip, baud=115200, use_native=True)
# figure out where to put a message
print(cube_orange.gps_0)

# through mavutil
cube_orange_connection = mavutil.mavlink_connection(ip)
cube_orange_connection.mav.send('test')