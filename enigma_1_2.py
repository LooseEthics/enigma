"""Works - inverting rotors is a pain in the ass
	v1.1
		Changed wireboard storage format - single line now
		Removed Enigma.settrawgen() - redundant
		TODO: Find a way to eliminate the no-self-encryption property
			Increasing depth with more machines does not work
			Can this even be done without introducing asymmetry or 
				compromising the strength?
			Static self-reflection maybe
			Rotating reflector maybe
	
	v1.2
		Made it possible to initialize multiple machines and encrypt 
			multiple messages in a single run"""

import msvcrt as m
import os
import sys
from copy import deepcopy

def wait():
	"""Pauses the program until a keystroke is detected"""
	m.getch()

def terminate():
	"""Pauses and kills the program - for errors"""
	print("Terminating program")
	wait()
	sys.exit()


def readfile(fname):
	"""Reads a file, returns contents as string"""
	if os.path.isfile(fname)==0:
		print("Error:\nFile does not exist")
		terminate()
	filebuf=open(fname,'r')
	try:
		cont=filebuf.read()
	except:
		print("Error:\nUnable to read settings file")
		print("File may contain characters which cannot be processed")
		terminate()
	filebuf.close()
	return cont


def rand(rate=3.999999,xin=420):
	"""Pseudorandom number generator; returns number between 0 and 1; 3.6<rate<4, 0<xin<1;
		outside these constraints the output may converge or diverge to infinity"""
	if xin==420:
		xin=4-rate
	xout=rate*xin*(1-xin)
	return xout


class Enigma():
	"""The Enigma machine"""
	
	def __init__(self):
		self.settfile=self.sett_read()
		self.settraw=self.settfile.split('\n')
		self.validchars=self.validgen()
		self.validlen=len(self.validchars)
		self.rotortot=self.rotortotgen()
		self.rotorpos=self.rotorposgen()
		self.rotordic=self.rotordicgen()
		self.reflector=self.reflectorgen()
		self.wb=self.wbgen()
		self.invrotordic=self.rotorinv()
			

	def sett_read(self):
		prompt="Gib settings file name w extension\nd for default\n"
		fname=input(prompt)
		if fname=='d':
			fname="enigmasettings.txt"
		elif fname=='t':
			fname="estest.txt"
		settfile=readfile(fname)
		return settfile
	
	def validgen(self):
		"""Generates legal character string"""
		list1=self.settraw[0]+'\n'
		if list1=="\n":
			print("Error:\nNo legal characters")
			terminate()
		list2=''
		redundancy=0
		for char in list1:
			if (char in list2):
				if redundancy==0:
					print("Warning:\nRedundant characters in legal character list\n")
				redundancy=1
			else:
				list2+=char
		return list2
	
	def rotortotgen(self):
		"""Reads the total number of rotors"""
		try:
			rotortot=int(self.settraw[1])
		except:
			# Invalid characters
			print("Error:\nInvalid number of rotors")
			terminate()
		if rotortot<=0:
			print("Error:\nNumber of rotors must be greater than 0")
			terminate()
		return rotortot

	def rotorgen(self,i):
		"""Generates encryption rotor number i"""
		j=1
		rotor={}
		l1=[]
		rate=(4-(i/(10*self.rotortot+2)))
		xin=4-rate
		# Fills l1 with random numbers
		while j<=self.validlen:
			xin=rand(rate,xin)
			l1.append(xin)
			j+=1
		l2=l1[:]
		l2.sort()
		j=0
		# Assigns values to keys in rotor based on relative sizes on numbers in l1
		while j<self.validlen:
			k=0
			while k<self.validlen:
				if l2[j]==l1[k]:
					rotor[j]=k
					break
				else:
					k+=1
			j+=1
		return rotor
	
	def rotordicgen(self):
		"""Generates rotordic"""
		rotordic={}
		i=1
		while i<=self.rotortot:
			rotordic[i]=self.rotorgen(i)
			i+=1
		return rotordic
	
	def rotorposgen(self):
		"""Generates initial rotor positions"""
		i=0
		rotorpos=self.settraw[2].split(",")
		initlen=len(rotorpos)
		if rotorpos[0]=='':
			rotorpos[0]=0
		while i<self.rotortot:
			if i<initlen:
				rotorpos[i]=int(rotorpos[i])%self.validlen
			else:
				# Fills remaining slots with 0 if positions are incomplete
				if i==initlen:
					print("Warning:\nInitial rotor position not fully defined\n")
				rotorpos.append(0)
			i+=1
		return rotorpos
	
	def rotorupdate(self,pos):
		"""Increments rotor position"""
		# Starts from furthest rotor, on full revolution calls itself to increment the closest lower value rotor
		self.rotorpos[pos]=(self.rotorpos[pos]+1)%self.validlen
		if self.rotorpos[pos]==0:
			if pos!=0:
				self.rotorupdate(pos-1)
	
	def rotorinv(self):
		"""Inverts encryption rotors"""
		invrotordic={}
		for rotorno,rotor in self.rotordic.items():
			invrotordic[rotorno]={}
			for val in rotor:
				invrotordic[rotorno][rotor[val]]=val
		return invrotordic
	
	def reflectorgen(self):
		"""Generates reflector dictionary"""
		reflector={}
		i=0
		while i<self.validlen:
			reflector[i]=self.validlen-1-i
			i+=1
		return reflector
	
	def wbgen(self):
		"""Generates wireboard"""
		wb={}
		wbdump=[]	#for redundancy checking
		pbuff=self.settraw[3].split(",")
		wbtot=len(pbuff)
		i=0
		while i<wbtot:
			buff=pbuff[i].split("-")
			if len(buff)>2:
				# Multiple dashes in a single entry
				print("Error:\nSyntax error in wireboard settings")
				terminate()
			try:
				v1=int(buff[0])
				v2=int(buff[1])
			except:
				# Invalid characters
				print("Error:\nSyntax error in wireboard settings")
				terminate()
			if v1==v2:
				# Self-pairing doesn't break anything, but it makes the entry redundant
				print("Warning:\nSelf-pairing in wireboard settings\n")
			if (v1 in wbdump) or (v2 in wbdump):
				# Single char pairing with multiple others breaks the encryption
				print("Error:\nRedundancy in wireboard settings")
				terminate()
			elif v1>=self.validlen or v2>=self.validlen:
				print("Error:\nValue in wireboard too large")
				terminate()
			else:
				wb[v1]=v2
				wb[v2]=v1
				wbdump.append(v1)
				wbdump.append(v2)
				i+=1
		return wb




