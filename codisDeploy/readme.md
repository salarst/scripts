Description:
	main.py read the config file main.conf to deploy codis cluster


configFile:
	hosts: recording codis nodes's IP and hostname in this file. main.py will read it and write to /etc/hosts.
	roles: define codis roles in this file. read this file for detail
	main.conf: is dependence by main.py.  main.py read all confing and deploy codis to nodes. read this file for detail.

adminStript:
	for admin codis service. use these scripts to start/stop services.