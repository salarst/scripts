Description:

	this is a script to automate the deployment of a codis cluster. if each components of codis is 
	sucessfully deployed on each machine.it will be recored the component name in resources/install.txt.
	
	

Deployment:

	require:
	
		1.jdk for zookeeper
		2.python 2.7.x 
		3.the machine which scrips run on require ssh key login to deployment node.
		
	configFile:
		
		hosts: this file records deployment nodes's hostname and IP. it will written to hosts file of each deployment 
		node by scripts.
		roles: the role information is defined in this file,the scrips will deployes the corresponding components to 
		the corresponding 
				machine
		main.conf: this file is the main config file. this file records all configuration information for all components.
		
		see the file for details.

	adminStript:

		these scrips are the startup scrips for all components. all scrips are store in $codisDir/bin direcotry.
		
	resources:
		
		please download binary zookeeper packages and binary codis packages to resources direcotry. and modify the 
		packageName in main.conf.
		
	install:
		#dos2unix all scrips and files. cause the file is generate on windows server.
		
			python main.py 
		
		# if you want skip deployment of some components.you can write "COMPONET_NAME END" to install.txt,require "\n".
			the following are all the components name
			
				CODIS-FE
				CODIS-SEV
				CODID-DASHBOARD
				ZK
				CODIS-PROXY
				CODIS-SENTINEL
		
				
