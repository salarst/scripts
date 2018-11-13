#!/usr/bin/python
#-*- coding:UTF-8 -*-
import os
import sys
import paramiko
import commands
import time
#需要把id_rsa.pub和cpcmd.sh放到/tmp/leicl下，并打包成leicl.tar.gz

#传输key
clasee init_server()
	pkey = paramiko.RSAKey.from_private_key_file('/root/.ssh/id_rsa')
	def __init__(self,hostFile,local_path,user,userpasswd)
		self.hostFile = hostFile
		self.local_path = local_path
		self.remote_path = remote_path
		self.user = user
		self.userpasswd = userpasswd
		self.local_path = local_path
		self.remote_path = '/tmp/leicl.tar.gz'
	def transfer_pubkey(self):
		fd = open(self.hostFile)
		#remote_path = '/tmp/leicl.tar.gz'
		for i in fd.readlines():
			#传输入KEY
			tmp = i.split(',')
		host = tmp[0]
		#passwd = tmp[1].rstrip('\n')
			try:
				t = paramiko.Transport((host,22))
				t.connect(username='root',pkey=self.pkey)
				sftp = paramiko.SFTPClient.from_transport(t)
				sftp.put(self.local_path,self.remote_path)
			print('tranfer file successfully!')
			except Exception as e:
				print(e)
			t.close()
		fd.close()
	
	#为server建立用户并添加id_rsa.pub并执行用户配置脚本
	def initialization(self):
		fd = open(hostFile)
		jdk_url = 'http://192.168.1.137/website/software/jdk-8u11-linux-x64.tar.gz'
		os.system('echo > failedIp')
		key_path = '/home/%s/.ssh'%self.user
		for i in fd.readlines():
			tmp = i.split(',')
			host = tmp[0]
		print host
		t = paramiko.Transport((host,22))
		t.connect(username='root',pkey=self.pkey)
			ssh = paramiko.SSHClient()
		ssh._transport = t
		#建立用户
			stdin,stdout,stderr = ssh.exec_command('id %s'%(self.user))
			stdin, stdout, stderr = ssh.exec_command('id %s' % (self.user))
			if 'no such user' in stderr.read():
				try:
					stdin, stdout, stderr = ssh.exec_command('useradd %s' % (self.user))
					stdin, stdout, stderr = ssh.exec_command('echo %s | passwd --stdin %s' % (self.userpasswd,self.user))
			print('create new')
				except Exception as e:
					print('create user failed,cause %s' % e)
					sys.exit(1)
			print('create uesr %s successfully!' % (self.user))
			stdin, stdout, stderr = ssh.exec_command('cd /tmp && tar xf leicl.tar.gz')
		#修改环境变量
			stdin, stdout, stderr = ssh.exec_command('cd /tmp/leicl && bash -x cpcmd.sh %s '%(self.user))
		stdin, stdout, stderr = ssh.exec_command('/usr/bin/cp  /tmp/leicl/admin.sh /etc/profile.d/')
		#格式化磁盘
		stdin, stdout, stderr = ssh.exec_command('''fdisk -l | grep "Disk /dev"  | awk -F"GB" '{print $1}' | awk '{print $2""$3}' ''')
		time.sleep(1)
		diskinfo = stdout.read().strip().split('\n')
		for i in diskinfo:
			diskName = i.split(':')[0] 
			diskSpace = float(i.split(':')[1])
			if diskSpace >= 200:
				partition = diskName +'1'
				stdin, stdout, stderr = ssh.exec_command('mount | grep %s'%partition)
				isMount = stdout.read()
				if isMount :
					print("/data is already mounted,exit!")
					continue
				stdin, stdout, stderr = ssh.exec_command('echo -e "n\np\n1\n\n\nw\n" | fdisk %s && mkfs.xfs -f %s && mkdir /data -v'%(diskName,partition))
				outMsg = stdout.read()
				errMsg = stderr.read()
				if "created directory" in outMsg or "File exists" in errMsg :
					print("format disk successfully!")
				else:
					print errMsg
					sys.exit(1)	
				stdin, stdout, stderr = ssh.exec_command("blkid %s | awk '{print $2}' "%partition)
				UUID = stdout.read().strip('\n')
				stdin, stdout, stderr = ssh.exec_command('echo -n  %s >> /etc/fstab && echo -e "	/data 	xfs 	defaults 0 0" >> /etc/fstab'%UUID)
				stdin, stdout, stderr = ssh.exec_command('mount -a')
				print stdout.read()
				print stderr.read()
		#安装常用命令
		while True:
			stdin,stdout,sdterr=ssh.exec_command('ls /home/yhxy')
			if "cannot access /home/yhxy" in stderr.read():
				print("waiting for yhxy dir created...")
				time.sleep(1)
			else:
				break
		stdin, stdout, stderr = ssh.exec_command('/bin/bash /tmp/leicl/s02_new_host_init_script.sh')
		while not stdout.channel.exit_status_ready():
			time.sleep(1)
		#stdin, stdout, stderr = ssh.exec_command('/usr/bin/which wget')
		#print stderr.read()
		#if 'no get in' in stderr.read():
		#    print('wget not install,please check yum configuration!')
		#    t.close()
		#    ssh.close()
		#    continue
		#安装jdk1.8
		jdkUrl = "http://192.168.1.137/website/software/jdk-8u11-linux-x64.tar.gz"
		stdin, stdout, stderr = ssh.exec_command('mkdir /data/apps -v')
		stdin, stdout, stderr = ssh.exec_command(' cd /tmp && wget -q  %s -O /tmp/jdk.tar.gz'%jdkUrl)
		while not stdout.channel.exit_status_ready():
			time.sleep(1)
		stdin, stdout, stderr = ssh.exec_command('/usr/bin/tar xf /tmp/jdk.tar.gz -C /data/apps')
		while not stdout.channel.exit_status_ready():
			time.sleep(1)
			stdin, stdout, stderr = ssh.exec_command('/bin/cp /tmp/leicl/jdk.sh /etc/profile.d && source /etc/profile &> /dev/null ; java -version')	
		print stderr.read()
		#建立.ssh目录	
			stdin, stdout, stderr = ssh.exec_command('cd /home/%s/ && source /etc/profile && mkdir -v .ssh && chmod 700 .ssh && chown %s.%s .ssh'%(user,user,user))
			if stderr.read().strip() != '':
				stdin, stdout, stderr = ssh.exec_command('cd %s && cp authorized_keys authorized_keys.bak'%(key_path))
			stdin, stdout, stderr = ssh.exec_command('cd %s && cat /tmp/leicl/id_rsa.pub >> authorized_keys && chmod 600 authorized_keys && chown %s.%s authorized_keys' %(key_path,user,user))
		t.close()
			ssh.close()
		print('-------------------------------------')
		fd.close()
	
	def Keys(self):
		localFile = '/root/.ssh/id_rsa.pub'
		remoteFile = '/tmp/id_rsa.pub'
		sshPath = '/root/.ssh'
		for i in fd.readlines(): 
			if not i:
				continue
			tmp = i.strip('\n').split(',')
			host = tmp[0]
			passwd = tmp[1]
			print(host)
			print(passwd)
			if not passwd:
				continue
			try:
				t = paramiko.Transport((host,22))
				t.connect(username='root',password=passwd)
				sftp = paramiko.SFTPClient.from_transport(t)
				sftp.put(localFile,remoteFile)
				sftp.close()
				s = paramiko.SSHClient()
				s._transport = t
				stdin,stdout,stderr = s.exec_command('mkdir %s && chmod 700 %s ; cat %s >> %s/authorized_keys && chmod 600 %s/authorized_keys'%(sshPath,sshPath,remoteFile,sshPath,sshPath))
				print(stdout.read())
				print(stderr.read())
			except Exception as e:
				print(e)
				t.close()
				s.close()
				continue
			t.close()
			s.close()
	
	def run(self):
		self.ssh
		self.transfer_pubkey()
		self.initialization()







