#!/usr/bin/python
# coding:utf8
#v1.1
import os
import sys
import yaml
import paramiko
import subprocess
import time
import colors


class deployCodis():
    zkDirName = None
    codisDirName = None

    # codisDirName = '/data/apps/codis3.2.1-go1.8.3-linux'

    def __init__(self, configFile):
        fd = open(configFile)
        self.config = yaml.load(fd)
        fd.close()
        self.zkConfig = self.config['zkConfig']
        self.resourcePath = self.config['Packages']['path']
        self.codisPassword = self.config['codisConfig']['password']
        codisRolesFile = self.config['Dependencies']['roleFile']
        with open(codisRolesFile, 'r') as fd:
            self.codisRoles = yaml.load(fd)
        self.zkNodes = self.codisRoles['zk']
        zkPort = self.config['zkConfig']['port']
        m = ''
        for i in self.zkNodes:
            m += i + ':' + str(zkPort) + ','
        self.zkAddress = m.strip(',').strip()
        try:
            os.mknod('%s/install.txt' % self.resourcePath)
        except Exception as e:
            var = raw_input()

    def ssh_handler(self, hostname, port=22):
        pkey = paramiko.RSAKey.from_private_key_file('/root/.ssh/id_rsa')
        t = paramiko.Transport((hostname, port))
        try:
            t.connect(username='root', pkey=pkey)
        except Exception as e:
            print('ssh login error: %s' % e)
            sys.exit(1)
        ssh = paramiko.SSHClient()
        ssh._transport = t
        return ssh

    def baseInit(self):
        subprocess.Popen('cat %s/hosts >> /etc/hosts' % self.resourcePath, shell=True)
        for i in self.zkNodes:
            print(i)
            ssh = self.ssh_handler(i)
            for j in self.config['DeployPath'].values():
                ssh.exec_command('mkdir -pv %s' % j)
            ssh.close()
        for i in self.zkNodes:
            ssh = self.ssh_handler(i)
            p = subprocess.Popen('scp %s %s:/tmp'%(self.config['Dependencies']['dnsFile'],i),shell=True)
            p.wait()
            ssh.exec_command('cat /tmp/hosts >> /etc/hosts')
            ssh.close()
        with open('%s/install.txt' % self.resourcePath, 'a') as fd:
            fd.write('INIT END\n')

    def wait_for_finish(self,stdout):
        while not stdout.channel.exit_status_ready():
            time.sleep(1)

    def decorator_isRecord(self,func):
        def check(record,count):
            if count == 0:
                return func(record,count)
        return check


    @decorator_isRecord
    def recordOperations(self, record,count):
        with open('%s/install.txt' % self.resourcePath, 'ab+') as fd:
            fd.write('%s END\n' % record)

    def checkServiceStatus(self, host, cmd, serviceName):
        color = colors.colors()
        ssh = self.ssh_handler(host)
        stdin, stdout, stderr = ssh.exec_command('%s' %cmd)
        self.wait_for_finish(stdout)
        print('check %s status on %s' % (serviceName, host))
        if stdout.channel.recv_exit_status() == 0:
            print('%s%s start sucess!%s' % (color.color['green'], serviceName, color.end))
            print(stdout.read())
            ssh.close()
            return 0
        else:
            print('%s%s start failed!%s' % (color.color['red'], serviceName, color.end))
            ssh.close()
            return 1

    def install_zk(self):
        zookeeperPackageName = self.config['Packages']['zookeeperPackageName']
        zookeeperPath = self.config['DeployPath']['zookeeperPath']

        for i in self.zkNodes:
            ssh = self.ssh_handler(i)
            subprocess.Popen(
                'scp -o StrictHostKeyChecking=no %s/%s  %s:/tmp' % (self.resourcePath, zookeeperPackageName, i),
                shell=True)
            stdin,stdout,stderr = ssh.exec_command('tar xf /tmp/%s -C %s' % (zookeeperPackageName, zookeeperPath))
            self.wait_for_finish(stdout)
            if not self.zkDirName:
                stdin, stdout, stderr = ssh.exec_command('cd /data/apps/zookeeper*;pwd')
                self.zkDirName = stdout.read().strip('\n')
            ssh.exec_command('mkdir %s/{logs,data}' % self.zkDirName)
            ssh.exec_command("cd %s/conf;cp zoo_sample.cfg zoo.cfg; sed -i 's#/tmp/zookeeper#%s/data#g' zoo.cfg" % (
            self.zkDirName, self.zkDirName))
            ssh.exec_command(
                "cd %s/conf;sed -i 's#/tmp/2181#%s#g' zoo.cfg" % (self.zkDirName, self.config['zkConfig']['port']))
            ssh.exec_command('echo -e "logDir=%s/logs\ninitLimit=10\nsyncLimit=2" >> %s/conf/zoo.cfg' % (
            self.zkDirName, self.zkDirName))
            for k, v in self.config['zkConfig']['cluster'].items():
                ssh.exec_command('echo %s=%s >> %s/conf/zoo.cfg' % (k, v, self.zkDirName))
            ssh.exec_command('echo %s > %s/data/myid' % (self.zkConfig['myid'][i], self.zkDirName))
            stdin, stdout, stderr = ssh.exec_command('cd %s/bin;./zkServer.sh start' % (self.zkDirName))
            self.wait_for_finish(stdout)
            ssh.close()
        count = 0
        for i in self.zkNodes:
            cmd = '%s/bin/zkServer.sh status' % self.zkDirName
            status = self.checkServiceStatus(i, cmd, 'zk')
            count += status
        self.recordOperations('ZK',count)


    def install_codis_server(self):
        codisPackageName = self.config['Packages']['codisPackageName']
        codisPath = self.config['DeployPath']['codisPath']
        sampleFile = self.config['codisConfig']['codis-server']['configFile']
        adminScript = self.config['codisConfig']['codis-server']['adminScript']
        count = 0
        for i in self.codisRoles['codis-server']:
            ssh = self.ssh_handler(i)
            p = subprocess.Popen('scp -o StrictHostKeyChecking=no %s/%s  %s:/tmp' % (self.resourcePath, codisPackageName, i),shell=True)
            p.wait()
            stdin, stdout, stderr = ssh.exec_command('tar xf /tmp/%s -C %s' % (codisPackageName, codisPath))
            self.wait_for_finish(stdout)
            if not self.codisDirName:
                stdin, stdout, stderr = ssh.exec_command('cd /data/apps/codis*;pwd')
                self.codisDirName = stdout.read().strip('\n')
            ssh.exec_command('mkdir %s/{logs,config,data,sbin,bin}' % self.codisDirName)
            stdin,stdout,stderr = ssh.exec_command('cd %s;mv codis-* sbin;mv redis-* sbin' % (self.codisDirName))
            print(stderr.read())
            print (stdout.read())
            # set reids config
            for j in self.config['codisConfig']['codis-server']['port']:
                redisConfig = '%s/config/redis-%s.conf' % (self.codisDirName, j)
                instanceAdminScript = '%s/bin/codis-server-%s.sh' % (self.codisDirName, j)
                p = subprocess.Popen('scp %s/%s %s:%s' % (self.resourcePath, sampleFile, i, redisConfig), shell=True)
                p.wait()
                p = subprocess.Popen('scp %s %s:%s' % (adminScript, i, instanceAdminScript), shell=True)
                p.wait()
                # script setting
                ssh.exec_command("sed -i 's#PORT#%s#g' %s" % (j, instanceAdminScript))
                # config setting
                # set ip && port
                ssh.exec_command("sed -i -e 's#CODIS_ADDRESS#%s#g'\
				-e 's#CODIS_PORT#%s#g' \
				-e 's#CODIS_PID#%s\/logs\/redis-%s.pid#g' %s" \
                                 % (i, j, self.codisDirName, j, redisConfig))
                time.sleep(0.1)
                # set logfile
                ssh.exec_command("sed -i -e 's#CODIS_LOG#%s\/logs\/redis-%s.log#g' \
				-e 's#CODIS_RDB#redis-%s.rdb#g' \
				-e 's#CODIS_PASSWORD#%s#g' %s" \
                                 % (self.codisDirName, j, j, self.codisPassword, redisConfig))
                time.sleep(0.1)
                # start codis-server
                stdin, stdout, stderr = ssh.exec_command('%s start' % (instanceAdminScript))
                while not stdout.channel.exit_status_ready():
                    time.sleep(1)
                print('check codis-server status on %s' % i)

                cmd = 'netstat -tlnp | grep %s' % j
                serviceName = 'codis-server %s' % j
                staus = self.checkServiceStatus(i, cmd, serviceName)
                count += status
            ssh.close()
        self.recordOperations('CODIS-SEV',count)


    def install_codis_dashboard(self):
        dashboradHost = self.codisRoles['codis-dashboard']
        sampleFile = self.config['codisConfig']['codis-dashboard']['configFile']
        dashboradConf = '%s/config/dashboard.conf' % self.codisDirName
        adminScript = self.config['codisConfig']['codis-dashboard']['adminScript']
        count = 0
        for i in dashboradHost:
            ssh = self.ssh_handler(i)
            p = subprocess.Popen('scp %s/%s %s:%s/config' % (self.resourcePath, sampleFile, i, self.codisDirName),
                                 shell=True)
            p.wait()
            p = subprocess.Popen('scp %s %s:%s/bin' % (adminScript, i, self.codisDirName), shell=True)
            p.wait()
            ssh.exec_command("sed -i -e 's#ZK_ADDRESS#%s#g' \
	    		-e 's#CODIS_NAME#%s#g' %s" \
                             % (self.zkAddress, self.config['codisConfig']['productName'], dashboradConf))
            time.sleep(0.1)
            ssh.exec_command("sed -i -e 's#CODIS_PASSWORD#%s#g' \
	    		-e 's#CODIS_DASHBOARD_PORT#%s#g' %s" \
                             % (
                             self.config['codisConfig']['password'], self.config['codisConfig']['codis-dashboard']['port'],
                             dashboradConf))
            time.sleep(0.1)

            print('start codis dashboard on %s' % i)
            stdin, stdout, stderr = ssh.exec_command('%s/bin/codis-dashboard.sh start' % self.codisDirName)
            while not stdout.channel.exit_status_ready():
                time.sleep(1)
            cmd = 'netstat -tlnp | grep %s' % self.config['codisConfig']['codis-dashboard']['port']
            status = self.checkServiceStatus(i, cmd, 'codis-dashboard')
            count += status
            ssh.close()
        self.recordOperations('CODIS-DASHBOARD',count)


    def install_codis_fe(self):
        adminScript = self.config['codisConfig']['codis-fe']['adminScript']
        feHost = self.codisRoles['codis-fe']
        count = 0
        for i in feHost:
            ssh = self.ssh_handler(i)
            p = subprocess.Popen('scp %s %s:%s/bin' % (adminScript, i, self.codisDirName), shell=True)
            p.wait()
            ssh.exec_command("sed -i -e 's#ZK_ADDRESS#%s#g' \
	    		-e 's#FE_ADDRESS:FE_PORT#%s:%s#g' \
	    		%s/bin/codis-fe.sh" % (
            self.zkAddress, feHost, self.config['codisConfig']['codis-fe']['port'], self.codisDirName))
            time.sleep(0.1)
            print('start codis fe on %s' % i)
            stdin, stdout, stderr = ssh.exec_command('%s/bin/codis-fe.sh start' % self.codisDirName)
            while not stdout.channel.exit_status_ready():
                time.sleep(1)
            cmd = 'netstat -tlnp | grep %s' % self.config['codisConfig']['codis-fe']['port']
            status = self.checkServiceStatus(i, cmd, 'codis-fe')
            count += status
            ssh.close()
        self.recordOperations('CODIS-FE',count)


    def install_codis_proxy(self):
        proxyHost = self.codisRoles['codis-proxy']
        sampleFile = self.config['codisConfig']['codis-proxy']['configFile']
        proxyConf = '%s/config/proxy.conf' % self.codisDirName
        adminScript = self.config['codisConfig']['codis-proxy']['adminScript']
        count = 0
        for i in proxyHost:
            ssh = self.ssh_handler(i)
            p = subprocess.Popen('scp %s/%s %s:%s/config' % (self.resourcePath, sampleFile, i, self.codisDirName),
                                 shell=True)
            p.wait()
            p = subprocess.Popen('scp %s %s:%s/bin' % (adminScript, i, self.codisDirName), shell=True)
            p.wait()
            ssh.exec_command("sed -i -e 's#ZK_ADDRESS#%s#g' -e 's#CODIS_NAME#%s#g' %s" % (
            self.zkAddress, self.config['codisConfig']['productName'], proxyConf))
            time.sleep(0.1)
            ssh.exec_command(
                "sed -i -e 's#CODIS_PASSWORD#%s#g' -e 's#CODIS_PROXY_PORT#%s#g' -e 's#CODIS_PROXY_ADDRESS#%s#g' %s" % (
                self.config['codisConfig']['password'], self.config['codisConfig']['codis-proxy']['port'], i, proxyConf))
            time.sleep(0.1)

            print('start codis proxy on %s' % i)
            stdin, stdout, stderr = ssh.exec_command('%s/bin/codis-proxy.sh start' % self.codisDirName)
            while not stdout.channel.exit_status_ready():
                time.sleep(1)
            cmd = 'netstat -tlnp | grep %s' % self.config['codisConfig']['codis-proxy']['port']
            status = self.checkServiceStatus(i, cmd, 'codis-proxy')
            count += status
            ssh.close()
        self.recordOperations('CODIS-PROXY',status)


    def install_codis_sentinel(self):
        sentinelHost = self.codisRoles['codis-sentinel']
        sampleFile = self.config['codisConfig']['codis-sentinel']['configFile']
        sentinelConf = '%s/config/sentinel.conf' % self.codisDirName
        adminScript = self.config['codisConfig']['codis-sentinel']['adminScript']
        count = 0
        for i in sentinelHost:
            ssh = self.ssh_handler(i)
            p = subprocess.Popen('scp %s/%s %s:%s/config' % (self.resourcePath, sampleFile, i, self.codisDirName),
                                 shell=True)
            p.wait()
            p = subprocess.Popen('scp %s %s:%s/bin' % (adminScript, i, self.codisDirName), shell=True)
            p.wait()
            ssh.exec_command("sed -i 's#CODIS_SENTINEL_ADDRESS#%s#g' %s" % (i, sentinelConf))
            time.sleep(0.1)
            ssh.exec_command("sed -i 's#CODIS_SENTINEL_PORT#%s#g' %s" % (
            self.config['codisConfig']['codis-sentinel']['port'], sentinelConf))
            time.sleep(0.1)
            ssh.exec_command("sed -i 's#CODIS_DIR#%s#g' %s" % (self.codisDirName, sentinelConf))
            time.sleep(0.1)
            print('start codis sentinel on %s' % i)
            stdin, stdout, stderr = ssh.exec_command('%s/bin/codis-sentinel.sh start' % (self.codisDirName))
            while not stdout.channel.exit_status_ready():
                time.sleep(1)
            cmd = 'netstat -tlnp | grep %s' % self.config['codisConfig']['codis-sentinel']['port']
            status = self.checkServiceStatus(i, cmd, 'codis-sentinel')
            count += status
            ssh.close()
        self.recordOperations('CODIS-SENTINEL',count)


    def test(self):
        print('test...OK!')


if __name__ == '__main__':
    deployCodis('resources/main.conf').test()



