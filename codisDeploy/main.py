#!/usr/bin/python
#coding:utf8
import codis_deploy
import colors

def main():
    deploy = codis_deploy.deployCodis('resources/main.conf')
    with open('resources/install.txt','rb+') as fd:
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