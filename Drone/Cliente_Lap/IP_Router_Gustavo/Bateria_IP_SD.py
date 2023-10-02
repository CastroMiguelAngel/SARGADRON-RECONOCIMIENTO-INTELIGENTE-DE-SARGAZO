from djitellopy import Tello

tello = Tello('192.168.0.101') 

tello.connect()

print(tello.get_battery())