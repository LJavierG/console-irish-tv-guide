#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""
Copyright 2015, Luis Javier Gonzalez (luis.j.glez.devel@gmail.com)

This program is licensed under the GNU GPL 3.0 license.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

import requests, getopt, sys, json, os

class IrelandTv:
	page = None
	now_url = "http://entertainment.ie/tv/whats-on-now.asp"
	mis_Canales = [ "RTE-2", "TV3", "RTE-One", "UTV-Ireland", "TG4", 
	"BBC-One", "BBC-Two", "Sky1", "Setanta-Ireland", "3e", 
	"Comedy-Central", "MTV", "Sky-News", "Sky-Living", "E4", 
	"Channel-4", "Discovery-Channel"]

	Canales = []

	CADENAS = """ THESE ARE THE CHANNELS THAT YOU CAN SELECT FOR YOUR TV:
3e                                 	Alibi                              
Animal-Planet                      	BBC-One                            
BBC-Two                            	BT-Sport-1                         
BT-Sport-2                         	BT-Sport-ESPN                      
Boomerang                          	CBBC                               
CBeebies                           	Cartoon-Network                    
Challenge-TV                       	Channel-4                          
Channel-5                          	Comedy-Central                     
Comedy-Central-Extra               	DMAX                               
Dave                               	Discovery-Channel                  
Discovery-History                  	Discovery-Home-and-Health          
Discovery-Science                  	Discovery-Shed                     
Discovery-Turbo                    	Disney-Channel                     
Drama                              	E!-Entertainment                   
E4                                 	Eden                               
Eurosport                          	Eurosport-2                        
FOX                                	Fashion-TV                         
FilmFour                           	GOLD                               
Good-Food                          	History-Channel                    
Home                               	ITV2                               
ITV3                               	ITV4                               
Investigation-Discovery            	MGM                                
MTV                                	MTV-Rocks                          
More4                              	Nat-Geo-Wild                       
National-Geographic                	Nickelodeon                        
Nicktoons                          	Pick                               
Yesterday                          	RTE-2                              
RTE-One                            	Really                             
Setanta-Ireland                    	Setanta-Sports-1                   
Sky-Arts                           	Sky-Atlantic                       
Sky-Living                         	Sky-Living-It                      
Sky-Movies-Action-and-Adventure/HD 	Sky-Movies-Comedy                  
Sky-Movies-Crime-and-Thriller/HD   	Sky-Movies-Disney                  
Sky-Movies-Drama-and-Romance       	Sky-Movies-Family                  
Sky-Movies-Greats                  	Sky-Movies-Premiere                
Sky-Movies-Sci-fi/Horror           	Sky-Movies-Select                  
Sky-Movies-Showcase                	Sky-Sports-1                       
Sky-Sports-3                       	Sky-Sports-4                       
Sky-Sports-5                       	Sky-Sports-Ashes                   
Sky1                               	Sky2                               
Syfy                               	TG4                                
TLC                                	TV3                                
TV5MONDE                           	Travel-Channel                     
Turner-Classic-Movies              	UTV                                
UTV-Ireland                        	Universal-Channel                  
VH1                                	Viva                               
Watch                              	Sky-News
"""

	def __init__(self):
		HOME = os.getenv("HOME","/usr/tmp")
		try:
			os.makedirs(HOME + "/.itv")
		except:
			pass
		try:
			f = open(HOME + "/.itv/channels.db")
			self.Canales = json.load(f)
			f.close()
			print "Channels file loaded"
		except:
			self.reconfigure()
			try:
				f = open(HOME + "/.itv/channels.db", "w")
				f.write(json.dumps(Canales))
				f.close()
			except:
				print "Error: not creating channels file"
		self.reload()

	def reload(self):
		self.page = requests.get(self.now_url)

	def clean(self, cad):
		esc = 1
		cad2 = ""
		for el in cad:
			if el == "<":
				esc = 0
			if el == "&":
				cad2 +="E"
				esc = 0
			if esc != 0:
				cad2 += el 
			if el == ">":
				esc = 1
			if el == ";":
				esc = 1
		return cad2

	def get(self, c, n="N"):
		nom = self.Canales[c-1]
		print str(c)+ ". "+nom+":"
		page = self.page.text[self.page.text.find(nom + ".htm"):]
		now = page[page.find("<strong>")+8:]
		t_now = page[page.find("<strong>")-17:page.find("<strong>")-12]
		next = now[now.find("<strong>")+8:]
		t_next = now[now.find("<strong>")-17:now.find("<strong>")-12]
		now = now[:now.find("</strong>")]
		next = next[:next.find("</strong>")]
		try:
			if t_now[0] == ">":
				t_now = t_now[1:]
			print "\t"+t_now+" "+self.clean(now)+"."
		except:
			print "\tHH:MM Unknown."
		try:
			if t_next[0] == ">":
				t_next = t_next[1:]
			if n == "N":
				print "\t"+t_next+" "+self.clean(next)+"."
		except:
			if n == "N":
				print "\tHH:MM Unknown."

	def interactive(self):
		while (1):
			opt = raw_input("Canal a mostrar [1-"+str(len(self.Canales))+",t,n,q]: ")
			if opt != "q":
				self.reload()
			arg = "N"
			if opt == "q" or opt == "quit" or opt == "Quit" or opt == "Exit":
				break
			if opt == "t" or opt == "n":
				if opt == "n":
					arg = "n"
				for i in range(len(self.Canales)):
					self.get(i+1,arg)
			else:
				try:
					self.get(int(opt))
				except:
					print "Unrecognised input, try again."

	def reconfigure(self):
		print self.CADENAS
		a = 1
		ch = raw_input("Channel on P "+str(a)+" (just <Intro> for ending): ")
		while ch != "":
			a+=1
			if self.CADENAS.find(ch)>0:
				self.Canales.append(ch)
			else:
				print "Error: not valid channel"
				a-=1
			ch = raw_input("Channel on P "+str(a)+" (just <Intro> for ending): ")

	def parse_args(self):
		opts, args = getopt.getopt(sys.argv[1:], "ic:Nr", ["interactive", "channel=", "nexts", "reconfig"])
		if opts == []:
			for i in range(len(self.Canales)):
				self.get(i+1,"n")
			exit(0)
		for o, a in opts:
			if o in ("-N","--nexts"):
				for i in range(len(self.Canales)):
					self.get(i+1,"N")
				exit(0)
			if o in ("-i ","--interactive"):	
				self.interactive()
				exit(0)
			if o in ("-c","--channel"):
				try:
					self.get(int(a))
				except:
					print "Unrecognised input, try again."
			if o in ("-r","--reconfig"):
				self.reconfigure()

itv = IrelandTv()
itv.parse_args()
