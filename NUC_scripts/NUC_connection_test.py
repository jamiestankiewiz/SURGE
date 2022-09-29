from pymavlink import mavutil # use mavlink2

'''
Some useful info:
    system ID : Mission Planner
    component ID : any subsystem within our system (PX4)(1 = flight controller)
    message ID :  (note: MAVLink 2 messages have an ID > 255)
    payload : actual data
    target system ID : 255 (= Mission Planner)
    target component id : 1 (= Mission Planner)
    best resource: https://stackoverflow.com/questions/53394660/receiving-and-sending-mavlink-messages-using-pymavlink-library
    https://ardupilot.org/dev/docs/mavlink-basics.html
'''

# Start a connection listening on a UDP port
# cube_orange_connection = mavutil.mavlink_connection('udpin:localhost:5762') # returns mavutil.mavudp object
cube_orange_connection = mavutil.mavlink_connection('com6')

# change the flight
print('connected')
# Wait for the first heartbeat. This sets the system and component ID of remote system for the link.
cube_orange_connection.wait_heartbeat(timeout=10) # shows that the system is responding
# cube_orange_connection.target_system = 255
# cube_orange_connection.target_component = 1
print("Heartbeat from system (system %u component %u)" % (cube_orange_connection.target_system, cube_orange_connection.target_component))
# MAVLink_sys_status_message()
cube_orange_connection.mav.heartbeat_send(type=mavutil.mavlink.MAV_TYPE_GENERIC,#MAV_TYPE_GENERIC,
                                          autopilot=1,
                                          base_mode=0,
                                          custom_mode=0,
                                          system_status=0) # autopilot=1 is pixhawk, 
# Once connected, use 'the_connection' to get and send messages
# cube_orange_connection.mav.send('this is a test')

if cube_orange_connection.mode_mapping():
    print(cube_orange_connection.mode_mapping())
# cube_orange_connection.mav.set_mode_send(
#     cube_orange_connection.target_system,
#     mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
#     1)


cube_orange_connection.mav.param_request_list_send(
    cube_orange_connection.target_system, cube_orange_connection.target_component
)
while True:
    # time.sleep(0.01)
    try:
        message = cube_orange_connection.recv_match(type='PARAM_VALUE', blocking=True).to_dict()
        print('name: %s\tvalue: %d' % (message['param_id'],
                                       message['param_value']))
    except Exception as error:
        print(error)
        # sys.exit(0)

    
cube_orange_connection.close()
