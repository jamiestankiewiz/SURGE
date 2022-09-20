from dronekit import connect
from pymavlink import mavutil

ip = '/dev/ttyUSB0'

# def message(name, msg):
#     return msg


# through dronekit.connect
cube_orange = connect(ip=ip, baud=115200, use_native=True) # returns a Vehicle object
# figure out where to put a message
print(cube_orange.gps_0)
cube_orange.add_message_listener()
@cube_orange.on_message('HEARTBEAT')
def message(name, msg):
    return msg





# through mavutil
cube_orange_connection = mavutil.mavlink_connection(ip)
cube_orange_connection.mav.send('test') # something like that