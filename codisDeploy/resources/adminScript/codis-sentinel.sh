#!/bin/bash

CODIS_ADMIN="${BASH_SOURCE-$0}"
CODIS_ADMIN="$(dirname "${CODIS_ADMIN}")"
CODIS_ADMIN_DIR="$(cd "${CODIS_ADMIN}"; pwd)"

CODIS_BIN_DIR=$CODIS_ADMIN_DIR/../sbin
CODIS_LOG_DIR=$CODIS_ADMIN_DIR/../logs
CODIS_CONF_DIR=$CODIS_ADMIN_DIR/../config

CODIS_SENTINEL_BIN=$CODIS_BIN_DIR/redis-sentinel
CODIS_SENTINEL_PID_FILE=$CODIS_LOG_DIR/sentinel.pid

CODIS_SENTINEL_LOG_FILE=$CODIS_LOG_DIR/sentinel.log
CODIS_SENTINEL_DAEMON_FILE=$CODIS_LOG_DIR/codis-sentinel.out

CODIS_SENTINEL_CONF_FILE=$CODIS_CONF_DIR/sentinel.conf

echo $CODIS_SENTINEL_CONF_FILE

if [ ! -d $CODIS_LOG_DIR ]; then
    mkdir -p $CODIS_LOG_DIR
fi


case $1 in
start)
    echo  "starting codis-sentinel ... "
    if [ -f "$CODIS_SENTINEL_PID_FILE" ]; then
      if kill -0 `cat "$CODIS_SENTINEL_PID_FILE"` > /dev/null 2>&1; then
         echo $command already running as process `cat "$CODIS_SENTINEL_PID_FILE"`.
         exit 0
      fi
    fi
    nohup "$CODIS_SENTINEL_BIN" "${CODIS_SENTINEL_CONF_FILE}" > "$CODIS_SENTINEL_DAEMON_FILE" 2>&1 < /dev/null &
    ;;
stop)
    echo "stopping codis-sentinel ... "
    if [ ! -f "$CODIS_SENTINEL_PID_FILE" ]
    then
      echo "no codis-sentinel to stop (could not find file $CODIS_SENTINEL_PID_FILE)"
    else
      kill -2 $(cat "$CODIS_SENTINEL_PID_FILE")
      echo STOPPED
    fi
    exit 0
    ;;
stop-forced)
    echo "stopping codis-sentinel ... "
    if [ ! -f "$CODIS_SENTINEL_PID_FILE" ]
    then
      echo "no codis-sentinel to stop (could not find file $CODIS_SENTINEL_PID_FILE)"
    else
      kill -9 $(cat "$CODIS_SENTINEL_PID_FILE")
      rm "$CODIS_SENTINEL_PID_FILE"
      echo STOPPED
    fi
    exit 0
    ;;
restart)
    shift
    "$0" stop
    sleep 1
    "$0" start
    ;;
*)
    echo "Usage: $0 {start|stop|stop-forced|restart}" >&2

esac