import time
import pygame
from pygame.locals import *
import serial

#try:
try:
  from pymavlink import mavutil
  isMavlinkInstalled = True
except:
  isMavlinkInstalled = False
HEARTBEAT_SAMPLE_TIME = 1
ORDER_SAMPLE_TIME = 0.05
  
buttons_state             = 0 # Variable to store buttons state

# Use pygame for the joystick

JOY_RECONNECT_TIME = 2 #seconds. Time to reconnect if no joystick motion
FORWARD_BACKWARD_AXIS = 2
LEFT_RIGHT_AXIS       = 3
pygame.init()
global cmd1, cmd2
cmd1 = 0
cmd2 = 0
def resetOrder():
  global cmd1, cmd2
  cmd1 = 0
  cmd2 = 0

# Read mavlink messages
if isMavlinkInstalled:
  try:
    ground_station = 'udpout:localhost:14556'
    master_forward = mavutil.mavlink_connection(ground_station, baud=57600, source_system=254) # 255 is ground station
    isConnectedToGroundStation = True
    print("Connected to ground station on ", ground_station)
  except:
    isConnectedToGroundStation = False
    print("Mavlink connection to ground station failed")
    
while True:
  last_event_time = 0
  t0 = 0
  t_last_order = 0
  while True:
      if time.time()-t0 > HEARTBEAT_SAMPLE_TIME:
        t0 = time.time()
        if isConnectedToGroundStation:
          msg = master_forward.recv_match(type='HEARTBEAT', blocking=False)
          print "Sending heartbeat"
          master_forward.mav.heartbeat_send(mavutil.mavlink.MAV_TYPE_GCS, mavutil.mavlink.MAV_AUTOPILOT_INVALID,
                                  0, 0, 0)
      if time.time()-t_last_order > ORDER_SAMPLE_TIME:
          t_last_order = time.time()
          if isConnectedToGroundStation:
            #master_forward.mav.manual_control_send(0, cmd1*1000, cmd2*1000, 0, 0, buttons_state)
     # Deals with joystick deconnection and reconnection      
      if time.time()-last_event_time > JOY_RECONNECT_TIME:
         print("No joystick event for x seconds, trying reconnection")
         last_event_time = time.time()
         resetOrder()
         pygame.quit()
         pygame.init()
         pygame.joystick.init()
         actual_nb_joysticks = pygame.joystick.get_count()
         print("Number of joystick: ", actual_nb_joysticks)
         if actual_nb_joysticks > 0:
            my_joystick = pygame.joystick.Joystick(0)
            my_joystick.init()
            nb_joysticks = actual_nb_joysticks
            print("Joystick reinit")
      
      # Deals with gamepad events 
      for event in pygame.event.get():

        last_event_time = time.time()
        # Button events
        if (event.type == JOYBUTTONDOWN) or (event.type == JOYBUTTONUP) or event.type == JOYHATMOTION:
            buttons_state = 0
            for i in range(my_joystick.get_numbuttons()):
              buttons_state +=my_joystick.get_button(i)*2**i
            for i in range(my_joystick.get_numhats()):
              buttons_state +=(my_joystick.get_hat(i)[0]==-1)*2**(my_joystick.get_numbuttons()+4*i)
              buttons_state +=(my_joystick.get_hat(i)[1]==-1)*2**(my_joystick.get_numbuttons()+4*i+1)
              buttons_state +=(my_joystick.get_hat(i)[0]== 1)*2**(my_joystick.get_numbuttons()+4*i+2)
              buttons_state +=(my_joystick.get_hat(i)[1]== 1)*2**(my_joystick.get_numbuttons()+4*i+3)
            if isConnectedToGroundStation:
              master_forward.mav.manual_control_send(0, cmd1*1000, cmd2*1000, 0, 0, buttons_state)
              print buttons_state
        # Joystick events  
        if event.type == JOYAXISMOTION:
          if event.axis == FORWARD_BACKWARD_AXIS:
            #print("power control ", event.value)
            cmd1 = event.value
          elif event.axis == LEFT_RIGHT_AXIS :
            #print("direction control ", event.value)
            cmd2 = event.value
          if isConnectedToGroundStation:
            print cmd1,cmd2
            master_forward.mav.manual_control_send(0, cmd1*1000, cmd2*1000, 0, 0, buttons_state)
        