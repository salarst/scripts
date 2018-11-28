#!/usr/bin/python
#coding:utf8
import codisDeploy
import colors
import subprocess
import os

def main():
    filename = 'resources/install.txt'
    if not os.path.exists(filename):
        subprocess.Popen('touch %s'%filename,shell=True)
    with open(filename,'rb+') as fd:
        tmp = fd.readlines()
    if 'DONE\n' in tmp:
        p = subprocess.Popen('rm -rf %s'%filename,shell=True)
        p.wait()
    deploy = codisDeploy.deployCodis('resources/main.conf')
    with open(filename,'rb+') as fd:
        tmp = fd.readlines()
        if not ('INIT END\n' in tmp):
            deploy.baseInit()
        if not ('ZK END\n' in tmp):
            deploy.install_zk()
        if not ('CODIS-SEV END\n' in tmp):
            deploy.install_codis_server()
        if not ('CODIS-DASHBOARD END\n' in tmp):
            deploy.install_codis_dashboard()
        if not ('CODIS-PROXY END\n' in tmp):
            deploy.install_codis_proxy()
        if not ('CODIS-FE END\n' in tmp):
            deploy.install_codis_fe()
        if not ('CODIS-SENTINEL END\n' in tmp):
             deploy.install_codis_sentinel()

if __name__  == '__main__':
    color = colors.colors()
    main()
    with open('resources/install.txt', 'ab+') as fd:
        fd.write('DONE\n')

