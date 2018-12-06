#!/usr/bin/python
#coding:utf8
import argparse
from rabbitmqClusterInstall import install
import os
def main():
    flag = True
    conf = 'resources/main.conf'
    p = install(conf)
    parser = argparse.ArgumentParser(description='this script will automatic config a rabbitmq cluster!')
    parser.add_argument('-i','--init',action='store_False',default=False,dest='init',help='init mq nodes env')
    parser.add_argument('-m','--startMaster',action='store_False',default=False,dest='startMaster',help='start master node')
    parser.add_argument('-j','--joinCluster',action='store_False',default=False,dest='join',help='all nodes will join cluster except master node')
    parser.add_argument('-u','--addUser',action='store_False',default=False,dest='user',help='add a mq user base on config file')
    parser.add_argument('-p','--setPermission',action='store_False',default=False,dest='permission',help='set user permission base on config file')
    parser.add_argument('-v','--addVhost',action='store_False',default=False,dest='vhost',help='add a vhost base on config file')
    args = parser.parse_args()

    if args.init:
        try:
            os.remove('/tmp/pre_check')
        except:
            pass
        p.preEnv()
        flag = False
    if args.startMaster:
        p.startMaster()
        flag = False
    if args.join:
        p.joinCluster()
        flag = False
    if args.user:
        p.addUser()
        flag = False
    if args.vhost:
        p.addVhost()
        flag = False
    if args.permission:
        p.setPermission()
        flag = False
    if flag:
        parser.print_help()

if __name__ == '__main__':
    main()
