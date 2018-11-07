#!/usr/bin/python
#-*- coding:UTF-8 -*-
import os
import sys
import commands
#create a user on agent machine
class init_agent():
	def __init_(self,user,passwd)
		self.user = user
		self.passwd = passwd
		
	def create_user(self):
		is_exist = commands.getstatusoutput('id %s'%self.user)
		try:
			if is_exist[0] != 0:
				os.system('useradd %s'%(self.user))
				os.system(' echo %s | passwd --stdin %s &> /dev/null'%(self.passwd,self.user))
		else:
			print('user is already exist!')
		except Exception as e:
			print('create user failed,cause %s'%e)
			sys.exit(1)
		print('create uesr %s successfully!'%(self.user))
	#generate rsa key for user
	def create_rsa(self):
		try:
			os.system('''su %s -c "ssh-keygen -t rsa -P '' -f /home/%s/.ssh/id_rsa" &>/dev/null'''%(self.user,self.user))
		except Exception as e:
			print('@DEBUG %s'%e)
			sys.exit(2)
		print('craete ras key successfully!')
	#package directory
	def packet(self):
		CP = '/usr/bin/cp'
		os.chdir('leicl')
		os.system('%s /home/%s/.ssh/id_rsa.pub ./'%(CP,self.user))
		os.system('cd .. && tar zcf leicl.tar.gz leicl/*')
	
	def run(self):
		self.create_user()
		self.create_rsa()
		self.package()


