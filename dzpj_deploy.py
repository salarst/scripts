#!/usr/bin/python
#coding:utf8
import os
import getopt
import sys
import subprocess
import paramiko
import json
import time
import colors
class djzx_deploy(object):
''' 
	require:
		1.local machine  can ssh all machine by key file
		2.local machine ssh itself can use key file
'''
    hostNum = None
    dbIP = None
    ngIP = None
    iplist = None
    def __init__(self,deploylist):
        self.deploylist=deploylist
        with open(self.deploylist,'rb+') as fd:
            self.iplist = json.load(fd)
        self.hostNum = len(self.iplist)
        if self.hostNum == 2:
            self.ngIP = False
            self.dbIP = self.iplist['DB']
            self.appIP = self.iplist['APP']
        else:
            self.dbIP = self.iplist['DB']
            self.appIP = self.iplist['APP']
            self.ngIP = self.iplist['NG']

    def wait_for_fininsh(self,stdout):
        while not stdout.channel.exit_status_ready():
            time.sleep(1)

    def ssh_handers(self,ip,port=22):
        pkey = paramiko.RSAKey.from_private_key_file('/root/.ssh/id_rsa')
        t = paramiko.Transport((ip, port))
        t.connect(username='root', pkey=pkey)
        ssh = paramiko.SSHClient()
        ssh._transport = t
        return ssh

    def env_pre(self):
        subprocess.Popen('hostnamectl set-hostname server2',shell=True)
        fd = open('/etc/hosts','a')

        fd.write('%s    server1 server1.dzpjzx.com\n%s  server2 server2.dzpjzx.com\n'%(self.dbIP,self.appIP))
        fd.close()
        for k,v in self.iplist.items():
            ssh = self.ssh_handers(v)
            ssh.exec_command('mkdir /data')
            #jdk version check
            count = 0
            while count<3:
                stdin,stdout,stderr = ssh.exec_command('java -version')
                print(color.color['blue']+'check env on %s'%(k)+ color.end)
                if stdout.channel.recv_exit_status != 0:
                    print(color.color['green'] + 'jdk check pass' + color.end)
                    break
                else:
                    stdin,stdout,stderr = ssh.exec_command('rpm -qa | grep -i jdk')
                    removeRPMS = stdout.read()
                    if removeRPMS:
                        for i in removeRPMS:
                            stdin, stdout, stderr = ssh.exec_command('rpm -e %s --nodeps'%i)
                count += 1
            if count == 3:
                print(color.color['red'] + 'please remove jdk by manual!' + color.end)
			#remove mariadb-libs on db_host
            if k == 'DB':
                stdin,stdout,stdout = ssh.exec_command('rpm -e mariadb-libs --nodeps')
                self.wait_for_fininsh(stdout)
                if stdout.channel.recv_exit_status == 0:
                    print(color.color['green'] + 'mysql env check pass!' + color.end)
                else:
                    print(color.color['red'] + 'can not remove mariadb-libs,please remove it manual!' + color.end)
                    sys.exit(1)
                #cp packages to db_host
                subprocess.Popen('scp data_prepare.tar.gz %s:/tmp'% (self.dbIP),shell=True)
                subprocess.Popen('scp server1.tar.gz %s:/tmp'%(self.dbIP),shell=True)
                subprocess.Popen('scp /etc/hosts %s:/etc' % (self.dbIP),shell=True)
                ssh.exec_command('cd /tmp; tar xf data_prepare.tar.gz;hostnamectl set-hostname server1')
                ssh.exec_command('mkdir /data/apps')
                stdin,stdout,stderr = ssh.exec_command('tar xf /tmp/server1.tar.gz -C /data/apps')
                self.wait_for_fininsh(stdout)
            #disabled firewalld & selinux
            ssh.exec_command('systemctl firewalld stop ; systemctl disable firewalld ')
            ssh.exec_command("setenfoce 0 && sed -i 's#SELINUX=enforcing#SELINUX=disabled#'")
            ssh.close()

    def install_app(self):
        if os.path.exists('/data'):
            p = subprocess.Popen('tar xf apps.tar.gz -C /data',shell=True)
            if p.wait() == 0:
                p = subprocess.Popen('cp /data/apps/jdk.sh /etc/profile.d',shell=True)
                print('------jdk version---------')
                p = subprocess.Popen('java -version',stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
                if p.wait() == 0:
                    print(p.stdout.read())
                else:
                    print(p.stderr.read())
                    print(color.color['red'] + 'jdk env home is not exists!!!' + color.end)

    def install_ng(self):
        # if ngIP is False,install ng on APP
        if self.ngIP:
            ssh = self.ssh_handers(self.ngIP)
            p = subprocess.Popen('cd /data/apps && tar zcf nginx.tar.gz nginx/*',shell=True)
            p.wait()
            p = subprocess.Popen('mv /data/apps/nginx.tar.gz /tmp',shell=True)
            p.wait()
            subprocess.Popen('scp /tmp/nginx.tar.gz %s:/tmp'%(self.ngIP),shell=True)
            stdin,stdout,stderr = ssh.exec_command('yum -y install zlib zlib-devel openssl openssl--devel pcre pcre-devel openssl openssl-devel')
            self.wait_for_fininsh(stdout)
            ssh.exec_command('mkdir /data/apps; cd /tmp && tar xf nginx.tar.gz -C /data/apps')
            stdin,stdout,stderr = ssh.exec_command('cd /data/apps/nginx/conf/vhost && grep server_name https-www.conf')
            oldIp = stdout.read().split()[1].split(';')[0]

            #modify nginx.conf
            stdin, stdout, stdin = ssh.exec_command("cd /data/apps/nginx/conf/vhost && sed -i 's#%s#%s#g' https-www.conf"%(oldIp,self.ngIP))
            stdin, stdout, stdin = ssh.exec_command("cd /data/apps/nginx/conf/vhost && sed -i 's#%s#%s#g' www.conf"%(oldIp, self.ngIP))
            ssh.close()
        else:
            p = subprocess.Popen('cd /data/apps/nginx/conf/vhost && grep server_name https-www.conf',stdout=subprocess.PIPE,shell=True)
            oldIp = p.stdout.read().split()[1].split()[0]
            subprocess.Popen("sed -i 's#%s#%s#g' https-www.conf"%(oldIp,self.appIP),shell=True)
            subprocess.Popen("sed -i 's#%s#%s#g' www.conf"%(oldIp,self.appIP),shell=True)
        print('nginx install finished')

    def jdk_check(self):
        stdin, stdout, stderr = ssh.exec_command('java -version')
        if stdout.channel.recv_exit_status == 0:
            return 1
        else:
            return 0

    def install_csvn(self):
        ssh = self.ssh_handers(self.dbIP)
        subprocess.Popen('scp /data/apps/jdk.sh %s:/etc/profile.d/'%(self.dbIP))
        ssh.exec_command('mkdir /data')
        ssh.exec_command('tar xf /tmp/server1.tar.gz -C /data/apps && cd /data/apps && ln -s /data/apps/jdk1.8.0_11 /data/apps/jdk')
        #check jdk
        ret = self.jdk_check()
        if ret:
            ssh.exec_command('useradd csvn')
            ssh.exec_command('echo "csvn ALL = (root) NOPASSWD:ALL" > /etc/sudoers.d/csvn')
            ssh.exec_command('chown -R csvn.csvn /data/apps/csvn && sudo -E /data/apps/csvn/bin/csvn install')
        else:
            print(color.color['red'] + 'csvn require jdk,please install jdk first!' + color.end)
        ssh.close()

    def install_mysql(self):
        datadir = '/data/apps/mysql'
        ssh = self.ssh_handers(self.dbIP)
        stdin, stdout, stdin = ssh.exec_command('yum -y install perl-Data-Dumper')
        self.wait_for_fininsh(stdout)
        stdin,stdout,stderr = ssh.exec_command('cd /tmp/prepare/mysql && yum -y localinstall MySQL-client.rpm MySQL-server.rpm')
        self.wait_for_fininsh(stdout)
        ssh.exec_command('mv %s /tmp;mkdir /data/apps/mysql && chown mysql.mysql %s'%(datadir,datadir))
        stdin,stdout,stderr = ssh.exec_command('mysql_install_db --datadir=%s --user=mysql --basedir=/usr && \
         /bin/cp -r /tmp/mysql/* %s && chown -R mysql.mysql %s'%(datadir,datadir,datadir))
        #setting config
        ssh.exec_command("sed -i 's/\# datadir = ...../ datadir = \/data\/apps\/mysql/g' /usr/my.cnf")
        ssh.exec_command("sed -i 's/\# port = ...../ port = 12345/g' /usr/my.cnf")
        ssh.exec_command("sed -i 's/\# basedir = ...../ basedir = \/usr/g' /usr/my.cnf")
        stdin,stdout,stderr = ssh.exec_command('systemctl start mysql')
        if stdout.channel.recv_exit_status() == 0:
                print('start mysql sucessfully!')
        else:
                print(color.color['red'] + stderr.read() + color.end)
        ssh.close()
        print('mysql install finished')

    def install_redis(self):
        r_dir = '/data/apps/redis'
        ssh = self.ssh_handers(self.dbIP)
        ssh.exec_command('useradd redis')
        ssh.exec_command('chown -R redis.redis %s'%r_dir)
        stdin,stdout,stderr = ssh.exec_command('yum -y install glibc make')
        self.wait_for_fininsh(stdout)
        #start redis as redis
        stdin,stdout,stderr = ssh.exec_command('su -g redis -c "/data/apps/redis/bin/redis-server /data/apps/redis/conf/redis.conf" ')
        self.wait_for_fininsh(stdout)
        stdin,stdout,stderr = ssh.exec_command('netstat -tlnp | grep 12345')
        if stdout.channel.recv_exit_status() == 0:
            print('redis start sucessfully!')
        else:
            print(color.color['red'] + 'redis start failure!' + color.end)
        ssh.close()

    def install_mq(self):
        ssh = self.ssh_handers(self.dbIP)
        stdin,stdout,stderr = ssh.exec_command('yum -y localinstall /tmp/prepare/rabbitmq/*')
        self.wait_for_fininsh(stdout)
        print('start mq')
        if stdout.channel.recv_exit_status == 0:
            stdin,stdout,stderr = ssh.exec_command('rabbitmq-server -detached')
        else:
            print(color.color['red'] + 'rabbitmq start failed!' + color.end)
            sys.exit(1)
        time.sleep(5)
        stdin,stdout,stderr = ssh.exec_command("rabbitmqctl add_user USERNAME PASSWORD && rabbitmqctl set_user_tags USERNAME administrator && rabbitmqctl set_permissions -p / USERNAME '.*' '.*' '.*'")
        #verify mq status
        stdin,stdout,stderr = ssh.exec_command('rabbitmqctl list_users')
        print(stdout.read())


def usage():
    print('%s -i [csvn|redis|mysql|mq] or %s -h to see help!' % (sys.argv[0], sys.argv[0]))


def main(argv):
    '''hostFile.txt Format:
    {
        "DB":$IP,
        "APP":$IP,
        "NG":$IP
    }
    if only two hosts,NG will deploy on APP.
    '''
    hostFile = 'hostFile.txt'
    d = djzx_deploy(hostFile)
    if not os.path.exists('/tmp/check_prepare'):
        d.env_pre()
        os.system('touch /tmp/check_prepare')
    try:
        opts, args = getopt.getopt(argv, 'hi:')
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    for opt, name in opts:
        if opt == '-i':
            if name == 'redis':
                d.install_redis()
            elif name == 'csvn':
                d.install_csvn()
            elif name == 'mysql':
                d.install_mysql()
            elif name == 'mq':
                d.install_mq()
            elif name == 'nginx':
                d.install_ng()
            elif name == 'app':
                d.install_app()
            elif name == 'all':
                d.install_app()
                d.install_ng()
                d.install_mq()
                d.install_mysql()
                d.install_csvn()
                d.install_redis()
            else:
                usage()

if __name__ == '__main__':
        color = colors.colors()
        main(sys.argv[1:])
        if len(sys.argv) < 2 :
            usage()
