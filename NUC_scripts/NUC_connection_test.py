from pymavlink import mavutil # use mavlink2
'''
Some useful info:
    system ID : Mission Planner
    component ID : any subsystem within our system (PX4)(1 = flight controller)
    message ID :  (note: MAVLink 2 messages have an ID > 255)
    payload : actual data
    target system ID : 255 (= Mission Planner)
    target component id =1 ( for mission planner )
    best resource: https://stackoverflow.com/questions/53394660/receiving-and-sending-mavlink-messages-using-pymavlink-library
    https://ardupilot.org/dev/docs/mavlink-basics.html
'''
print('start')
# Start a connection listening on a UDP port
cube_orange_connection = mavutil.mavlink_connection('udpin:localhost:0002') # returns mavutil.mavudp object

# change the flight
print('connected')
# Wait for the first heartbeat 
#   This sets the system and component ID of remote system for the link
cube_orange_connection.wait_heartbeat(timeout=10) # shows that the system is responding

print("Heartbeat from system (system %u component %u)" % (cube_orange_connection.target_system, cube_orange_connection.target_component))
print(type(cube_orange_connection))

# Once connected, use 'the_connection' to get and send messages
cube_orange_connection.mav.send('this is a test')
# cube_orange_connection.mav.
# cube_orange_connection.mav.write()
cube_orange_connection.close()


