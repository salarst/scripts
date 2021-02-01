import subprocess
import time
import colors
import paramiko
import sys
import glob


class worker():
    color = colors.colors()
    def __init_(self):
        pass

    def ssh_handers(self, ip, port=22, keyLogin=True, passowrd=None):
        '''
        ssh login to linux server with key or password.
        if keyLogin is True,use ssh key login,else use password.
        if password is none,will raise an exception
        '''
        if keyLogin:
            try:
                pkey = paramiko.RSAKey.from_private_key_file('/root/.ssh/id_rsa')
            except Exception as e:
                print(self.color.color['red'] + e + self.color.end)
                sys.exit(1)
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            if not passowrd:
                ssh.connect(hostname=ip, port=port, username='root', pkey=pkey)
            else:
                ssh.connect(hostname=ip, port=port, username='root', passowrd=passowrd)
        except paramiko.SSHException as e:
            print(self.color.color['red'] + 'please check hostFile.txt to confirm the config is correct!' + self.color.end)
            print(self.color.color['red'] + 'the error IP is %s,ssh exception:%s' % (ip, e) + self.color.end)
            ssh.close()
            sys.exit(1)
        return ssh

    def wait_for_finish(self, stdout):
        '''
        wait for paramiko.SSHClient excute command finish
        '''
        while not stdout.channel.exit_status_ready():
            time.sleep(0.5)

    def do_work_local(self, cmdList, returncode=False, returnStdout=False, returnStderr=False):
        '''
        execute linux commands with subprocess module and if return* is Ture
        return the reqiurement values.
        '''
        res = {}
        pipe = subprocess.PIPE
        p = subprocess.Popen(cmdList, stdout=pipe, stderr=pipe)

        p.wait()
        if returncode:
            res['returncode'] = p.returncode
        if returnStdout:
            res['stdout'] = p.stdout
        if returnStderr:
            res['stderr'] = p.stderr.read()
        return res

    def do_work_remote(self, ssh, cmd, returnStdout=False, returnExitStatus=False, returnStderr=False):
        '''
        use paramiko to excute command on remote server and return the results of excution.
        '''
        res = {}
        stdin, stdout, stderr = ssh.exec_command(cmd)
        self.wait_for_finish(stdout)
        if returnStdout:
            res['stdout'] = stdout.read()
        if returnExitStatus:
            res['exitStatus'] = stdout.channel.recv_exit_status()
        if returnStderr:
            res['stderr'] = stderr.read()
        return res

    def check_service_status(self, ssh, cmd, serviceName):
        '''
        check service status.you can use commands like 'netstat -tlnp | grep $port'
        or 'systemctl status $service' to check the service status
        '''
        stdin, stdout, stderr = ssh.exec_command('%s' % cmd)
        if stdout.channel.recv_exit_status() == 0:
            print('%s %s is running! %s'%(self.color.color['green'],serviceName,self.color.end) )
            return True
        else:
            print('%s %s is down %s'%(self.color.color['red'],serviceName,self.color.end))
            return False


