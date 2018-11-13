#!/bin/bash
#require ssh login with key file

for i in `cat hostFile | awk -F',' '{print $1}'`;do
	ret=`ssh $i 'test -e /data && echo 1 || echo 0'`
	if [ $ret == 0 ];then
		echo "$i dose not have directory -- '/data' "
		continue
	fi
	scp zabbix_agent.tar.gz $i:/tmp
	ssh $i 'pkill zabbix'
	ssh $i 'rm -rf /data/apps/zabbix'
	ssh $i 'cd /tmp; mkdir /data/apps ; tar xf zabbix_agent.tar.gz -C /data/apps ;sleep 2; /data/apps/zabbix/autoconfig.py'
	echo -e "\033[31m$i -- check 10050 \033[0m"
	while : ;do
		res=`ssh $i 'netstat -tlnp | grep 10050'`
		if [ ! -z "$res" ];then
			break
		fi
		ssh $i ' /data/apps/zabbix/autoconfig.py'	
	done
	ssh $i 'netstat -tlnp | grep 10050'
done
