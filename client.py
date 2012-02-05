#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       client.py
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
import Image
import time
from StringIO import StringIO
#this is important for capturing/displaying images
import string
import pygame
import pyaudio
import wave
from pygame.locals import *

MYPORT = 8123
MYGROUP_6 = 'ff08:7079:7468:6f6e:6465:6d6f:6d63:6173'
group=MYGROUP_6
MYTTL = 32 # Increase to reach other networks
PARTS=40
BUFFER_SIZE=15
LIMIT_OO=10
pygame.init()
window = pygame.display.set_mode((640,550))
pygame.display.set_caption("CS425 project - Live IPv6 Multicasting")
screen = pygame.display.get_surface()


def pause():
	
	while 1:
		events=pygame.event.get()
		for event in events:
			if event.type==QUIT:
				sys.exit(0)
			elif event.type==KEYDOWN:
				if event.key==K_r :
					return
			

def client():
	pygame.init()
	window = pygame.display.set_mode((640,550))
	pygame.display.set_caption("CS425 project - Live IPv6 Multicasting")
	screen = pygame.display.get_surface()
	x=1
	addrinfo = socket.getaddrinfo(group, None)[0]
	s = socket.socket(addrinfo[0], socket.SOCK_DGRAM)
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	s.bind(('', MYPORT))
	group_bin = socket.inet_pton(addrinfo[0], addrinfo[4][0])
    # Join group
	mreq = group_bin + struct.pack('@I', 0)
	s.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_JOIN_GROUP, mreq)
	i=0
	img=''
	image=[['']*PARTS]*BUFFER_SIZE
	current_fno=0
	oo=0	
	PyAudio = pyaudio.PyAudio
	p = PyAudio()
# open stream
	stream = p.open(format =
			   p.get_format_from_width(2),
				channels =2,
				rate = 8000,
				output = True)
	bottom_font=pygame.font.SysFont('freemono', 30, bold=True, italic=False)
	notify=bottom_font.render("Press P to pause Streaming" , 1 , (255,255,255))
	screen.blit(notify, (20,500))
	while True:
		if oo> LIMIT_OO :
			image=[['']*PARTS]*BUFFER_SIZE
			current_fno=0
			oo=0	
		events = pygame.event.get()
		for event in events:
			if event.type == QUIT :
				sys.exit(0)
			if event.type == KEYDOWN and event.key == K_p :
				notify2=bottom_font.render("Press R to Resume Streaming" , 1 , (255,255,255),(0,0,0))
				screen.blit(notify2, (20,500))
				pygame.display.update()
				pause()
				notify2=bottom_font.render("Press P to Pause Streaming   " , 1 , (255,255,255),(0,0,0))
				screen.blit(notify2, (20,500))
				pygame.display.update()
				continue
					
		rp,wp=0,0
		print 'rp set to 0'
		print 'current frame ',current_fno
		avdata=''
		while rp<PARTS:
			data, sender = s.recvfrom(33000)
			while data[-1:] == '\0': data = data[:-1] # Strip trailing \0's
			avtype,fno,position,data=data.split(',',3)
			print 'data read: fno=',fno,' position=',position , "len=" , len(data)
			if(avtype=='aud'):
				stream.write(data)
			else:
				if current_fno==0:
					current_fno=int(fno)
					rp=int(position)
					wp=40
				buffer_position = int(fno) - current_fno
				if not buffer_position<0 and buffer_position<BUFFER_SIZE:
					image[buffer_position][int(position)]=data
					print 'data written: buffer_position=',buffer_position,' position=',position
				else:
					print "The peice arrived out of its order"
					oo=oo+1
					if oo >LIMIT_OO:
						break
				if current_fno == int(fno):
					rp+=1
			#print position
		print 'exited the first loop'
		#f=open('rec'+str(fno)+'.jpg','w')
		x=''
		while wp<PARTS:
			if not image[0][wp] == '':
				x=x+image[0][wp]
			else:
				print "Piece " + str(wp) + " Not received"
			wp+=1
		print 'exited the second loop'
		#f.write(x)
		image.pop(0)
		emptyframe=['']*PARTS
		image.append(emptyframe)
		print 'deleted the first entry of buffer'
		try:
			im=Image.open(StringIO(x))
			pg_img = pygame.image.frombuffer(im.tostring(), im.size, im.mode)
			screen.blit(pg_img, (0,0))
			pygame.display.flip()
		except IOError:
			print "Frame Skipped"
		#stream.write(avdata)
		current_fno=current_fno+1
		#print x
		#time.sleep(0.05)
		
def main():	
	client()
	return 0

if __name__ == '__main__':
	main()

