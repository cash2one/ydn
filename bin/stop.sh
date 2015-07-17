#!/bin/bash

function kill_process
{
    p_name=${1}
    pid_list=`ps -ef | grep ${p_name} | awk '{print $2}'`
    echo ${pid_list}
    for pid in ${pid_list}
    do
        kill ${pid}
    done
}

kill_process ad_server.py
kill_process limit_server.py
