#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       server.py
#       
#      
#       
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.
import os
import sys
import socket
import struct
import numpy
import Image
import time
import opencv
from StringIO import StringIO
#this is important for capturing/displaying images
from opencv import highgui 
import string
import pyaudio
import wave
#import pygame
#from pygame.locals import *
import cv

MYPORT = 8123
MYGROUP_6 = 'ff08:7079:7468:6f6e:6465:6d6f:6d63:6173'
group=MYGROUP_6
MYTTL = 32 # Increase to reach other networks
PARTS=40
QUALITY=75
# This is the code for the server. It creates a socket and sends data across it using UDP protocol.
def get_image(camera):
    im = highgui.cvQueryFrame(camera)
    # Add the line below if you need it (Ubuntu 8.04+)
    #im = opencv.cvGetMat(im)
    #convert Ipl image to PIL image
    #print im
    return opencv.adaptors.Ipl2PIL(im) 
    #print z.mode
    

def split_list(alist, wanted_parts=1):
    length = len(alist)
    return [ alist[i*length // wanted_parts: (i+1)*length //wanted_parts] 
           for i in range(wanted_parts) ]

def serverfromfile(moviefile):
	try:
		cap=cv.CaptureFromFile(moviefile)
	except IOError:
		print "Wrong file specified"
	# We shall first create the socket for connecting to the multicast address.
	p = pyaudio.PyAudio()
	FORMAT = pyaudio.paInt16
	CHANNELS = 2
	RATE = 8000
	AUD_PARTS=5
	chunk = RATE/AUD_PARTS
	stream = p.open(format = FORMAT, channels = CHANNELS, rate = RATE,input = True, frames_per_buffer = chunk)
	addrinfo = socket.getaddrinfo(group, None)[0] 
	s = socket.socket(addrinfo[0], socket.SOCK_DGRAM)
	ttl_bin = struct.pack('@i', MYTTL)
	s.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_MULTICAST_HOPS, ttl_bin)
	i=0
	#print len(image)
	#for i in range(0,5):
	#		image=get_image(camera)
	#		print i
	fno=0 #frame number
	no=0
	image1=cv.QueryFrame(cap)
	image = cv.CreateImage(cv.GetSize(image1), cv.IPL_DEPTH_8U, 3)
	while True:
		#time1=time.time()
		#image1=cv.QueryFrame(cap)
		image=cv.QueryFrame(cap)
		cv.CvtColor(image1, image , cv.CV_BGR2RGB)
		im=Image.fromstring('RGB' , (640,480) , image.tostring())
		stri=StringIO()
		im.save(stri,"jpeg",quality=QUALITY)
		#im.save('a.jpg')
		data=stri.getvalue()
		size_piece = len(data)/PARTS
		total=''
		for z in range(0,PARTS-1):
			data1=data[z*size_piece:(z+1)*size_piece]				
			s.sendto('vid,'+str(fno) + ',' + str(z)  + ',' +data1 + '\0', (addrinfo[4][0], MYPORT))
			i+=1
		z=z+1
		data1=data[z*size_piece:]		
		s.sendto('vid,'+str(fno) + ',' + str(z)  + ',' +data1 + '\0', (addrinfo[4][0], MYPORT))
		fno=fno+1
		#time.sleep(1/10.0 - (time.time() - time1))

           
def server():
	camera = highgui.cvCreateCameraCapture(0)
	p = pyaudio.PyAudio()
	FORMAT = pyaudio.paInt16
	CHANNELS = 2
	RATE = 8000
	AUD_PARTS=5
	chunk = RATE/AUD_PARTS
	stream = p.open(format = FORMAT, channels = CHANNELS, rate = RATE,input = True, frames_per_buffer = chunk)
	
	# We shall first create the socket for connecting to the multicast address.
	addrinfo = socket.getaddrinfo(group, None)[0] 
	s = socket.socket(addrinfo[0], socket.SOCK_DGRAM)
	ttl_bin = struct.pack('@i', MYTTL)
	s.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_MULTICAST_HOPS, ttl_bin)
	i=0
	#print len(image)
	for i in range(0,5):
			image=get_image(camera)
			print i
	fno=0 #frame number
	while True:
		time1=time.time()
		image=get_image(camera)
		#image=Image.open('arbaz.jpg')
		stri=StringIO()
		image.save(stri,"jpeg",quality=QUALITY)
		data=stri.getvalue()
		size_piece = len(data)/PARTS
		total=''
		dataaud=stream.read(chunk)
		size_piece_aud = len(dataaud)/AUD_PARTS
		for z in range(0,PARTS-1):
			data1=data[z*size_piece:(z+1)*size_piece]				
#data=newim.read()
			s.sendto('vid,'+str(fno) + ',' + str(z)  + ',' +data1 + '\0', (addrinfo[4][0], MYPORT))
			if z%8==0:
				data2=dataaud[z/8*size_piece_aud:(z+8)/8*size_piece_aud]				
				s.sendto('aud,'+str(fno) + ',' + str(z/8)  + ',' +data2 + '\0', (addrinfo[4][0], MYPORT))
			i+=1
		#	total=total+data1
			#time.sleep(0.001)
		z=z+1
		data1=data[z*size_piece:]		
		data2=dataaud[z*size_piece_aud:]		
		s.sendto('vid,'+str(fno) + ',' + str(z)  + ',' +data1 + '\0', (addrinfo[4][0], MYPORT))
		s.sendto('aud,'+str(fno) + ',' + str(z/8)  + ',' +data2 + '\0', (addrinfo[4][0], MYPORT))
		#total=total+data1
		#f=open('senders.jpg','w')
		#f.write(total)
		time2=time.time()
		time.sleep(0.2-time2+time1)
		fno=fno+1
		
def main():
	print sys.argv
	if '-f' in sys.argv[1:]:
		if len(sys.argv)<3:
			print "File not specified"
			print "Usage: python programname.py -f <filename>"
		else:
			serverfromfile(sys.argv[2])
	else:
		server()
	return 0

if __name__ == '__main__':
	main()

