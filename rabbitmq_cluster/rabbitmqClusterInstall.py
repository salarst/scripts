#!/usr/bin/python
#coding:utf8
from worker import worker
from colors import colors
import yaml
import os
import sys
import glob
import subprocess

class install():
    def __init__(self,conf):
        with open(conf,'r') as fd:
            config = yaml.load(fd)
        self.deps = config['Dependences']
        self.config = config['Config']
        self.dataDir = self.config['dataDir']
        self.webMntPlg = self.config['enable_web_management']
        self.user = self.config['user']
        self.userTag = self.config['tag']
        self.vhost = self.config['vhost']
        self.vhost_enable = self.vhost['enable']
        self.vhost_path = self.vhost['path']
        self.userPermission = self.config['permission']
        self.worker = worker()
        self.color = colors()
        self.clusterNodes = self.config['clusterNodes']
        self.master = self.clusterNodes['mq01']
    def preEnv(self):
        '''
        convert all files in resources dir into linux format by command dos2unix
        add ip host to /etc/hosts
        '''

        checkFlag = os.access('/tmp/pre_check',os.F_OK)
        resourcesDir = self.deps['dir']
        hostFile =  resourcesDir + '/' + self.deps['hostsFile']
        if not checkFlag:
            #convert
            cmd = glob.glob('%s/*'%resourcesDir)
            cmd.insert(0,'dos2unix')
            res = self.worker.do_work_local(cmd,returncode=True,returnStderr=True)
            if res['returncode'] != 0:
                print(res['stderr'])
                sys.exit(1)
            #stop mq
            for k,v in self.clusterNodes.items():

                ssh = self.worker.ssh_handers(v)
                cmd = 'rabbitmqctl stop'
                res = self.worker.do_work_remote(ssh, cmd, returnExitStatus=True,returnStderr=True)
                if res['exitStatus'] == 0:
                    print('%s stop rabbitmq sucessfully! %s' % (self.color.color['green'], self.color.end))
                    ssh.close()
                else:
                    print('%s %s %s' % (self.color.color['red'], res['stderr'], self.color.end))
                    print('please manully stop mq on %s first'%v)
                    ssh.close()
                    sys.exit(1)
            #add ip host to /etc/hosts
            for k,v in self.clusterNodes.items():
                ssh = self.worker.ssh_handers(v)
                self.worker.do_work_local(['scp',hostFile,'%s:/tmp'%v])
                cmd = 'cat /tmp/hosts.txt >> /etc/hosts'
                self.worker.do_work_remote(ssh,cmd)
                cmd = 'hostnamectl set-hostname %s'%k
                self.worker.do_work_remote(ssh,cmd)

                #create datadir and setting mq config
                cmd = 'mkdir -pv %s/{mnesia,logs}' % self.dataDir
                self.worker.do_work_remote(ssh, cmd)
                cmd = 'chown -R rabbitmq.rabbitmq %s' % self.dataDir
                self.worker.do_work_remote(ssh, cmd)
                cmd = "echo -e 'RABBITMQ_MNESIA_BASE=/data/apps/rabbitmq/mnesia\nRABBITMQ_LOG_BASE=/data/apps/rabbitmq/logs' > /etc/rabbitmq/rabbitmq-env.conf"
                self.worker.do_work_remote(ssh, cmd)
                ssh.close()
        os.mknod('/tmp/pre_check')

    def startMaster(self):
        '''start master and copy .erlang.cookie to local dir /tmp'''

        cmd = 'rabbitmq-server -detached'
        ssh = self.worker.ssh_handers(self.master)
        self.worker.do_work_remote(ssh, cmd)
        cmd = 'rabbitmqctl status'
        self.worker.check_service_status(ssh,cmd,'masterMQ')
        res = self.worker.do_work_remote(ssh, cmd, returnExitStatus=True, returnStderr=True)
        cookieDir = '/var/lib/rabbitmq'
        ssh.close()
        if res['exitStatus'] == 0:
            self.worker.do_work_local(['scp','%s:%s/.erlang.cookie'%(self.master,cookieDir),'/tmp'])
        else:
            print('%s %s %s' % (self.color.color['red'], res['stderr'], self.color.end))
            sys.exit(1)

    def joinCluster(self):
        '''
        join cluster and copy .erlang.cookie to slave nodes
        '''
        ssh = self.worker.do_work_remote(self.master)
        res = self.worker.check_service_status(ssh,'rabbitmqctl status','masterMQ')
        ssh.close()
        if not res:
            sys.exit(1)
            
        cookieDir = '/var/lib/rabbitmq'
        nodes = self.clusterNodes.copy()
        del nodes['mq01']
        for k,v in nodes.items():
            ssh = self.worker.ssh_handers(v)
            #self.worker.do_work_local('scp /tmp/.erlang.cookie %s:%s'%(v,cookieDir))
            self.worker.do_work_local(['scp','/tmp/.erlang.cookie','%s:%s'%(v,cookieDir)])
            self.worker.do_work_remote(ssh,'chown rabbitmq.rabbitmq %s/.erlang.cookie'%cookieDir)
            cmd = 'rabbitmq-server -detached'
            res = self.worker.do_work_remote(ssh,cmd,returnExitStatus=True,returnStderr=True)
            if res['exitStatus'] == 0:
                cmd = 'rabbitmqctl stop_app && rabbitmqctl join_cluster rabbit@mq01 && rabbitmqctl start_app'
                self.worker.do_work_remote(ssh,cmd)
                cmd = 'rabbitmqctl cluster_status'
                self.worker.check_service_status(ssh,cmd,'rabbitmq')
            else:
                print('%s %s %s'%(self.color.color['red'],res['stderr'],self.color.end))
                print('%s join cluster failed on %s %s'%(self.color.color['red'],v,self.color.end))
            ssh.close()

    def addUser(self):
        pass

    def addVhost(self):
        pass

    def setPermission(self):
        pass






