#!/usr/bin/env python
import time
import serial
from gpiozero import LED

RE = LED(13, active_high=False)
DE = LED(8)

rs485 = serial.Serial(
	port='/dev/ttyAMA0',
	baudrate = 9600,
	parity=serial.PARITY_NONE,
	stopbits=serial.STOPBITS_ONE,
	bytesize=serial.EIGHTBITS,
	timeout=1
)

lte = serial.Serial(
	port='/dev/ttyUSB0',
	baudrate = 115200,
	parity=serial.PARITY_NONE,
	stopbits=serial.STOPBITS_ONE,
	bytesize=serial.EIGHTBITS,
	timeout=1
)

while 1:
	RE.on()
	DE.off()
	time.sleep(1)
	rs485.flush()
	x = rs485.readline().decode('utf-8').rstrip()
	if x:
		RE.off()
		DE.on()
		time.sleep(1)
		#print(len(x))
		lte.write(str(len(x)).encode('utf-8'))
		time.sleep(1)
		#print(x)
		lte.write(x.encode('utf-8'))
		time.sleep(30)
