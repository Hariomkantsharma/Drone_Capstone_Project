import socket
from pymavlink import mavutil
import time
import keyboard


# RPI to drone commection 
master = mavutil.mavlink_connection('tcp:127.0.0.1:5762')
master.wait_heartbeat()
print("Heartbeat from system (system ID %u component ID %u)" % (master.target_system, master.target_component))


def set_stabilize_mode(master):
    print("STABLIZING DRONE")
    # The custom mode for STABILIZE in ArduPilot is 0
    mode = 'STABILIZE'
    mode_id = master.mode_mapping()[mode]

    # Send a SET_MODE command with the base mode and custom mode
    master.mav.set_mode_send(
        master.target_system,
        mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
        mode_id
        )
    
#arming and prearm checks
def arm_and_takeoff(target_altitude):
    """ Arms vehicle and fly to target_altitude. """

    print("Arming motors")
    master.mav.command_long_send(
        master.target_system,
        master.target_component,
        mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
        0,
        1, 0, 0, 0, 0, 0, 0)

# wait until arming confirmed (can manually check with master.motors_armed())
    print("Waiting for the vehicle to arm")
    master.motors_armed_wait()
    print('Armed!')
    

def move(direction, duration):
    """ Move the drone in a specific direction for a duration """
    # Define the velocity vector
    # velocity_x = velocity_y = velocity_z = 0
    if direction == "0":
        #forward
        print("forward")
        # velocity_x = 1
        master.mav.manual_control_send(
            master.target_system,
            -600,
            0,
            400,
            0,
            0)
    elif direction == "1":
        #backward
        print("backward")
        # velocity_x = -1
        master.mav.manual_control_send(
            master.target_system,
            600,
            0,
            450,
            0,
            0)    
    elif direction == "4":
        #left
        print("left")
        # velocity_y = 1
        master.mav.manual_control_send(
            master.target_system,
            0,
            600,
            500,
            0,
            0)
    elif direction == "5":
        #right
        print("right")
        # velocity_y = -1
        master.mav.manual_control_send(
            master.target_system,
            0,
            -600,
            500,
            0,
            0)
    elif direction == "2":
        #up
        print("up")
        # velocity_z = -1
        master.mav.manual_control_send(
            master.target_system,
            0,
            0,
            600,
            0,
            0)
    elif direction == "3":
        #down
        print("down")
        # velocity_z = 1
        master.mav.manual_control_send(
            master.target_system,
            0,
            0,
            400,
            0,
            0)

def yaw(angle, duration):
    # Send SET_POSITION_TARGET_LOCAL_NED command to request the drone to yaw
    master.mav.set_position_target_local_ned_send(
        0, master.target_system, master.target_component,
        mavutil.mavlink.MAV_FRAME_LOCAL_NED,
        0b0000111111000111,
        0, 0, 0, 0, 0, 0, 0, 0, angle, 0, 0)

    # Allow some time for the drone to yaw
    time.sleep(duration)

    # Stop yawing
    master.mav.set_position_target_local_ned_send(
        0, master.target_system, master.target_component,
        mavutil.mavlink.MAV_FRAME_LOCAL_NED,
        0b0000111111000111,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)

def stop():

    master.mav.manual_control_send(
            master.target_system,
            0,
            0,
            500,
            0,
            0)

def land():
    # Send LAND command to request the drone to land
    master.mav.command_long_send(
        master.target_system, master.target_component,
        mavutil.mavlink.MAV_CMD_NAV_LAND,
        0, 0, 0, 0, 0, 0, 0, 0)

    # Wait until the drone lands
    while True:
        # Access actual altitude from GLOBAL_POSITION_INT message
        altitude = master.recv_match(type='GLOBAL_POSITION_INT', blocking=True).alt / 1000.0
        print(" Altitude: ", altitude)
        if altitude <= 0.2:  # Land when altitude is close to ground
            print("Safe landing achieved")
            break
        time.sleep(1)

def emergency_stop():
    print("Emergency stop triggered. Stopping the drone and descending slowly...")
    stop()  # Stop the drone
    # Descend slowly
    while True:
        master.mav.set_position_target_local_ned_send(
            0, master.target_system, master.target_component,
            mavutil.mavlink.MAV_FRAME_LOCAL_NED,
            0b0000111111000111,
            0, 0, -0.1, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        time.sleep(0.1)  # Adjust descent rate as needed


set_stabilize_mode(master)
arm_and_takeoff(5)  # Arm the drone and takeoff to an altitude of 5 meters

HOST = '127.0.0.1'  # Listen on all available interfaces
PORT = 5000  # Same port number used in the client script

# Create a socket object
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the address and port
server_socket.bind((HOST, PORT))

# Listen for incoming connections
server_socket.listen()

print("Waiting for connection...")

# Accept incoming connections
client_socket, client_address = server_socket.accept()
print(f"Connection established with {client_address}")

while True:
            data = client_socket.recv(1024)
            if not data:
                print("Client disconnected")
                break
            command = data.decode('utf-8').strip()
            if command == "exit":
                break
            duration = 5  # Default duration for movement commands
            if command == "yaw_left":
                yaw(-45, duration)
            elif command == "yaw_right":
                yaw(45, duration)
            elif command == "stop":
                # stop
                print("Stop")
                stop()
            elif command == "land":
                land()
            elif command == "emergency_stop":
                emergency_stop()
            else:
                move(command, duration)



def main():
    print("THIS IS INSIDE MAIN FUNCTION")
# Define host and port to listen on
    HOST = '10.38.2.61'  # Listen on all available interfaces
    PORT = 5000  # Same port number used in the client script

# Create a socket object
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the address and port
    server_socket.bind((HOST, PORT))

# Listen for incoming connections
    server_socket.listen()

    print("Waiting for connection...")

# Accept incoming connections
    client_socket, client_address = server_socket.accept()
    print(f"Connection established with {client_address}")

#     # prearm_checks(master)

    set_stabilize_mode(master)


    emergency_stop()

if __name__ == "_main_":
    main()