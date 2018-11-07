#!/usr/bin/python
import os
import sys
import init_agent
import init_server
import time


def deploy_ntp(hostFile,ntpServerIP):
	'''
		hostFile format:   ip,password
		require prepare files ntp.conf and ntpd on the current directory 
	'''
	fd = open(hostFile,'rb+')
	for i in fd.readlines():
		tmp = i.strip('\n').split(',')
		host = tmp[0]
		password = tmp[1]
		t = paramiko.Transport((host,22))
		try:
			pkey = paramiko.RSAKey.from_private_key_file('/root/.ssh/id_rsa')
			t.connect(username='root',pkey=pkey)
		except Exception as e:
			print('cat not login with key files. login with password!')
			t.connect(username='root',password=passowrd)
		ssh = paramiko.SSHClient()
		ssh._transport = t
		sftp = paramiko.SFTPClient.from_transport(t)
		sftp.put('ntpd','/etc/sysconfig/ntpd')
		sftp.put('ntp.conf','/etc/ntp.conf')
		sdtin,stdout,stderr = ssh.exec_command('yum -y install ntp ntpdate')
		while not stdout.channel.exit_status_ready():
			print('wait for ntp install finished')
			time.sleep(1)
		ssh.exec_command('systemctl stop ntp;systemctl enable ntp')
		stdin,stdout,stderr = ssh.exec_command('ntpdate %s;systemctl start ntp;'%ntpServerIP)
		while not stdout.channel.exit_status_ready()
			time.sleep(1)
		print('')
		stdin,stdout,stderr = ssh.exec_command('ntp -p')
		print(stdout.read())
		sftp.close()
		ssh.close()
	fd.close()
	
def Usage():
	print('''
		use "mian.py -a USERNAME:PASSWORD" to initial agent server
		use "main.py -f hostFile -s USERNAME:PASSWORD -l script.tar.gz" to initial target server
		use -h for help
	''')
def main():
	local_path = None
	hostFile = None
	username = None
	password = None
	ntpServerIP = None
	try:
		#-a username:password
        opts, args = getopt.getopt(argv, 'ha:s:l:f:')
    except getopt.GetoptError:
        usage()
        sys.exit(2)
	tmp = dict(opts)
	if tmp.has_key('-a') and len(opts) > 1:
		print('ERROR: -a can not use with other options')
		sys.exit(1)
    for opt, name in opts:
        if opt == '-a':
			tmp = name.split(':')
            if len(tmp)<2:
				print('Parameter error. Format: -a username:passowrd')
				sys.exit(1)
            username = tmp[0]
			password = tmp[1]
			p = init_agent.init_agent(username,passowrd)
			p.run()
		elif opt == '-s':
			tmp = name.split(':')
			if len(tmp)<2:
			print('Parameter error. Format: -a username:passowrd')
				sys.exit(1)
            username = tmp[0]
			password = tmp[1]
		elif opt == '-l':
			local_path = name
		elif opt == '-f':
			hostFile = name
		elif opt == '-n':
			ntpServerIP = name
		else:
			Usage()
		
	if local_path and username and password and hostFile:
		p = init_server.init_server(hostFile,local_path,username,passowrd)
		p.run()
	else:
		print('please give enough args to initial server')
	
	if hostFile and ntpServerIP:
		deploy_ntp(hostFile,ntpServerIP)
		print('deploy ntp sucessfully!')
	else:
		print('please give enough args to deploy ntp!')
		
	
	
                

if __name__ == '__main__':
        color = colors.colors()
        main(sys.argv[1:])
        if len(sys.argv) < 2 :
            usage()

