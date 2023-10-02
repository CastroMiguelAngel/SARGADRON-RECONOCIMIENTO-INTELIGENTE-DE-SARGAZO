from djitellopy import Tello

tello = Tello('192.168.1.71') 

tello.connect()

print(tello.get_battery())