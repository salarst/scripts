#!/bin/bash
#description:
#	create a user can only user specified command
source /etc/profile
cmd_list='ls cat tail less more bash ps top free ip ss netstat ifconfig grep df'
dst_bin_path="/home/${1}/bin"
dst_lib64_path="/home/${1}/lib64"

#create a lib directory on user home
for i in $dst_bin_path $dst_lib64_path;do
        if [ ! -d $i ];then
                while :;do
                mkdir $i
                if [ $? == 0 ];then
                        break
                fi
                done
        fi
done


#cp the cmd to /home/$1/bin
#cp cmd lib to /home/$1/lib64
cp /lib64/ld-linux-x86-64.so.2 $dst_lib64_path
for i in $cmd_list
do
        cmdpath=`which $i`
        cp $cmdpath $dst_bin_path
        libFile=`ldd  $cmdpath | sed -n '1!p' | awk -F'=>' '{print $2}' | awk '{print $1}'`
        for j in $libFile
        do
                cp $j $dst_lib64_path
        done
done




#create a admin.sh in /etc/profile.d and write follow content to it.

#get login user
username=`who am i| awk '{print $1}'` 

#if the user is yhxy, modify it env value PATH.
if [ "$username" = "yhxy" ];then
        PATH=/home/yhxy/bin
        export PATH
        LD_LIBRARY_PATH=/home/yhxy/lib64
        export LD_LIBRARY_PATH
fi