class EncData():
	"""Encryption data"""
	
	def __init__(self,enigma):
		self.enigma=enigma
		self.msgplain=self.msg_read()
		self.msglen=len(self.msgplain)
		self.msgnumplain=self.numconv()
		self.msgnumenc=self.encrypt()
		self.msgenc=self.invnumconv()

	def msg_read(self):
		"""Asks for file, returns contents in string form"""
		prompt="Gib plaintext file name w extension\n"
		prompt+="To revert encryption, use the ciphertext file as input\n"
		prompt+="d for default input\no for default output as input\n"
		fname=input(prompt)
		if fname=='d':
			fname="enigmaplain.txt"
		elif fname=='t':
			fname="eptest.txt"
		elif fname=='o':
			fname="enigmaout.txt"
		msg=readfile(fname)
		return msg

	def numconv(self):
		"""Converts string to int list based on validchars"""
		outp=[]
		for char in self.msgplain:
			pos=self.enigma.validchars.find(char)
			if pos!=-1:
				outp.append(pos)
			else:
				print("Error:\nPlaintext contains illegal characters")
				terminate()
		return outp

	def invnumconv(self):
		"""Converts int list to string"""
		outp=''
		for num in self.msgnumenc:
			outp+=self.enigma.validchars[num]
		return outp

	def encrypt(self):
		"""Encrypts input int list"""
		i=0
		j=1
		out=[]
		while i<self.msglen:
			char=self.msgnumplain[i]
			# First rotor pass
			while j<=self.enigma.rotortot:
				char=self.enigma.rotordic[j][(char+self.enigma.rotorpos[j-1])%(self.enigma.validlen)]
				j+=1
			# Wireboard, reflector, wireboard
			if char in self.enigma.wb.keys():
				char=self.enigma.wb[char]
			char=self.enigma.reflector[char]
			if char in self.enigma.wb.keys():
				char=self.enigma.wb[char]
			# Inverse rotor pass
			while j>1:
				j-=1
				char=(self.enigma.invrotordic[j][(char)]-self.enigma.rotorpos[j-1])%(self.enigma.validlen)
			i+=1
			self.enigma.rotorupdate(self.enigma.rotortot-1)
			out.append(char)
		return out
	
	def write(self):
		"""Asks for output file and writes out encrypted text"""
		prompt="Gib output file name w extension\n"
		prompt+="d for default\n"
		outfname=input(prompt)
		if outfname=="d":
			outfname="enigmaout.txt"
		try:
			outfile=open(outfname,'w')
			outfile.write(self.msgenc)
			outfile.close()
		except:
			print("Error:\nUnable to open file")
			terminate()

enigma=0
msg=0

while True:
	if enigma==0:
		print("Enigma machine not initialized")
	if msg==0:
		print("Plaintext not loaded")
	cmdprompt="Please submit a command\n"
	cmd=input(cmdprompt)
	if cmd=='quit' or cmd=='q':
		break
	elif cmd=="enigma" or cmd=='e':
		enigma=Enigma()
		enigmab=deepcopy(enigma)	#for rewinding back to original state
	elif cmd=="msg" or cmd=='m':
		if enigma==0:
			print("Please initialize an Enigma machine before inserting plaintext")
		else:
			msg=EncData(enigma)
			enigma=deepcopy(enigmab)
	elif cmd=='print' or cmd=='p':
		try:
			print(msg.msgenc)
		except:
			print("No ciphertext available")
	elif cmd=='write' or cmd=='w':
		try:
			msg.write()
			print("Ciphertext written to file")
		except:
			print("No ciphertext available")
	cmd=0
