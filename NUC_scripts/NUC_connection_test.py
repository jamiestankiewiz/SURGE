from dronekit import connect
from pymavlink import mavutil, MAVLink_message

ip = '/dev/ttyUSB0'


# through dronekit.connect
cube_orange = connect(ip=ip, baud=115200, use_native=True) # returns a Vehicle object
# figure out where to put a message
print(cube_orange.gps_0)

@cube_orange.on_message('HEARTBEAT')
def message(name: str, msg: MAVLink_message):
    print(msg)



# through mavutil
cube_orange_connection = mavutil.mavlink_connection(ip)
cube_orange_connection.mav.send('test') # something like that